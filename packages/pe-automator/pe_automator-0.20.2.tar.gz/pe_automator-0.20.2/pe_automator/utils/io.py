import pandas as pd
import h5py
import numpy as np
from pesummary.utils.array import Array


def read_samples(model_file, param_keys):
    """
    Read samples from a model file, which can be either a uib hdf5 file or a gwtc hdf5 file.
    """
    if isinstance(param_keys, str):
        return_one = True
        param_keys = [param_keys]
    else:
        return_one = False

    samples = {}
    if type(model_file) == str:
        # read the uib hdf5 file
        file_path = model_file
        hdf5_group = 'posterior'
        with h5py.File(file_path, 'r') as f:
            # posterior_keys = list(f['posterior'].keys())
            # print(f"\nPosterior keys for model '{model}':\n{posterior_keys}\n")
            for param_key in param_keys:
                if f'{hdf5_group}/{param_key}' in f:
                    samples[param_key] = f[f'{hdf5_group}/{param_key}'][:]
                else:
                    # print(f"Parameter {param_key} not found in {file_path}. Setting to None.")
                    samples[param_key] = np.array([])
                    # samples[param_key] = None
    else:
        # read the gwtc hdf5 file
        file_path = model_file['filename']
        posterior_samples = pd.read_hdf(file_path, key=f"{model_file['run_name']}/posterior_samples")
        for param_key in param_keys:
            if param_key in posterior_samples:
                samples[param_key] = posterior_samples[param_key].values
            # else:
            #     # print(f"Parameter {param_key} not found in {file_path}. Setting to None.")
            #     samples[param_key] = np.array([])
            #     # samples[param_key] = None

    for key in samples:
        samples[key] = Array(samples[key])

    if return_one and len(samples) == 1:
        return samples[param_keys[0]]
    else:
        return samples