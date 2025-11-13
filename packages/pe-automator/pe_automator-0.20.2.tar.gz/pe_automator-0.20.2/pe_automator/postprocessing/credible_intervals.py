from pe_automator.utils.io import read_samples
import numpy as np
from pesummary.utils.array import Array
from pe_automator.constants.approximants import PRECESSING_APPROXIMANTS, ECCENTRIC_APPROXIMANTS, PRECESSING_PARAMETERS, ECCENTRIC_PARAMETERS
from pesummary.gw.conversions import convert

def credible_intervals(samples):
    """
    Compute credible intervals for the given samples.
    """
    data = {}
    for event, models in samples.items():
        data[event] = {}
        for model, params in models.items():
            data[event][model] = {}
            for param, values in params.items():
                if values is None or len(values) == 0:
                    continue

                ci = values.credible_interval([5, 95])
                data[event][model][param] = {
                    "lower": ci[0],
                    "upper": ci[1],
                    "median": float(values.average("median"))
                }
    return data


def combine_samples(samples_list, parameters):
    combined_samples = {par: [] for par in parameters}
    all_wf_names = samples_list.keys()
    for par in parameters:
        if par in PRECESSING_PARAMETERS:
            wf_names = [wf for wf in all_wf_names if wf in PRECESSING_APPROXIMANTS]
        elif par in ECCENTRIC_PARAMETERS:
            wf_names = [wf for wf in all_wf_names if wf in ECCENTRIC_APPROXIMANTS]
        else:
            wf_names = list(all_wf_names)

        for wf in wf_names:
            combined_samples[par] = np.concatenate((combined_samples[par], samples_list[wf].get(par, [])))
        combined_samples[par] = Array(combined_samples[par])
    return combined_samples


def credible_intervals_from_data_dict(data_dict, parameters, eventnames):
    all_samples = {}

    # loop over eventname
    for eventname in eventnames:
        all_samples[eventname] = {}
        full_parameters = set(parameters)
        # loop over model/labels
        for model, file_path in data_dict[eventname].items():
            try:
                samples = read_samples(file_path, parameters)
                samples = {k: v for k, v in samples.items() if v.size > 0}
                all_samples[eventname][model] = convert(samples)

                if not hasattr(all_samples,'chi_1') and hasattr(all_samples,'spin_1z'):
                    all_samples[eventname][model]['chi_1'] = all_samples[eventname][model]['spin_1z']

                if not hasattr(all_samples,'chi_2') and hasattr(all_samples,'spin_2z'):
                    all_samples[eventname][model]['chi_2'] = all_samples[eventname][model]['spin_2z']

                full_parameters.update(all_samples[eventname][model].keys())
            except Exception as e:
                print(f"Error reading samples for {eventname} - {model}: {e}")
                raise e

        combined_samples = combine_samples(all_samples[eventname], full_parameters)
        all_samples[eventname]['Combined'] = combined_samples

    credible_intervals_dict = credible_intervals(all_samples)

    return credible_intervals_dict