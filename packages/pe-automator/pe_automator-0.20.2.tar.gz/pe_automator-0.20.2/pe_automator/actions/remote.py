import os
import subprocess
import regex
from pe_automator.utils.parse_ssh_output import clean_env_in_string

def run_command(command, remote="", silent=False, ssh_client=None):
    """
    Run a command on the remote server.
    """
    if ssh_client:
        if not silent:
            print(f"Running command on remote server {ssh_client.username}@{ssh_client.hostname}: {command}")
        # If ssh_client is provided, use it to execute the command
        result, err = ssh_client.execute(command, get_output=True)
        if not silent:
            print(f"Command output: {result + err}")
        # if err:
        #     print(f"Error executing command: {err}")
        #     raise Exception(f"Command failed with error: {err}")
        return result + ' ' + clean_env_in_string(err)

    if remote:
        if not silent:
            print(f"Running command on remote server {remote}: {command}")
        result = subprocess.run(["ssh", remote, command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if not silent:
            print(f"Command output: {result.stdout}")
        if result.returncode != 0:
            print(f"Error running command: {result.stderr}")
            raise Exception(f"Command failed with error: {result.stdout} {result.stderr}")
        return result.stdout
    
    raise ValueError("Either ssh_client or remote must be provided to run_command.")
    

def upload_files(local_path, remote_path, remote):
    """
    Upload files from local path to remote path.
    """
    print(f"Uploading files from {local_path} to {remote}:{remote_path}")
    os.system(f"rsync -havP  {local_path} {remote}:{remote_path}")


def download_files(remote_path, local_path, remote, is_file=False):
    """
    Download files from remote path to local path.
    """
    print(f"Downloading files from {remote}:{remote_path} to {local_path}")
    # get the directory part of the local path
    if is_file:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
    else:
        os.makedirs(local_path, exist_ok=True)
    os.system(f"rsync -av --ignore-existing {remote}:{remote_path} {local_path}")


def extract_submit_command(log):
    """
    Extra the line '$ sbatch xxx' command from the log to submit the job.
    """
    lines = log.split('\n')
    for line in lines:
        if line.startswith('$ sbatch'):
            command = line[2:].strip()  # Remove the leading '$ ' and strip whitespace
            print(f"Extracted submit command: {command}")
            return command
    raise ValueError("No submit command found in the log.")


def extract_run_dir(submit_command):
    """
    Extract the run directory from the submit command
    """
    match = regex.search(r'sbatch\s+(.+?)/submit/', submit_command)
    if match:
        run_dir = match.group(1)
        print(f"Extracted run directory: {run_dir}")
        return run_dir
    else:
        raise ValueError("No run directory found in the submit command.")


def extract_job_id(log):
    """
    Extract the job ID from the log Submitted batch job xxxx
    """
    lines = log.split('\n')
    for line in lines:
        print(line)
        # if line.strip().startswith('Submitted batch job'):
        #     job_id = line.split()[-1]  # Get the last word in the line
        #     print(f"Extracted job ID: {job_id}")
        #     return job_id
        match = regex.search(r'Submitted batch job (\d+)', line)
        if match:
            job_id = match.group(1)
            print(f"Extracted job ID: {job_id}")
            return job_id
    raise ValueError("No job ID found in the log.")