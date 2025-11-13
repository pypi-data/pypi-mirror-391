import gitlab
import re
import json
import os
from pe_automator.actions.gitlab import get_information_from_issue
from pe_automator.actions.allocation import get_allocation_info, get_env_path
from pe_automator.types.ssh import SimpleSSHClient
from pe_automator.actions.remote import run_command


def rescue_run(issue_number, data_path, private_token, walltime=""):
    """
    Restart a run by re-creating the environment and re-submitting the job.
    """
    print(f"Restarting run for issue number {issue_number}...")
    with open(os.path.join(data_path, 'project', 'project.json'), 'r') as f:
        project_config = json.load(f)
    print(f"Loaded project configuration: {project_config}")
    gitlab_url, gitlab_project = project_config['gitlab_url'], project_config['gitlab_project']

    gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
    project = gl.projects.get(gitlab_project)
    issue = project.issues.get(issue_number)

    run_info = get_information_from_issue(issue)
    print(f"Run information: {run_info}")


    allocation = run_info['allocation']
    conda_env = run_info['conda_env']
    allocation_info = get_allocation_info(allocation, data_path=data_path)
    conda_activate_command = f"{get_env_path(allocation_info)}/{conda_env}/bin/activate"

    user = run_info['user']
    hostname = run_info['remote'].split('@')[1]
    allocation = run_info['allocation']
    allocation_info = get_allocation_info(allocation, data_path=data_path)
    match = re.match(r'^(.*?)/runs/', run_info['run_dir'])
    if match:
        event_path = match.group(1)
        run_path = run_info['run_dir'][len(event_path) + 1:]
        print(f"Event path: {event_path}, Run path: {run_path}")
    else:
        raise ValueError("Run directory does not match expected format.")

    with SimpleSSHClient(name=allocation, hostname=hostname, username=user) as ssh_client:
        submit_file = run_command(f'cd {event_path} && ls {run_path}/submit/slurm*_master.sh', ssh_client=ssh_client)
        submit_file = submit_file.strip()
        print(f"Found submit file: {submit_file}")

        if walltime:
            print(f"Updating walltime to {walltime}...")
            # sed -E -i.bak "/analysis_[^ ]+_par[0-9]+\.sh\)\)/s/--time=[^[:space:]]+/--time=23:50:00/g" submit_script.sh
            run_command(f'cd {event_path} && sed -E -i.bak "/analysis_[^ ]+_par[0-9]+\.sh\)\)/s/--time=[^[:space:]]+/--time={walltime}/g" {submit_file}', ssh_client=ssh_client)

        run_command(f'source {conda_activate_command} && cd {event_path} && sbatch {submit_file}', ssh_client=ssh_client)