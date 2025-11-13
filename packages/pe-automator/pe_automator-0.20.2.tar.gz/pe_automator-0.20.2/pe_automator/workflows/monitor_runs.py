from datetime import datetime
import os
import json
from ..actions.gitlab import fetch_runs, update_job_status, get_job_status
from ..actions.job_status import check_data_analysis, check_data_generated
from ..actions.results import download_result_file, download_corner_plots, check_if_downloaded, download_config_file
from ..actions.git import push_new_results
from ..actions.allocation import get_all_allocations, get_allocation_info
from ..types.ssh import MultiSSHManager, SimpleSSHClient

def monitor_runs(private_token, ssh_key, result_dir='results', data_path='data'):
    """
    Monitor the PE Automator processes.
    This function will check the status of the PE Automator runs and print relevant information.
    """
    # get the list of runs from gitlab issues
    with open(os.path.join(data_path, 'project', 'project.json'), 'r') as f:
        project_config = json.load(f)
    print(f"Loaded project configuration: {project_config}")
    gitlab_url, gitlab_project = project_config['gitlab_url'], project_config['gitlab_project']

    runs = fetch_runs(gitlab_url=gitlab_url, gitlab_project=gitlab_project, private_token=private_token)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Found {len(runs['ongoing'])} ongoing runs, {len(runs['completed'])} completed runs, and {len(runs['failed'])} failed runs.")
    
    print("Now checking the status of ongoing runs...")
    with MultiSSHManager() as manager:
        for run in runs['ongoing']:
            print(f"Checking run: {run['title']}")

            allocation = get_allocation_info(run['allocation'], data_path)
            user = allocation['maintainer']

            manager.add_client(
                name=run['allocation'],
                hostname=allocation['hostname'],
                username=user,
                key_filename=ssh_key,
                skip_if_exists=True
            )
            ssh_client = manager.get_client(run['allocation'])

            # Check if data generation is complete
            status, message = check_data_generated(run, ssh_client)
            print(f"Run data generation - Status: {status}, Message: {message}")
            if status:
                # which means it is either failed or pending
                update_job_status(run['issue'], status)
                if message:
                    run['issue'].notes.create({'body': f"Error message at stage data generation: \n\n{now}\n\n```\n{message}\n```\n\n"})
                # so we can skip the rest of the checks
                continue
        
            # Check if data analysis is complete
            status, message = check_data_analysis(run, ssh_client)
            print(f"Run analysis - Status: {status}, Message: {message}")
            current_status = get_job_status(run['issue'])
            if status:
                update_job_status(run['issue'], status)
                if status == 'completed':
                    print(f"Run {run['title']} is completed. Closing the issue and downloading the data.")
                    run['issue'].state_event = 'close'
                    run['issue'].save()
            if message:
                if current_status == 'hold' and get_job_status(run['issue']) == 'hold':
                    print(f"Run {run['title']} is on hold. No need to add a comment.")
                else:
                    # if the message is an array
                    if isinstance(message, list):
                        message = '\n'.join([f'```\n{line}\n```' for line in message])
                    else:
                        message = f'```\n{message}\n```'
                    run['issue'].notes.create({'body': f"Error message: \n\n{now}\n\n{message}\n\n"})

            # if it is running, gather the run status
            if status == 'running':
                process_ongoing_run(run)
            # if it is done, download the data
            elif status == 'completed':
                process_completed_run(run, user, result_dir)

    for run in runs['completed']:
        allocation = get_allocation_info(run['allocation'], data_path)
        user = allocation['maintainer']
        print(f"Processing completed run: {run['title']}")
        process_completed_run(run, user, result_dir)
    
    # generate the result catalog
    results_catalog = generate_results_catalog(runs['completed'], result_dir=result_dir)
    with open(os.path.join(result_dir, 'results_catalog.json'), 'w') as f:
        json.dump(results_catalog, f, indent=4)


def process_completed_run(run_info, user, result_dir):
    """
    Process a completed run.
    This function will handle the post-processing of a completed run.
    """
    # get the last part of the run directory
    if check_if_downloaded(run_info, output_dir=result_dir):
        print(f"Run {run_info['title']} has already been downloaded. Skipping download.")
        return
 
    download_result_file(run_info, output_dir=result_dir, user=user)
    download_config_file(run_info, output_dir=result_dir, user=user)
    download_corner_plots(run_info, output_dir=result_dir, user=user)
    # push_new_results(result_dir)


def process_ongoing_run(run):
    """
    Process an ongoing run.
    This function will handle the post-processing of an ongoing run.
    """
    print(f"(Not implemented yet) Processing ongoing run: {run['title']}")
    # Here you can implement the logic to handle the ongoing run
    # For example, checking the status, updating the user, etc.
    pass


def generate_results_catalog(completed_runs, result_dir):
    """
    Generate a results catalog from the completed runs.
    This function will create a catalog of the completed runs.
    """
    print("Generating results catalog...")
    eventnames = set(run['eventname'] for run in completed_runs)
    results_catalog = {eventname: [] for eventname in eventnames}
    
    for run in completed_runs:
        eventname = run['eventname']
        run['issue_url'] = run['issue'].web_url
        run['issue_title'] = run['issue'].title
        run['submitted_by'] = run['issue'].author['name']
        run['created_at'] = run['issue'].created_at
        run['closed_at'] = run['issue'].closed_at
        del run['issue']  # Remove the issue object to avoid serialization issues

        # find file path contains f"{run_info['approximant']}_{run_info['run_label']}" in {results}/{eventname} 
        event_dir = f'{result_dir}/{eventname}'
        if not os.path.exists(event_dir):
            print(f"Error: Directory {event_dir} does not exist for event {eventname}")
            continue
        else:
            file_path = next((f for f in os.listdir(event_dir) if f"{run['approximant']}_{run['run_label']}" in f and (f.endswith('.hdf5') or f.endswith('.h5'))), None)
            if not file_path:
                print(f"Error: File not found for run {run['run_label']} in event {eventname}")
            else:
                run['file_path'] = os.path.join(event_dir, file_path)
        results_catalog[eventname].append(run)

    return results_catalog