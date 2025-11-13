from pe_automator.actions.gitlab import fetch_runs
import os
import json
import re
import bilby
import numpy as np


def get_jobs(access_token, gitlab_url, gitlab_project, approximant, status='all'):
    """
    Get the jobs for a given approximant and status.
    """
    runs = fetch_runs(gitlab_url=gitlab_url, gitlab_project=gitlab_project, private_token=access_token)

    if status == 'all':
        selected_runs = [r for r in runs['completed'] if r['approximant'] == approximant] + \
               [r for r in runs['ongoing'] if r['approximant'] == approximant]
    elif status == 'completed':
        selected_runs = [r for r in runs['completed'] if r['approximant'] == approximant]
    elif status == 'ongoing':
        selected_runs = [r for r in runs['ongoing'] if r['approximant'] == approximant]
    else:
        raise ValueError("Status must be 'all', 'completed', or 'ongoing'.")
    
    eventnames = [r['eventname'] for r in selected_runs]
    reformated_runs = { eventname: [] for eventname in eventnames }
    for run in selected_runs:
        reformated_runs[run['eventname']].append(run)

    return reformated_runs


def get_full_eventnames(data_folder):
    full_eventnames = []
    for filename in os.listdir(os.path.join(data_folder, 'configs')):
        if filename.endswith("_config.ini"):
            # extract the event name from the filename
            eventname = filename.split("_config.ini")[0]
            full_eventnames.append(eventname)

    # sort the event names
    full_eventnames.sort()
    return full_eventnames


def read_results_catalog(results_folder='results', results_catalog_file='results_catalog.json'):
    """
    Read the results catalog from a JSON file.
    """
    return Catalog(os.path.join(results_folder, results_catalog_file))


def get_gwtc_hdf5_filename(gwtc4_directory, run_name='C00:IMRPhenomXPHM-SpinTaylor', special_runs={}):
    """
    Functions to get the GWTC HDF5 filename for a given event and run name.

    Arguments:
    - gwtc4_directory: The directory containing the GWTC-4 HDF5 files.
    - run_name: The name of the run to use if no special run is found.
    - special_runs: A dictionary mapping event names to special run names.

    """

    hdf5_files = [os.path.join(gwtc4_directory, f) for f in os.listdir(gwtc4_directory) if f.endswith('.hdf5') and 'combined_PEDataRelease' in f]

    gwtc_files = {}
    for filename in hdf5_files:
        match = re.search(r'GW\d{6}_\d{6}', filename)
        if match:
            eventname = match.group(0)
            gwtc_files[eventname] = {
                'filename': filename,
                'run_name': special_runs.get(eventname, run_name),
                'merged': True
            }
        else:
            print(f"Warning: No GWTC-4 match found in filename {filename}")

    return gwtc_files


class Catalog(dict):
    """
    A dictionary subclass to hold catalog information.
    """
    def __init__(self, filename):
        super().__init__()
        self.read(filename)

    def read(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        self.update(data)
        self.__dict__ = self

    def get_run(self, eventname, approx, label):
        runs = self.get(eventname, [])
        for run in runs:
            if run['approximant'] == approx and run['run_label'] == label:
                return run
        return None
    
    def get_result_file_base(self, eventname, approx, label):
        run = self.get_run(eventname, approx, label)
        if run:
            if '_data0_' in run['file_path']:
                return run['file_path'].split('/')[2].rsplit('_data0_', 1)[0]
            else:
                raise ValueError(f"Unexpected file_path format: {run['file_path']}")
        return None

    def get_result(self, eventname, approx, label):
        run = self.get_run(eventname, approx, label)
        if run:
            return bilby.result.read_in_result(filename=run['file_path'])
        return None

    def get_posterior(self, eventname, approx, label):
        run = self.get_run(eventname, approx, label)
        if run:
            return bilby.result.read_in_result(filename=run['file_path']).posterior
        return None

    def get_config_path(self, eventname, approx, label):
        run = self.get_run(eventname, approx, label)
        file_base = self.get_result_file_base(eventname, approx, label)
        if run:
            return f'results/{run["eventname"]}/{file_base}_config_complete.ini'
        return None
    
    def get_recomputed_likelihood_path(self, data_dir, eventname, approx, label):
        return os.path.join(data_dir, f"{eventname}_{approx}_{label}_recomputed_likelihood.dat")
    
    def get_recomputed_likelihood(self, data_dir, eventname, approx, label):
        file_path = self.get_recomputed_likelihood_path(data_dir, eventname, approx, label)
        if os.path.exists(file_path):
            return np.loadtxt(file_path)
        return None
