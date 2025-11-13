import gitlab

approximant_table = {
    'IMRPhenomXHM_NSBH': 'XHM_NSBH',
    'IMRPhenomXPNR': 'XPNR',
    'IMRPhenomXPHM': 'XPHM',
    'IMRPhenomXPHM_lal': 'XPHM_lal',
    'IMRPhenomTHM': 'THM',
    'IMRPhenomTEHM': 'TEHM',
    'IMRPhenomXE': 'XE',
    'IMRPhenomXHM': 'XHM',
    'IMRPhenomTHM_20': 'THM_20',
}

rev_approximant_table = {v: k for k, v in approximant_table.items()}

def generate_issue_title(eventname, approximant, run_label):
    """
    Generate a title for the GitLab issue based on event name, approximant, and run label.
    
    Parameters:
    - eventname: Name of the event
    - approximant: Gravitational wave approximant
    - run_label: Label for the run
    
    Returns:
    - A formatted string representing the issue title.
    """
    return f"{eventname} - {approximant} - {run_label}"


def check_access_to_gitlab(gitlab_url, gitlab_project, private_token=None):
    """
    Check if the user has access to the GitLab instance.
    
    Parameters:
    - gitlab_url: URL of the GitLab instance
    - private_token: Personal access token for GitLab authentication
    
    Returns:
    - True if access is successful, False otherwise.
    """
    try:
        gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        gl.projects.get(gitlab_project)
        print("Access to GitLab is successful.")
        return True
    except gitlab.exceptions.GitlabAuthenticationError:
        print("Authentication failed. Please check your private token.")
        return False
    except Exception as e:
        print(f"An error occurred while accessing GitLab: {e}")
        return False


def create_gitlab_issue(run_info, gitlab_url, gitlab_project, private_token=None):
    """
    Create a GitLab issue with the run information.
    
    Parameters:
    - run_info: dict containing run information (eventname, approximant, run_label, run_dir, job_id, remote, conda_env)
    - gitlab_url: URL of the GitLab instance
    - private_token: Personal access token for GitLab authentication
    
    Returns:
    - The created issue object.
    """
    # Authenticate with GitLab
    gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
    
    # Get the project (replace with your project ID or namespace/project-name)
    project = gl.projects.get(gitlab_project)
    
    # Create a new issue
    issue_title = generate_issue_title(run_info['eventname'], run_info['approximant'], run_info['run_label'])

    # information to be added to the issue
    information = f"Run directory: {run_info['run_dir']}\n\n" \
                  f"Label: {run_info['label']}\n\n" \
                  f"Job ID: {run_info['job_id']}\n\n" \
                  f"Remote: {run_info['remote']}\n\n" \
                  f"Conda environment: {run_info['conda_env']}\n\n" \
                  f"Pipeline version: {run_info['pipeline_version']}\n\n" \
                  f"Allocation: {run_info['allocation']}\n\n" \
                  f"User: {run_info['user']}\n\n" \
                  f"Hostname: {run_info['hostname']}\n\n" \
                  f"Npoint: {run_info['npoint']}\n\n" \
                  f"Nact: {run_info['nact']}\n\n" \
                  f"Naccept: {run_info['naccept']}\n\n" \
                  f"MaxMCMC: {run_info['maxmcmc']}\n\n" \
                  f"Memory: {run_info['memory']}\n\n" \
                  f"CPU: {run_info['cpu']}\n\n" \
                  f"F_min: {run_info.get('f_min', 'N/A')}\n\n" \
                  f"Waveform F_min: {run_info.get('waveform_f_min', 'N/A')}\n\n" \
                  f"Waveform F_ref: {run_info.get('waveform_f_ref', 'N/A')}\n\n" \
                  f"Priors: {run_info.get('priors', '')}\n\n" \
                  f"Mode array: {run_info.get('mode_array', '')}\n\n" \
                  f"Distance marginalization: {run_info.get('distance_marginalization', '')}\n\n" \
                  f"Comment: {run_info.get('comment', '')}\n\n"

    # check if the issue already exists
    existing_issues = project.issues.list(search=issue_title, labels='PE Run')
    if existing_issues:
        print(f"Issue with title '{issue_title}' already exists. Not creating a new issue.")
        
        # add the run information to the existing issue as a comment and attach the json file
        # existing_issues[0].notes.create({
        #     'body': f"Run directory: {run_info['run_dir']}\n\nJob ID: {run_info['job_id']}\n\nRemote: {run_info['remote']}\n\nConda environment: {run_info['conda_env']}",
        # })
        existing_issues[0].notes.create({
            'body': information,
        })
        
        return existing_issues[0]

    approximant = run_info['approximant']
    new_issue = project.issues.create({
        'title': issue_title,
        'description': information,
        'labels': ['PE Run', f'event::{run_info["eventname"]}', f'approx::{approximant_table.get(approximant, approximant)}'],
    })

    print(f"Created new issue: {new_issue.title} (ID: {new_issue.id})")
    
    return new_issue


def update_job_status(issue, status):
    """
    Update the job status in the GitLab issue.
    
    Parameters:
    - issue: The GitLab issue object
    - status: The status to update (e.g., 'created', 'running', 'completed', 'failed')
    
    Returns:
    - None
    """
    # Remove existing job status labels
    for label in issue.labels:
        if label.startswith('job::'):
            issue.labels.remove(label)
    
    # Add the new job status label
    issue.labels.append(f'job::{status}')
    
    # Save the changes to the issue
    issue.save()
    
    print(f"Updated issue {issue.id} with status '{status}'.")


def get_job_status(issue):
    """
    Get the job status from the GitLab issue.
    
    Parameters:
    - issue: The GitLab issue object
    
    Returns:
    - The job status (e.g., 'created', 'running', 'completed', 'failed') or None if not found.
    """
    for label in issue.labels:
        if label.startswith('job::'):
            return label[len('job::'):].strip()
    return None


def add_approximant_to_issue(issue, approximant):
    """
    Add the approximant to the GitLab issue.
    
    Parameters:
    - issue: The GitLab issue object
    - approximant: The approximant to add
    
    Returns:
    - None
    """
    # Add the approximant as a label
    issue.labels.append(f'approx::{approximant_table.get(approximant, approximant)}')
    
    # Save the changes to the issue
    issue.save()
    
    print(f"Added approximant '{approximant}' to issue {issue.id}.")


def fetch_runs(gitlab_url, gitlab_project, private_token=None):
    """
    Fetch all runs from the GitLab project.
    
    Parameters:
    - gitlab_url: URL of the GitLab instance
    - gitlab_project: Project ID or namespace/project-name
    - private_token: Personal access token for GitLab authentication
    
    Returns:
    - A list of run information dictionaries.
    """
    gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
    project = gl.projects.get(gitlab_project)
    
    issues = project.issues.list(labels='PE Run', get_all=True)
    
    completed_runs = [get_information_from_issue(issue) for issue in issues if 'job::completed' in issue.labels]
    failed_runs = [get_information_from_issue(issue) for issue in issues if 'job::failed' in issue.labels]
    canceled_runs = [get_information_from_issue(issue) for issue in issues if 'job::cancelled' in issue.labels]
    ongoing_runs = [get_information_from_issue(issue) for issue in issues if 
                    'job::completed' not in issue.labels and
                    'job::failed' not in issue.labels and
                    'job::cancelled' not in issue.labels]

    return {
        'completed': completed_runs,
        'failed': failed_runs,
        'canceled': canceled_runs,
        'ongoing': ongoing_runs,
    }


def get_information_from_issue(issue) -> dict:
    """
    Parse the comment to extract run directory, job ID, remote, and conda environment.
    """
    comment = issue.description
    eventname = get_label(issue.labels, 'event::')
    approx = get_label(issue.labels, 'approx::')
    approximant = rev_approximant_table.get(approx, approx)
    job_status = get_label(issue.labels, 'job::')
    run_label = [t.strip() for t in issue.title.split('-')][2]
    run_info = {
        'eventname': eventname,
        'approximant': approximant,
        'job_status': job_status,
        'run_label': run_label,
    }

    for line in comment.split('\n'):
        if line.startswith('Run directory:'):
            run_info['run_dir'] = line.split(': ')[1].strip()
        elif line.startswith('Job ID:'):
            run_info['job_id'] = line.split(': ')[1].strip()
        elif line.startswith('Remote:'):
            run_info['remote'] = line.split(': ')[1].strip()
        elif line.startswith('Conda environment:'):
            run_info['conda_env'] = line.split(': ')[1].strip()
        elif line.startswith('Allocation:'):
            run_info['allocation'] = line.split(': ')[1].strip()
        elif line.startswith('User:'):
            run_info['user'] = line.split(': ')[1].strip()
        elif line.startswith('Hostname:'):
            run_info['hostname'] = line.split(': ')[1].strip()
        elif line.startswith('Npoint:'):
            run_info['npoint'] = int(line.split(': ')[1].strip())
        elif line.startswith('Nact:'):
            run_info['nact'] = int(line.split(': ')[1].strip())
        elif line.startswith('Naccept:'):
            run_info['naccept'] = int(line.split(': ')[1].strip())
        elif line.startswith('MaxMCMC:'):
            run_info['maxmcmc'] = int(line.split(': ')[1].strip())
        elif line.startswith('Memory:'):
            run_info['memory'] = int(line.split(': ')[1].strip())
        elif line.startswith('CPU:'):
            run_info['cpu'] = int(line.split(': ')[1].strip())
        elif line.startswith('Priors:'):
            run_info['priors'] = line.split(': ')[1].strip()
        elif line.startswith('Mode array:'):
            run_info['mode_array'] = eval(line.split(': ')[1].strip())
        elif line.startswith('Distance marginalization:'):  
            dm_str = line.split(': ')[1].strip()
            if dm_str == 'True':
                run_info['distance_marginalization'] = True
            elif dm_str == 'False':
                run_info['distance_marginalization'] = False
            else:
                run_info['distance_marginalization'] = None
        elif line.startswith('F_min:'):
            run_info['f_min'] = float(line.split(': ')[1].strip()) if line.split(': ')[1].strip() != 'None' else None
        elif line.startswith('Waveform F_min:'):
            run_info['waveform_f_min'] = float(line.split(': ')[1].strip()) if line.split(': ')[1].strip() != 'None' else None
        elif line.startswith('Waveform F_ref:'):
            run_info['waveform_f_ref'] = float(line.split(': ')[1].strip()) if line.split(': ')[1].strip() != 'None' else None
        elif line.startswith('Comment:'):
            if len(line.split(': ')) > 1:
                run_info['comment'] = line.split(': ')[1].strip()
    
    run_info['issue'] = issue
    run_info['title'] = issue.title
    return run_info


def issue_exists(event_name, approximant, run_label, gitlab_url, gitlab_project, private_token=None):
    """
    Check if an issue with the given event name, approximant, and run label already exists.
    
    Parameters:
    - event_name: Name of the event
    - approximant: Gravitational wave approximant
    - run_label: Label for the run
    - gitlab_url: URL of the GitLab instance
    - private_token: Personal access token for GitLab authentication
    
    Returns:
    - True if the issue exists, False otherwise.
    """
    gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
    project = gl.projects.get(gitlab_project)
    
    issue_title = generate_issue_title(event_name, approximant, run_label)
    issues = project.issues.list(search=issue_title, labels='PE Run')
    
    return len(issues) > 0


def get_label(labels, key):
    """
    Get the value of a label from the issue labels.
    """
    for label in labels:
        if label.startswith(key):
            return label[len(key):].strip()
    return None