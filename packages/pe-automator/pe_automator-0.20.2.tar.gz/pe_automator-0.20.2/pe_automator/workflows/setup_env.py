import json
import shutil
from pathlib import Path
from ..actions.remote import run_command, upload_files, download_files
from ..actions.allocation import get_all_allocations
from filecmp import cmp

def setup_env(env_name, source_env, source_remote, data_dir):
    # download the packed environment
    print(f"Downloading packed environment {env_name} from {source_remote}:{source_env}")
    # This is a placeholder for the actual download logic
    ext = ''.join(Path(source_env).suffixes)
    env_filename = f"{env_name}{ext}"
    packed_env = f"{data_dir}/envs/{env_filename}"
    if source_remote:
        download_files(source_env, packed_env, source_remote, is_file=True)
    else:
        # skip if two files are the same
        if Path(source_env).exists() and Path(packed_env).exists() and cmp(source_env, packed_env, shallow=False):
            print(f"Environment {env_name} already exists in {data_dir}/envs, skipping download")
        else:
            print(f"Copying environment {env_name} to {data_dir}/envs")
            Path(data_dir, 'envs').mkdir(parents=True, exist_ok=True)
            shutil.copy(source_env, packed_env)

    # get the allocations
    allocations = get_all_allocations(data_dir)

    # upload the environment to the remote servers
    for name, allocation in allocations.items():
        hostname = allocation.get('hostname')
        maintainer = allocation.get('maintainer')
        scratch = allocation.get('scratch')
        
        if not (hostname and maintainer and scratch):
            print(f"No remote specified for allocation {name}, skipping upload")

        remote = f"{maintainer}@{hostname}"
        env_path = f"{scratch}/{maintainer}/envs"
        target_path = f"{env_path}/{env_name}"

        # check if the conda env exists on the remote server by checking the target path is not empty
        check_command = f"if [ -d {target_path} ] && [ \"$(ls -A {target_path})\" ]; then echo 'exists'; else echo 'not exists'; fi"
        exists = run_command(check_command, remote)
        if exists.strip() == "exists":
            print(f"Environment {env_name} already exists on {remote}, skipping upload")
        else:
            # upload the environment
            print(f"Uploading environment {env_name} to {remote}:{target_path}")
            # create the target directory if it does not exist
            create_dir_command = f"mkdir -p {env_path}"
            run_command(create_dir_command, remote)
            upload_files(packed_env, env_path, remote)

            # set the conda environment
            print(f"Unpacking environment {env_name} on {remote}:{target_path}")
            set_env_command = f"mkdir -p {target_path} && tar -xzf {env_path}/{env_filename} -C {target_path}"
            run_command(set_env_command, remote)

            # unpack the environment
            # print(f"Unpacking environment {env_name} on {remote}:{target_path}")
            # unpack_command = f"source {target_path}/bin/activate && conda-unpack "
            # run_command(unpack_command, remote)

        # check if the environment is set correctly
        print(f"Checking if environment {env_name} is set correctly on {remote}")
        # try import bilby
        check_command = f"source {target_path}/bin/activate && python -c 'import bilby; print(bilby.__version__)'"
        version = run_command(check_command, remote)
        if version:
            print(f"Environment {env_name} is set correctly on {remote}, version: {version.strip()}")