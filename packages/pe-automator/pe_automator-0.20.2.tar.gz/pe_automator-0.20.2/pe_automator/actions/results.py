import os
import glob
from pe_automator.actions.remote import download_files


def download_result_file(run, output_dir, user):
    """
    Download the result file for the given run.
    
    Parameters:
    - run: Dictionary containing run information including 'run_dir' and 'remote'.
    - output_dir: Directory where the result file will be downloaded.
    - user: User information for remote access.
    
    Returns:
    - str: Path to the downloaded result file.
    """
    remote = f"{user}@{run['hostname']}"
    result_file = f"{run['run_dir']}/result/*_merge_result.hdf5"

    output_dir = os.path.join(output_dir, run['eventname'])
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Download the result file
    download_files(remote_path=result_file, local_path=output_dir, remote=remote)


def download_corner_plots(run, output_dir, user):
    """
    Download the merged plots for the given run.
    
    Parameters:
    - run: Dictionary containing run information including 'run_dir' and 'remote'.
    - output_dir: Directory where the merged plots will be downloaded.
    - user: User information for remote access.
    
    Returns:
    - str: Path to the downloaded merged plots.
    """
    remote = f"{user}@{run['hostname']}"
    merged_plots = f"{run['run_dir']}/result/*_corner.png"
    
    output_dir = os.path.join(output_dir, run['eventname'])
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Download the merged plots
    download_files(remote_path=merged_plots, local_path=output_dir, remote=remote)


def download_config_file(run, output_dir, user):
    """
    Download the config file for the given run.
    
    Parameters:
    - run: Dictionary containing run information including 'run_dir' and 'remote'.
    - output_dir: Directory where the config file will be downloaded.
    - user: User information for remote access.
    
    Returns:
    - str: Path to the downloaded config file.
    """
    remote = f"{user}@{run['hostname']}"
    config_file = f"{run['run_dir']}/*_config_complete.ini"

    output_dir = os.path.join(output_dir, run['eventname'])
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Download the config file
    download_files(remote_path=config_file, local_path=output_dir, remote=remote)


def check_if_downloaded(run, output_dir):
    """
    Check if the result file and corner plots have been downloaded for the given run.
    
    Parameters:
    - run: Dictionary containing run information including 'eventname'.
    - output_dir: Directory where the results are expected to be downloaded.
    - user: User information for remote access.
    
    Returns:
    - bool: True if both files are downloaded, False otherwise.
    """
    label = run['run_dir'].split('/')[-1]
    result_file = os.path.join(output_dir, run['eventname'], f'{label}*_merge_result.hdf5')

    matched_files = glob.glob(result_file)
    if not matched_files:
        return False
    
    config_file = os.path.join(output_dir, run['eventname'], f'{label}*_config_complete.ini')
    matched_configs = glob.glob(config_file)
    if not matched_configs:
        return False

    return True