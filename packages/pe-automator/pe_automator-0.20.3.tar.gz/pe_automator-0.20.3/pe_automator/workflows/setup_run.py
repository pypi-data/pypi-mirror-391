from ..actions.update_config import update_config
from ..actions.upload_files import upload_files
from ..actions.remote import run_command, upload_files, extract_submit_command, extract_run_dir, extract_job_id
from ..actions.gitlab import create_gitlab_issue, check_access_to_gitlab, update_job_status, issue_exists, generate_issue_title
from ..actions.allocation import get_allocation_info, get_env_path
from ..utils.encryption import encrypted_name
from ..utils.check import get_dir_size_MB
from ..types.ssh import MultiSSHManager, SimpleSSHClient
from pe_automator._version import __version__
from jinja2 import Template
from datetime import datetime
import os
import shutil
import json
import click


def setup_run(eventname, data_path, run_label, 
              account, partition, qos, approximant, 
              user, conda_env, private_token, allocation, 
              npoint=1000, nact=50, naccept=60, maxmcmc=20000,
              memory=300, cpu=None, walltime='71:40:00',
              dry_run=False, parallel_bilby=False, comment='', distance_marginalization=None,
              minimum_frequency=None, waveform_minimum_frequency=None, waveform_reference_frequency=None,
              encrypt_label=False,
              priors=None, mode_array=None):
    """
    Setup the run environment for the PE Automator workflow.
    This function is called before the main workflow execution.
    """
    with open(os.path.join(data_path, 'project', 'project.json'), 'r') as f:
        project_config = json.load(f)
    print(f"Loaded project configuration: {project_config}")
    gitlab_url, gitlab_project = project_config['gitlab_url'], project_config['gitlab_project']

    if not dry_run:
        check_access_to_gitlab(gitlab_url=gitlab_url, gitlab_project=gitlab_project, private_token=private_token)

    # check if the size of data_path/framefiles is less than 100MB, if true, raise a warning with click
    if not os.path.exists(os.path.join(data_path, 'framefiles')):
        raise FileNotFoundError(f"Data path {os.path.join(data_path, 'framefiles')} does not exist.")
    data_size_MB = get_dir_size_MB(os.path.join(data_path, 'framefiles'))
    if data_size_MB < 100:
        click.confirm(f"The size of the data path {os.path.join(data_path, 'framefiles')} is {data_size_MB:.2f} MB, which is less than 100 MB. "
                       "This could mean the git-lfs is not correctly installed and the framefiles are not correctly pulled. Do you want to continue?", abort=True)        
    
    #### Remote information
    # get allocation information
    allocation_info = get_allocation_info(allocation, data_path)
    hostname = allocation_info['hostname']

    # remote project path
    remote_project_path = os.path.join(allocation_info['scratch'], user, 'uib_o4a_catalog')

    if allocation_info['cluster'] == 'MareNostrum5':
        slurm_extra_lines = f"account={account} partition={partition} qos={qos}"
    else:
        slurm_extra_lines = f"constraint=cal mem={int(memory)}gb"

    #### Local setup
    # define the label
    date = datetime.now().strftime("%Y%m%d")
    label = f"{eventname}_{approximant}_{run_label}_{date}"
    if encrypt_label:
        encrypted_label = encrypted_name(data_path, eventname, approximant, run_label, date)
    else:
        encrypted_label = label

    remote = f"{user}@{hostname}"

    conda_activate_command = f"{get_env_path(allocation_info)}/{conda_env}/bin/activate"

    # set up the configuration file
    config_file = os.path.join(data_path, "configs", f"{eventname}_config.ini")
    template_file = os.path.join(data_path, "templates", "bilby_config.tpl.ini")

    #### Main workflow
    # check if the run exists in git issue
    if not dry_run:
        print(f"Checking if the run already exists in GitLab issues for event {eventname} with approximant {approximant} and label {run_label}")
        if issue_exists(eventname, approximant, run_label, private_token=private_token, gitlab_url=gitlab_url, gitlab_project=gitlab_project):
            print(f"Issue {generate_issue_title(eventname, approximant, run_label)} already exists. Please change the run label if you want to create a new run.")
            print("Exiting setup_run.")
            return
    
    config, files_to_copy = update_config(config_file=config_file, 
                           template_file=template_file, 
                           label=encrypted_label,
                           approximant=approximant,
                           priors=priors,
                           eventname=eventname,
                           slurm_extra_lines=slurm_extra_lines,
                           scheduler_analysis_time=walltime,
                           memory=memory,
                           npoint=npoint,
                           naccept=naccept,
                           nact=nact,
                           maxmcmc=maxmcmc,
                           waveform_minimum_frequency=waveform_minimum_frequency,
                           waveform_reference_frequency=waveform_reference_frequency,
                           minimum_frequency=minimum_frequency,
                           npool=cpu if cpu else allocation_info['cpu_per_node'],
                           mode_array=mode_array,
                           dist_margin=distance_marginalization
                           )

    # create output directory
    outdir = os.path.join("runs", label)
    os.makedirs(outdir, exist_ok=True)

    # save the config content to file
    config_path = os.path.join(outdir, "config.ini")
    with open(config_path, 'w') as f:
        f.write(config)

    # copy necessary files to the output directory
    for file_list in files_to_copy.values():
        for file_path in file_list:
            source_path = os.path.join(data_path, file_path)
            if os.path.exists(source_path):
                # create the destination directory if it doesn't exist
                dest_dir = os.path.dirname(os.path.join(outdir, file_path))
                os.makedirs(dest_dir, exist_ok=True)
                # copy the file
                shutil.copy(source_path, os.path.join(outdir, file_path))
            else:
                raise FileNotFoundError(f"Source file {source_path} does not exist.")
    
    if dry_run:
        print("Dry run mode is enabled. No files will be uploaded to the remote server.")
        print(f"Output directory: {outdir}")
        print(f"Config file: {config_path}")
        return

    # zip the output directory
    shutil.make_archive(outdir, 'zip', outdir)

    # upload the output directory with ssh
    # create a folder ~/uib_o4a_catalog
    with SimpleSSHClient(name=allocation, hostname=hostname, username=user) as ssh_client:
        ssh_client.connect()
        print(f"Creating project directory on cluster: {remote_project_path}")
        run_command(f"mkdir -p {remote_project_path}", ssh_client=ssh_client)

        # upload the zip file to the remote server
        print(f"Uploading files to remote server: {remote_project_path}")
        upload_files(f"{outdir}.zip", remote_project_path, remote)

        # unzip the file on the remote server
        print(f"Unzipping files on remote server: {remote_project_path}/{os.path.basename(outdir)}.zip")
        run_command(f"unzip -o {remote_project_path}/{os.path.basename(outdir)}.zip -d {remote_project_path}/{label}", ssh_client=ssh_client)

        # remove the zip file from the remote server
        print(f"Removing zip file from remote server: {remote_project_path}/{os.path.basename(outdir)}.zip")
        run_command(f"rm {remote_project_path}/{os.path.basename(outdir)}.zip", ssh_client=ssh_client)

        # run conda activate parallel_bilby && cd ~/uib_o4a_catalog/{label} && bilby_pipe config.ini
        print(f"Running bilby_pipe on remote server: {remote_project_path}/{label}")
        output = run_command(f"source {conda_activate_command} && cd {remote_project_path}/{label} && bilby_pipe config.ini", ssh_client=ssh_client)

        submit_command = extract_submit_command(output)

        print(f"Submitting job with command: {submit_command}")
        if allocation_info['cluster'] == 'MareNostrum5':
            submit_file = submit_command.strip().split()[1]
            preprocess_sub_file_command = f"sed -i -e '/^#SBATCH --mem=/d' -e 's/--mem=[^[:space:]]*//g' {submit_file} &&"
        else:
            preprocess_sub_file_command = ''
        job_info = run_command(f"source {conda_activate_command} && cd {remote_project_path}/{label} && {preprocess_sub_file_command} {submit_command}", ssh_client=ssh_client)

    job_id = extract_job_id(job_info)
    run_dir = extract_run_dir(submit_command)

    run_info = {
        "eventname": eventname,
        "approximant": approximant,
        "run_label": run_label,
        "label": label,
        "run_dir": os.path.join(remote_project_path, label, run_dir),
        "job_id": job_id,
        "remote": remote,
        "conda_env": conda_env,
        "priors": priors,
        "mode_array": mode_array,
        "distance_marginalization": distance_marginalization,
        "pipeline_version": __version__,
        "allocation": allocation,
        "user": user,
        "hostname": hostname,
        "npoint": npoint,
        "nact": nact,
        "naccept": naccept,
        "maxmcmc": maxmcmc,
        "memory": memory,
        "cpu": cpu if cpu else allocation_info['cpu_per_node'],
        "f_min": minimum_frequency,
        "waveform_f_min": waveform_minimum_frequency,
        "waveform_f_ref": waveform_reference_frequency,
        "comment": comment,
    }

    print(f"Run setup complete. Run info: {run_info}")

    # dump the run info to a JSON file
    run_info_file = os.path.join(outdir, "run_info.json")
    with open(run_info_file, 'w') as f:
        json.dump(run_info, f, indent=4)

    # create a GitLab issue with the run information
    issue = create_gitlab_issue(run_info, gitlab_url=gitlab_url, gitlab_project=gitlab_project, private_token=private_token)

    # update the job status in the GitLab issue
    update_job_status(issue, 'created')

