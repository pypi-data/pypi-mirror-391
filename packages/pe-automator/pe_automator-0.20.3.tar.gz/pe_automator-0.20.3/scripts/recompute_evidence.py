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
from bilby.core.result import reweight
import json

results_dir = 'results'

def main(results_dir, original_loglikelihood_dir, new_loglikelihood_dir, save_to=None):
    results_catalog = read_results_catalog(results_dir)
    # wf_model_ready_to_process = ['IMRPhenomXPNR', 'IMRPhenomXPHM', 'IMRPhenomTPHM_lal']
    wf_model_ready_to_process = ['IMRPhenomXPNR', 'IMRPhenomXPHM', 'IMRPhenomTPHM_lal', 
                                    'IMRPhenomTHM', 'IMRPhenomXE', 'IMRPhenomXHM',
                                    'IMRPhenomTPHM', 'IMRPhenomTEHM']
    new_evidences = {}
    for eventname in tqdm(results_catalog, desc="Processing events"):
        new_evidences[eventname] = {}
        for run in tqdm(results_catalog[eventname], desc=f"Processing {eventname}", leave=False):
            is_od_run = run['run_label'].startswith('OD') and not run['run_label'].startswith('OD16k')
            is_target_approximant = run['approximant'] in wf_model_ready_to_process
            if run['approximant'] not in new_evidences[eventname]:
                new_evidences[eventname][run['approximant']] = {}
            if is_od_run and is_target_approximant:
                recomputed_likelihoods_org = results_catalog.get_recomputed_likelihood(original_loglikelihood_dir, eventname, run['approximant'], run['run_label'])
                recomputed_likelihoods_new = results_catalog.get_recomputed_likelihood(new_loglikelihood_dir, eventname, run['approximant'], run['run_label'])
                if recomputed_likelihoods_org is None or recomputed_likelihoods_new is None:
                    print(f"Recomputed likelihoods not found for {eventname}, {run['approximant']}, {run['run_label']}. Skipping.")
                    continue
                print(f"Recomputing evidence for {eventname}, {run['approximant']}, {run['run_label']}")
                result = results_catalog.get_result(eventname, run['approximant'], run['run_label'])
                previous_log_evidence = result.log_evidence
                result.posterior['log_likelihood'] = recomputed_likelihoods_org
                reweighted_result = reweight(result, new_likelihood=recomputed_likelihoods_new)
                print(f"Event: {eventname}, Approximant: {run['approximant']}, Run label: {run['run_label']}")
                print(f"    Previous evidence: {previous_log_evidence:.2f}")
                print(f"  Recomputed evidence: {reweighted_result.log_evidence:.2f}")
                new_evidences[eventname][run['approximant']][run['run_label']] = reweighted_result.log_evidence

    # save new evidences to a json file
    if save_to:
        with open(save_to, 'w') as f:
            json.dump(new_evidences, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recompute evidences for GW events using new likelihoods.")
    parser.add_argument('--results_dir', '-r', type=str, default='results', help='Directory containing the results catalog')
    parser.add_argument('--original_loglikelihood_dir', '-o', type=str, required=True, help='Directory containing the original recomputed likelihood files')
    parser.add_argument('--new_loglikelihood_dir', '-n', type=str, required=True, help='Directory containing the new recomputed likelihood files')
    parser.add_argument('--save_to', '-s', type=str, default='new_evidences.json', help='Path to save the new evidences JSON file')
    args = parser.parse_args()

    main(args.results_dir, args.original_loglikelihood_dir, args.new_loglikelihood_dir, save_to=args.save_to)
