from pe_automator.actions.gitlab import fetch_runs
from pe_automator.types.ssh import MultiSSHManager
from pe_automator.actions.allocation import get_allocation_info
from pe_automator.actions.status_updater import parse_progress
from pe_automator.actions.job_status import get_data_analysis_log
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os


def dlogz_plot(private_token, ssh_key, data_path="./data", save_file=None):
    with open(os.path.join(data_path, 'project', 'project.json'), 'r') as f:
        project_config = json.load(f)
    print(f"Loaded project configuration: {project_config}")
    gitlab_url, gitlab_project = project_config['gitlab_url'], project_config['gitlab_project']

    runs = fetch_runs(gitlab_url=gitlab_url, gitlab_project=gitlab_project, private_token=private_token)
    ongoing_runs = runs['ongoing']


    fig, axes = plt.subplots(nrows=len(ongoing_runs), ncols=1, figsize=(10, 3 * len(ongoing_runs)))
    if len(ongoing_runs) == 1:
        axes = [axes]  # Make it iterable

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plt.suptitle(f'dlogz Progress Check at {now}', fontsize=16)
    
    with MultiSSHManager() as manager:
        for i, run in enumerate(ongoing_runs):
            print(f"Checking run: {run['title']}")
            axes[i].set_title(f'Issue {run["issue"].iid}, Run: {run["title"]}, by {run["issue"].author["name"]}')

            allocation = get_allocation_info(run['allocation'], data_path)
            user = allocation['maintainer']

            manager.add_client(
                name=run['allocation'],
                hostname=allocation['hostname'],
                key_filename=ssh_key,
                username=user,
                skip_if_exists=True
            )
            ssh_client = manager.get_client(run['allocation'])
            files = get_data_analysis_log(run, ssh_client)

            try:
                analysis_out_file = [f for f in files if f['job_type'] == 'analysis' and f['type'] == 'out'][0]
            except IndexError:
                print(f"No analysis output file found for run: {run['title']}")
                axes[i].text(0.5, 0.5, 'No analysis output file found', horizontalalignment='center', verticalalignment='center', transform=axes[i].transAxes)
                continue

            if not analysis_out_file:
                print("No analysis output file found.")
                axes[i].text(0.5, 0.5, 'No analysis output file found', horizontalalignment='center', verticalalignment='center', transform=axes[i].transAxes)
                continue
            # test if file contains 50 lines
            result, err = ssh_client.execute(f"wc -l < {analysis_out_file['filename']}")
            try:
                num_lines = int(result.strip())
                if num_lines < 50:
                    print(f"Analysis output file {analysis_out_file['filename']} has less than 50 lines: {num_lines} lines.")
            except ValueError:
                print(f"Could not parse the number of lines from the output: {result.strip()}")
                axes[i].text(0.5, 0.5, 'Could not parse number of lines', horizontalalignment='center', verticalalignment='center', transform=axes[i].transAxes)
                continue

            result, err = ssh_client.execute(f"tail -n 100 {analysis_out_file['filename']}")

            progress = parse_progress(result)

            if progress:
                axes[i].plot([p['time']/3600 for p in progress], [p['dlogz'] for p in progress], marker='o', label='dlogz')
                print(f"Issue: {run['issue'].iid}, Run: {run['title']}")
                axes[i].set_xlabel('Time (hours)')
                axes[i].set_ylabel('Progress')
                axes[i].legend()
            else:
                continue

        plt.tight_layout()

        if save_file:
            plt.savefig(save_file)
        else:
            plt.show()
