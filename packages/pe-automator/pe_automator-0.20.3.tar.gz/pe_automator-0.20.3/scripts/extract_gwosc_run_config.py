# this is a command line script to extract the priors for GWTC-4 with given hdf5 files and save them to a file
import argparse
import h5py
import numpy as np
import re
import os
import shutil
import zipfile
import json
from math import floor, ceil

special_runs = {
    'GW230529_181500': 'C00:IMRPhenomXPHM:LowSpinSecondary',
    'GW250114_082203': 'bilby-IMRPhenomXPHM-SpinTaylor_prod-reweighted'
}

default_run_name = ['C00:IMRPhenomXPHM-SpinTaylor', 'C01:IMRPhenomXPHM', 'IMRPhenomPv2_posterior', 'IMRPhenomPv2NRT_highSpin_posterior', 'C01:IMRPhenomXPHM:HighSpin', 'C01:IMRPhenomPv2_NRTidal:HighSpin']


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
    

def find_preferred_wf_run(eventname, pe_samples):
    run_names = list(pe_samples.keys())
    if special_runs.get(eventname):
        return special_runs[eventname]
    
    for preferred_run in default_run_name:
        if preferred_run in run_names:
            return preferred_run
    return None


def get_gw_name_from_hdf5_filename(filename):
    match = re.search(r'GW\d{6}_\d{6}', filename)
    if match:
        return match.group(0)
    
    match = re.search(r'GW\d{6}', filename)
    if match:
        return match.group(0)
    
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
        if value.startswith('UniformInComponentsChirpMass') or value.startswith('UniformSourceFrame') or value.startswith('UniformInComponentsMassRatio'):
            # print(f"⚠️ Detected complex prior {value} for key {key}, replacing with bilby.gw.prior.{value}")
            value = f'bilby.gw.prior.{value}'
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


def extract_psds(pe_samples, run_name):
    psd_keys = pe_samples[run_name]['psds'].keys()

    psds = {}
    for key in psd_keys:
        psds[key] = np.array(pe_samples[run_name]['psds'][key])

    return psds


def extract_cal_env(pe_samples, run_name):
    cal_env_keys = pe_samples[run_name]['calibration_envelope'].keys()

    cal_env = {}
    for key in cal_env_keys:
        cal_env[key] = np.array(pe_samples[run_name]['calibration_envelope'][key])

    return cal_env


def extract_info(hdf5_files, output_dir):
    os.chdir(output_dir)
    # create a tmp directory to store the priors
    os.makedirs('configs', exist_ok=True)
    os.makedirs('psds', exist_ok=True)
    os.makedirs('spline_cal_envs', exist_ok=True)
    os.makedirs('framefile_meta', exist_ok=True)

    for hdf5_file in hdf5_files:
        gw_name = get_gw_name_from_hdf5_filename(hdf5_file)
        try:
            f = h5py.File(hdf5_file, 'r')
        except Exception as e:
            print(f"⚠️ Failed to open {hdf5_file}: {e}")
            continue
        
        with f as pe_samples:
            wf_run_name = find_preferred_wf_run(gw_name, pe_samples)
            if wf_run_name is None:
                print(f"⚠️ No preferred wf run found for {gw_name} in {hdf5_file}, available runs: {list(pe_samples.keys())}")
                continue
            print(f"Extracting config for {gw_name} with run name {wf_run_name}")

            # check if it is compatible
            try:
                _ = pe_samples[wf_run_name]['config_file']['config']
            except:
                print(f"⚠️ Incompatible PE samples structure for {gw_name} in {hdf5_file} under run {wf_run_name}, skipping.")
                continue
            
            # extract the config for the given run name
            config = extract_config(pe_samples, wf_run_name)

            # rewrite channel dict
            channel_dict = parse_dict_from_string(config.get('channel-dict'))
            for key in channel_dict.keys():
                channel_dict[key] = f"GWOSC-16KHZ_R1_STRAIN"
            if 'channel-dict' in config:
                config['channel-dict'] = '{' + ', '.join(f'{k}: {v}' for k, v in channel_dict.items()) + '}'
            elif 'channel_dict' in config:
                config['channel_dict'] = '{' + ', '.join(f'{k}: {v}' for k, v in channel_dict.items()) + '}'
            else:
                config['channel-dict'] = '{' + ', '.join(f'{k}: {v}' for k, v in channel_dict.items()) + '}'

            # rewrite the prior
            if not config.get('prior-dict') or config.get('prior-dict') == 'None':
                print("⏳ Extracting prior...")
                prior = extract_prior(pe_samples, wf_run_name)
                prior_str = '{' + ', '.join(f"{k}: {v}" for k, v in prior.items()) + '}'
                config['prior-dict'] = prior_str
                config['prior-file'] = 'None'

            config['calibration-correction-type'] = 'template'

            with open(f'configs/{gw_name}_config.ini', 'wb') as f:
                for key, value in config.items():
                    f.write(f"{key} = {value}\n".encode('utf-8'))

            psd_dict = extract_psds(pe_samples, wf_run_name)
            cal_env_dict = extract_cal_env(pe_samples, wf_run_name)

            for ifo, psd in psd_dict.items():
                np.savetxt(f'psds/{gw_name}_{ifo}_psd.txt', psd)
            for ifo, cal_env in cal_env_dict.items():
                np.savetxt(f'spline_cal_envs/{gw_name}_{ifo}_spline_cal_env.txt', cal_env)

            detectors = parse_array_from_string(config['detectors'])
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
                'start_time': floor(start_time),
                'end_time': ceil(end_time),
                'gwosc': True
            }
            # save the required data to a json file
            with open(f'framefile_meta/{gw_name}.json', 'w') as f:
                json.dump(required_data, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Extract priors from GWOSCg HDF5 files.")
    parser.add_argument('gwosc_directory', type=str, help='Directory containing the GWOSC HDF5 files.')
    parser.add_argument('--output', type=str, default='data',
                        help='Output file to save the extracted priors (default: data)')
    

    args = parser.parse_args()

    gwosc_directory = os.path.abspath(args.gwosc_directory)
    args.output = os.path.abspath(args.output)

    # get all hdf5 files contains 'GW' in the gwosc_directory
    hdf5_files = [os.path.join(gwosc_directory, f) for f in os.listdir(gwosc_directory) if (f.endswith('.hdf5') or f.endswith('.h5') or f.endswith('.hdf')) and 'combined_PEDataRelease' in f]
    print(f"Found {len(hdf5_files)} HDF5 files in {gwosc_directory}")
    extract_info(hdf5_files, args.output)


if __name__ == "__main__":
    main()