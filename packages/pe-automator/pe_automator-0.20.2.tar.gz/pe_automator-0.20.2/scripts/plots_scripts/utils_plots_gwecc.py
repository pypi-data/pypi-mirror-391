
import os, glob, json
import numpy as np


import warnings
warnings.filterwarnings("ignore", "Wswiglal-redir-stdio")
import bilby

import matplotlib.pyplot as plt

def gwecc_TEHM_comparison_v2(res_dir:str, gw_ecc_dir:str, event:str):
    """
    Compare eccentricity samples from a gw_eccentricity and a Bilby TEHM runs.
    
    Parameters
    ----------
    dat_file : str
        Path to the .dat file produced by gw_eccentricity.
    hdf5_file : str
        Path to the Bilby .hdf5 result file produced by our run.
    """ 
    
    # Read gw_eccentricity postprocessed file
    gw_ecc_files = glob.glob(gw_ecc_dir+f'{event}/*json')

    # Check if gw_ecc file exist
    if len(gw_ecc_files)==0:
        raise ValueError(f"No gw eccentricity file for {event}")

    elif len(gw_ecc_files)>1: 
        raise ValueError(f"Multiple gw eccentricity files  = {gw_ecc_files} for {event}")

    else:
        gw_ecc_file = gw_ecc_files[0]

    basename = os.path.basename(gw_ecc_file)
    string_event = basename.split('_result')[0]

    # Read the corresponding posterior file
    res_files = glob.glob(res_dir+f"{event}/{string_event}*")

    # Perform some checks on the file
    if len(res_files)==0:
        raise ValueError(f"No res file for {event}")

    elif len(res_files)>1: 
        raise ValueError(f"Multiple posterior files  = {res_files} for {event}")

    else:
        res_file = res_files[0]
        
    ##########################################################
    
    # Read Bilby result
    result = bilby.result.read_in_result(res_file)
    posterior = result.posterior
    
    # Read gw_eccentricity file
    
    print(f"gw_ecc_file = {gw_ecc_file}")
    with open(gw_ecc_file) as json_data:
        result_gw_ecc = json.load(json_data)
    
    len_pe_samples = len(posterior['total_mass'])
    print('Number of samples from PE: ', len_pe_samples)

    #df0 = df0.where(df0 >= 0, np.nan)
    #samples = df0['eccentricity'].dropna().tolist()
    egw = np.array(result_gw_ecc['ew22_posterior'])
    lgw = np.array(result_gw_ecc[ 'meanAno22_posterior'] )
                        
    idx_bo = np.where(egw !=-1)[0]
    egw = egw[idx_bo]
    lgw = lgw[idx_bo]
    
    len_egw = len(egw)
    print('Number of samples in gw_eccentricity: ', len_egw)

    frac_survived = len_egw/len_pe_samples
    frac_dropped = 1 - frac_survived

    if frac_survived < 0.75:
        print(f"Warning: {frac_dropped*100:.1f}% of samples were dropped, do not trust the gw_eccentricity posterior.")

    plt.hist(posterior['eccentricity'], bins=60, density=True, histtype='step', lw=1.5, color='tomato', label='Bilby run TEHM')
    plt.hist(egw, bins=60, density=True, histtype='step', lw=1.5, color='mediumseagreen', label='gw_eccentricity')
    plt.xlabel("$e$", fontsize=16)
    plt.legend()
    plt.show()
    
    plt.hist(posterior['mean_anomaly'], bins=60, density=True, histtype='step', lw=1.5, color='tomato', label='Bilby run TEHM')
    plt.hist(lgw, bins=60, density=True, histtype='step', lw=1.5, color='mediumseagreen', label='gw_eccentricity')
    plt.xlabel("$l$", fontsize=16)
    plt.legend()
    plt.show()
    
    return

