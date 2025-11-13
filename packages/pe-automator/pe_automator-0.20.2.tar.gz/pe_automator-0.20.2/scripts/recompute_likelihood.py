from pe_automator.postprocessing.jobs import read_results_catalog
import os
import tempfile
import shutil
import numpy as np
import os
import bilby
from bilby_pipe.utils import parse_args
from bilby_pipe.data_analysis import create_analysis_parser, DataAnalysisInput
from bilby_pipe.data_generation import create_generation_parser, DataGenerationInput
from bilby.core.sampler import get_sampler_class
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm


def generate_bilby_dump(config):
    args, unknown_args = parse_args([config], create_generation_parser())
    data = DataGenerationInput(args, unknown_args)
    data.save_data_dump()
    dump_file = os.path.join(data.data_directory, "_".join([data.label, "data_dump.pickle"]))
    print(f'Data dump saved to {dump_file}')
    return dump_file


def recompute_log_likelihood(bilby_dump_file, config, result_file, save_to=None):
    arg_string = f'{config} --data-dump-file {bilby_dump_file} --label bilby_mannual --sampling-seed 1 --sampler dynesty'

    args, unknown_args = parse_args(
            arg_string.split(),
            create_analysis_parser(usage=__doc__),
        )

    analysis = DataAnalysisInput(args, unknown_args)

    likelihood, priors = analysis.get_likelihood_and_priors()

    priors.fill_priors(likelihood, default_priors_file=None)

    sampler_class = get_sampler_class(analysis.sampler)

    sampler = sampler_class(
        likelihood,
        priors=priors,
        outdir=analysis.outdir,
        label=analysis.label,
        injection_parameters=None,
        meta_data=analysis.meta_data,
        result_class=analysis.result_class,
        conversion_function=analysis.parameter_generation,
        **analysis.sampler_kwargs,
    )

    sampler._set_sampling_method()

    sampler.kwargs["live_points"] = sampler.get_initial_points_from_prior(
                        sampler.nlive
                    )
    # sampler.use_ratio = True

    result = bilby.result.read_in_result(filename=result_file)

    log_likelihood = []
    for index, row in result.posterior.iterrows():
        if index % 3000 == 0:
            print(f'Processing row {index}')
        theta = [row[key] for key in sampler._search_parameter_keys]
        log_l = sampler.log_likelihood(theta)
        log_likelihood.append(log_l)
        
    log_likelihood = np.array(log_likelihood)
    if save_to is not None:
        np.savetxt(save_to, log_likelihood)
        print(f'Log likelihoods saved to {save_to}')

    return log_likelihood


def recompute_likelihood_worker(eventname, run, config_file, data_dir, output_dir):
    # print(f"Worker started for {eventname} with {run['approximant']} and label {run['run_label']}")
    recomputed_likelihood_file = os.path.join(output_dir, f"{eventname}_{run['approximant']}_{run['run_label']}_recomputed_likelihood.dat")
    if recomputed_likelihood_file is None:
        raise ValueError(f"Could not determine recomputed likelihood file path for {eventname} with {run['approximant']} and label {run['run_label']}.")
    
    # test if the config file exists
    if not os.path.isfile(config_file):
        print(f"Config file {config_file} does not exist. Skipping.")
        return
    if os.path.isfile(recomputed_likelihood_file):
        print(f"Recomputed likelihood file {recomputed_likelihood_file} exists. Skipping.")
        return

    print(f"Processing {eventname} with {run['approximant']} and label {run['run_label']}")

    with tempfile.TemporaryDirectory() as tmpdirname:
        # copy the config file to the temporary directory
        tmp_config_file = os.path.join(tmpdirname, os.path.basename(config_file))
        # rewrite the line outdir= to outdir=outputs
        with open(config_file, 'r') as f:
            lines = f.readlines()
        with open(tmp_config_file, 'w') as f:
            for line in lines:
                if line.startswith('outdir='):
                    f.write('outdir=outputs\n')
                elif line.startswith('mode-array=') or line.startswith('mode_array='):
                    f.write('mode-array=[None]\n')
                else:
                    f.write(line)
        # find data_dir/psds/eventname_* and copy to tmpdirname
        os.mkdir(os.path.join(tmpdirname, 'psds'))
        os.mkdir(os.path.join(tmpdirname, 'framefiles'))
        os.mkdir(os.path.join(tmpdirname, 'spline_cal_envs'))
        psd_files = [os.path.join('psds', f) for f in os.listdir(os.path.join(data_dir, 'psds')) if f.startswith(eventname)]
        frame_files = [os.path.join('framefiles', f) for f in os.listdir(os.path.join(data_dir, 'framefiles')) if f.startswith(eventname)]
        spline_cal_env_files = [os.path.join('spline_cal_envs', f) for f in os.listdir(os.path.join(data_dir, 'spline_cal_envs')) if f.startswith(eventname)]
        files_to_copy = psd_files + frame_files + spline_cal_env_files
        for f in files_to_copy:
            source_path = os.path.join(data_dir, f)
            dest_path = os.path.join(tmpdirname, f)
            print(f"Copying {source_path} to {dest_path}")
            shutil.copy(source_path, dest_path)
        
        pwd = os.getcwd()
        os.chdir(tmpdirname)
        try:
            dump_file = generate_bilby_dump(tmp_config_file)
        except Exception as e:
            print(f"Error occurred while generating bilby dump: {e}")
            return
        finally:
            os.chdir(pwd)

        dump_file = os.path.join(tmpdirname, dump_file)
        if not os.path.isfile(dump_file):
            print(f"Dump file {dump_file} does not exist. Skipping recompute.")
            return

        recompute_log_likelihood(dump_file, tmp_config_file, run['file_path'], save_to=recomputed_likelihood_file)


def recompute_likelihood_all(results_dir, data_dir, output_dir, n_processes=1):
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    results_catalog = read_results_catalog(results_dir)
    # wf_model_ready_to_process = ['IMRPhenomXPNR', 'IMRPhenomXPHM', 'IMRPhenomTPHM_lal']
    wf_model_ready_to_process = ['IMRPhenomXPNR', 'IMRPhenomXPHM', 'IMRPhenomTPHM_lal', 
                                 'IMRPhenomTHM', 'IMRPhenomXE', 'IMRPhenomXHM',
                                 'IMRPhenomTPHM', 'IMRPhenomTEHM']

    futures = []
    with ProcessPoolExecutor(max_workers=n_processes) as executor:
        for eventname in results_catalog:
            for run in results_catalog[eventname]:
                is_od_run = run['run_label'].startswith('OD') and not run['run_label'].startswith('OD16k')
                is_target_approximant = run['approximant'] in wf_model_ready_to_process
                if is_od_run and is_target_approximant:
                    config_file = results_catalog.get_config_path(eventname, run['approximant'], run['run_label'])
                    futures.append(
                        executor.submit(recompute_likelihood_worker, eventname, run, config_file, data_dir, output_dir)
                    )

        # progress bar over all submitted futures
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing events"):
            try:
                future.result()   # raises exception if worker failed
            except Exception as e:
                print(f"[MAIN] Worker failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Recompute likelihoods for GW events.")
    parser.add_argument('--results', '-r', type=str, required=True, help='Directory containing the results catalog.')
    parser.add_argument('--data', '-d', type=str, required=True, help='Directory containing the data files (psds, framefiles, spline_cal_envs).')
    parser.add_argument('--output', '-o', type=str, default='recomputed_likelihoods', help='Directory to save recomputed likelihood files.')
    parser.add_argument('--n-processes', '-n', type=int, default=1, help='Number of parallel processes to use.')
    args = parser.parse_args()

    recompute_likelihood_all(args.results, args.data, args.output, n_processes=args.n_processes)


if __name__ == "__main__":
    main()