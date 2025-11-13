from pe_automator.postprocessing.plots import js_divergence_plot, posteriors_1d
from pe_automator.postprocessing.jobs import get_full_eventnames, read_results_catalog, get_gwtc_hdf5_filename
from pe_automator.postprocessing.credible_intervals import credible_intervals_from_data_dict
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import json
from pe_automator.actions.pe_summary import generate_summary_command
import subprocess


special_runs = {
    'GW250114_082203': 'bilby-IMRPhenomXPHM-SpinTaylor_prod-reweighted',
}


def post_process(results_dir, data_dir, gwtc_dir, output_dir):
    """
    Post-process the results from the parameter estimation.
    """

    # Set font for the plots
    mpl.font_manager.fontManager.addfont(os.path.join(data_dir, "cmunrm.otf"))
    plt.rcParams.update({"font.family": "CMU Serif", "mathtext.fontset": "cm"})
    plt.rcParams['font.size'] = 16

    results_catalog = read_results_catalog(results_dir)
    pe_file_dict_latest = get_latest_runs_dict(results_catalog, gwtc_dir)
    eventnames = sorted(get_full_eventnames(data_dir))

    ##########  credible intervals ############
    print(f"Processing credible intervals for events")
    parameters = ['total_mass', 'chirp_mass', 'mass_ratio', 
                  'chi_1', 'chi_2', 'tilt_1', 'tilt_2', 'a_1', 'a_2',
                  'luminosity_distance', 'chi_eff', 'chi_p', 'theta_jn',
                  'eccentricity', 'mean_anomaly', 'H1_optimal_snr', 'L1_optimal_snr']

    try:
        credible_intervals_dict = credible_intervals_from_data_dict(pe_file_dict_latest, parameters, eventnames)
        with open(os.path.join(output_dir, 'credible_intervals.json'), 'w') as f:
            json.dump(credible_intervals_dict, f, indent=4)
    except Exception as e:
        print(f"Error occurred while calculating credible intervals: {e}")

    ##########  1d posterior plots ############
    print(f"Processing 1D posterior plots for events")
    parameters = {
        'total_mass': r"$M\ [M_\odot]$",
        'chirp_mass': r"$\mathcal{M}\ [M_\odot]$",
        'mass_ratio': r"$q$",
        # 'a_1': r"$\chi_1$",
        # 'a_2': r"$\chi_2$",
        # 'tilt_1': r"$\theta_1\ [\mathrm{rad}]$",
        # 'tilt_2': r"$\theta_2\ [\mathrm{rad}]$",
        'chi_eff': r"$\chi_{\mathrm{eff}}$",
        'chi_p': r"$\chi_{\mathrm{p}}$",
        # 'luminosity_distance': r"$D_L$[Mpc]",
        'eccentricity': r"$e$",
        # 'mean_anomaly': r"$l$",
        'H1_optimal_snr': r"$\mathrm{SNR}_{\mathrm{H1}}$",
        'L1_optimal_snr': r"$\mathrm{SNR}_{\mathrm{L1}}$"
    }

    try:
        posteriors_1d(pe_file_dict_latest, parameters, output_dir + '/posteriors_1d.png', eventnames=eventnames)
    except Exception as e:
        print(f"Error occurred while plotting 1D posteriors: {e}")
    # GWTC_1d_posterior_plot(data_dir, parameters, gwtc_dir, output_dir + '/posteriors_1d_GWTC.png')

    try:
        production_1d_posterior_plot(data_dir, parameters, results_catalog, gwtc_dir, output_dir + '/posteriors_1d_production.png')
    except Exception as e:
        print(f"Error occurred while plotting production 1D posteriors: {e}")
    try:
        test_1d_posterior_plot(data_dir, parameters, results_catalog, gwtc_dir, output_dir + '/posteriors_1d_test.png')
    except Exception as e:
        print(f"Error occurred while plotting test 1D posteriors: {e}")

    ############ JS Divergence Plots ############

    # Choose the parameters you want to plot here
    parameters = {
        'total_mass': r"$M$",
        'mass_ratio': r"$q$",
        'mass_1': r"$m_1$",
        'mass_2': r"$m_2$",
        'luminosity_distance': r"$D_L$",
        'theta_jn': r"$\theta_{\mathrm{JN}}$"
    }

    model_pairs = [('GWTC', 'IMRPhenomTEHM'), ('GWTC', 'IMRPhenomTHM_20'), ('GWTC', 'IMRPhenomXPNR'), ('IMRPhenomTEHM', 'IMRPhenomTHM_20'), ('IMRPhenomTEHM', 'IMRPhenomXPNR'), ('IMRPhenomTHM_20', 'IMRPhenomXPNR')]

    try:
        js_divergence_plot(pe_file_dict_latest, parameters, output_dir, eventnames=eventnames, model_pairs=model_pairs)
    except Exception as e:
        print(f"Error occurred while plotting JS divergence: {e}")

    ########### PE Summary ###########
    catalog_file = 'results/results_catalog.json'

    with open(catalog_file, 'r') as f:
        catalog = json.load(f)

    for eventname, runs in catalog.items():
        command = generate_summary_command(eventname, runs, 'plots/pesummary')
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running command for {eventname}: {e}")


def get_latest_runs_dict(results_catalog, gwtc_dir):
    pe_file_dict_latest = {}
    for eventname, runs in results_catalog.items():
        waveform_models = set([run['approximant'] for run in runs])
        if eventname not in pe_file_dict_latest:
            pe_file_dict_latest[eventname] = {}
        for model in waveform_models:
            # use ODProd runs if available, otherwise fall back to all runs
            wf_runs = [run for run in runs if run['approximant'] == model and run['run_label'].startswith('ODProd')]
            if not wf_runs:
                wf_runs = [run for run in runs if run['approximant'] == model]
            # find the latest run
            latest_run = max(wf_runs, key=lambda x: datetime.datetime.strptime(x['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'))
            pe_file_dict_latest[eventname][model] = latest_run['file_path']
            if len(wf_runs) > 1:
                print(f"Multiple runs found for {eventname} with model {model}. Using the latest run: {latest_run['run_label']}")

    for eventname, runs in get_gwtc_hdf5_filename(gwtc_dir, 'C00:Mixed', special_runs).items():
        if eventname not in pe_file_dict_latest:
            pe_file_dict_latest[eventname] = {}
        pe_file_dict_latest[eventname]['GWTC'] = runs

    return pe_file_dict_latest


def GWTC_1d_posterior_plot(data_dir, parameters, gwtc_dir, filename):
    pe_file_dict = {}

    for eventname, runs in get_gwtc_hdf5_filename(gwtc_dir, 'C00:IMRPhenomXPHM-SpinTaylor', special_runs).items():
        if eventname not in pe_file_dict:
            pe_file_dict[eventname] = {}
        pe_file_dict[eventname]['GWTC-XPHM'] = runs

    for eventname, runs in get_gwtc_hdf5_filename(gwtc_dir, 'C00:Mixed', special_runs).items():
        if eventname not in pe_file_dict:
            pe_file_dict[eventname] = {}
        pe_file_dict[eventname]['GWTC-Mixed'] = runs

    for eventname, runs in get_gwtc_hdf5_filename(gwtc_dir, 'C00:SEOBNRv5PHM', special_runs).items():
        if eventname not in pe_file_dict:
            pe_file_dict[eventname] = {}
        pe_file_dict[eventname]['GWTC-SEOB'] = runs

    for eventname, runs in get_gwtc_hdf5_filename(gwtc_dir, 'C00:IMRPhenomXO4a', special_runs).items():
        if eventname not in pe_file_dict:
            pe_file_dict[eventname] = {}
        pe_file_dict[eventname]['GWTC-XO4a'] = runs

    for eventname, runs in get_gwtc_hdf5_filename(gwtc_dir, 'C00:NRSur7dq4', special_runs).items():
        if eventname not in pe_file_dict:
            pe_file_dict[eventname] = {}
        pe_file_dict[eventname]['GWTC-NRSur'] = runs

    for eventname, runs in get_gwtc_hdf5_filename(gwtc_dir, 'C00:Mixed+XO4a', special_runs).items():
        if eventname not in pe_file_dict:
            pe_file_dict[eventname] = {}
        pe_file_dict[eventname]['GWTC-Mixed+XO4a'] = runs
        
    eventnames = sorted(get_full_eventnames(data_dir))

    posteriors_1d(pe_file_dict, parameters, filename, eventnames=eventnames)


def production_1d_posterior_plot(data_dir, parameters, results_catalog, gwtc_dir, filename):
    pe_file_dict_prod = {}

    for eventname, runs in results_catalog.items():
        waveform_models = set([run['approximant'] for run in runs])
        if eventname not in pe_file_dict_prod:
            pe_file_dict_prod[eventname] = {}

        for model in waveform_models:
            # here you can filter the labels start with 'ODProd'
            wf_runs = [run for run in runs if run['approximant'] == model and run['run_label'].startswith('ODProd')]

            if wf_runs:
                latest_run = max(wf_runs, key=lambda x: datetime.datetime.strptime(x['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'))

                pe_file_dict_prod[eventname][model] = latest_run['file_path']

                if len(wf_runs) > 1:
                    print(f"Multiple runs found for {eventname} with model {model}. Using the latest run: {latest_run['run_label']}")

    for eventname, runs in get_gwtc_hdf5_filename(gwtc_dir, 'C00:Mixed', special_runs).items():
        if eventname not in pe_file_dict_prod:
            pe_file_dict_prod[eventname] = {}
        pe_file_dict_prod[eventname]['GWTC'] = runs

    eventnames = sorted(get_full_eventnames(data_dir))
    posteriors_1d(pe_file_dict_prod, parameters, filename, eventnames=eventnames)


def test_1d_posterior_plot(data_dir, parameters, results_catalog, gwtc_dir, filename):
    pe_file_dict_test = {}

    for eventname, runs in results_catalog.items():
        waveform_models = set([run['approximant'] for run in runs])
        if eventname not in pe_file_dict_test:
            pe_file_dict_test[eventname] = {}

        for model in waveform_models:
            # here you can filter the labels start with 'ODProd'
            wf_runs = [run for run in runs if run['approximant'] == model and 'PROD' not in run['run_label'].upper()]

            if wf_runs:
                latest_run = max(wf_runs, key=lambda x: datetime.datetime.strptime(x['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'))

                pe_file_dict_test[eventname][model] = latest_run['file_path']

                if len(wf_runs) > 1:
                    print(f"Multiple runs found for {eventname} with model {model}. Using the latest run: {latest_run['run_label']}")

    for eventname, runs in get_gwtc_hdf5_filename(gwtc_dir, 'C00:Mixed', special_runs).items():
        if eventname not in pe_file_dict_test:
            pe_file_dict_test[eventname] = {}
        pe_file_dict_test[eventname]['GWTC'] = runs

    eventnames = sorted(get_full_eventnames(data_dir))
    posteriors_1d(pe_file_dict_test, parameters, filename, eventnames=eventnames)
