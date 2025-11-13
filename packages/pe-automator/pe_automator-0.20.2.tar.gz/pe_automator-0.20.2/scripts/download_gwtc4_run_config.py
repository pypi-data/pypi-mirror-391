# this is a command line script to extract the priors for GWTC-4 with given hdf5 files and save them to a file
import argparse
import h5py
import numpy as np
import re
import os
import shutil
import zipfile
import json


special_runs = {
    'GW230529_181500': 'C00:IMRPhenomXPHM:LowSpinSecondary'
}

default_run_name = 'C00:IMRPhenomXPHM-SpinTaylor'


class FlexibleKeyDict(dict):
    """
    A dictionary that allows flexible key access, replacing '-' with '_' and vice versa, to handle the different key formats
    used in bilby pipe
    """
    def get(self, key, default=None):
        if key in self:
            return super().get(key, default)

        # Try replacing - with _ and vice versa
        alt_key_1 = key.replace('-', '_')
        alt_key_2 = key.replace('_', '-')

        if alt_key_1 in self:
            return super().get(alt_key_1, default)
        elif alt_key_2 in self:
            return super().get(alt_key_2, default)

        return default
    

def get_gw_name_from_hdf5_filename(filename):
    match = re.search(r'GW\d{6}_\d{6}', filename)
    if match:
        return match.group(0)
    else:
        raise ValueError(f"Filename {filename} does not match expected format for GW name.")


def parse_dict_from_string(dict_string):
    dict_string = dict_string.strip('{} \n')
    # Split into key-value pairs
    dict_items = [item for item in dict_string.split(',') if item.strip()]
    # Build the dictionary
    parsed_dict = {}
    for item in dict_items:
        if ':' in item:
            key, value = item.split(':', 1)
            key = key.strip().strip('"').strip("'")
            value = value.strip().strip('"').strip("'")
           
            parsed_dict[key] = value

    return parsed_dict


def parse_array_from_string(array_string):
    if array_string.startswith('['):
        output_arr = eval(array_string)
    else:
        output_arr = [array_string]
    
    output_arr = [item.strip("'") for item in output_arr]
    
    return output_arr


def extract_prior(pe_samples, run_name):
    prior_keys = pe_samples[run_name]['priors']['analytic'].keys()

    prior = {}
    for key in prior_keys:
        value = pe_samples[run_name]['priors']['analytic'][key][0]
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        prior[key] = value

    return prior


def extract_config(pe_samples, run_name):
    config_keys = pe_samples[run_name]['config_file']['config'].keys()

    config = FlexibleKeyDict({})
    for key in config_keys:
        value = pe_samples[run_name]['config_file']['config'][key][0]
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        config[key] = value

    return config


def extract_info(hdf5_files, output_file):
    # create a tmp directory to store the priors
    os.makedirs('priors', exist_ok=True)
    os.makedirs('configs', exist_ok=True)
    os.makedirs('psds', exist_ok=True)
    os.makedirs('spline_cal_envs', exist_ok=True)
    os.makedirs('framefile_meta', exist_ok=True)

    for hdf5_file in hdf5_files:
        gw_name = get_gw_name_from_hdf5_filename(hdf5_file)
        
        with h5py.File(hdf5_file, 'r') as pe_samples:
            wf_run_name = special_runs.get(gw_name, default_run_name)

            # extract the prior for the given run name
            prior = extract_prior(pe_samples, wf_run_name)

            print(f"Extracting priors for {gw_name} with run name {wf_run_name}")
            with open(f'priors/{gw_name}_priors.ini', 'wb') as f:
                for key, value in prior.items():
                    f.write(f"{key} = {value}\n".encode('utf-8'))

            # extract the config for the given run name
            config = extract_config(pe_samples, wf_run_name)

            print(f"Extracting config for {gw_name} with run name {wf_run_name}")
            with open(f'configs/{gw_name}_config.ini', 'wb') as f:
                for key, value in config.items():
                    f.write(f"{key} = {value}\n".encode('utf-8'))

            psd_dict = parse_dict_from_string(config.get('psd-dict'))
            spline_cal_env_dict = parse_dict_from_string(config.get('spline-calibration-envelope-dict'))

            # copy the psd file to the psds directory
            for ifo, psd_file in psd_dict.items():
                dst_psd_path = os.path.join('psds', f"{gw_name}_{ifo}_psd.txt")
                shutil.copyfile(psd_file, dst_psd_path)

            # copy the spline calibration envelope file to the spline_cal_envs directory
            for ifo, spline_cal_env_file in spline_cal_env_dict.items():
                dst_spline_cal_env_path = os.path.join('spline_cal_envs', f"{gw_name}_{ifo}_spline_cal_env.txt")
                shutil.copyfile(spline_cal_env_file, dst_spline_cal_env_path)

            detectors = parse_array_from_string(config['detectors'])
            channel_dict = parse_dict_from_string(config.get('channel-dict'))
            trigger_time = float(config.get('trigger-time'))
            post_trigger_duration = float(config.get('post-trigger-duration', 0))
            duration = float(config['duration'])
            start_time = trigger_time + post_trigger_duration - duration
            end_time = start_time + duration
            required_data = {
                'gw_name': gw_name,
                'detectors': detectors,
                'channel_dict': channel_dict,
                'trigger_time': trigger_time,
                'post_trigger_duration': post_trigger_duration,
                'duration': duration,
                'start_time': start_time,
                'end_time': end_time
            }
            # save the required data to a json file
            with open(f'framefile_meta/{gw_name}.json', 'w') as f:
                json.dump(required_data, f, indent=4)


    # create a zip file with the priors and configs, keeping the directory structure
    with zipfile.ZipFile(output_file, 'w') as zipf:
        for dir in ['priors', 'configs', 'psds', 'spline_cal_envs', 'framefile_meta']:
            for root, dirs, files in os.walk(dir):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(dir, '..')))

    # clean up the tmp directory
    shutil.rmtree('priors')
    shutil.rmtree('configs')
    shutil.rmtree('psds')
    shutil.rmtree('spline_cal_envs')
    shutil.rmtree('framefile_meta')


def main():
    parser = argparse.ArgumentParser(description="Extract priors from GWTC-4 HDF5 files.")
    parser.add_argument('gwtc4_directory', type=str, help='Directory containing the GWTC-4 HDF5 files.')
    parser.add_argument('--output', type=str, default='gwtc4_info.zip',
                        help='Output file to save the extracted priors (default: gwtc4_info.zip)')
    

    args = parser.parse_args()

    # get all hdf5 files contains 'GW' in the gwtc4_directory
    hdf5_files = [os.path.join(args.gwtc4_directory, f) for f in os.listdir(args.gwtc4_directory) if f.endswith('.hdf5') and 'combined_PEDataRelease' in f]

    extract_info(hdf5_files, args.output)


if __name__ == "__main__":
    main()