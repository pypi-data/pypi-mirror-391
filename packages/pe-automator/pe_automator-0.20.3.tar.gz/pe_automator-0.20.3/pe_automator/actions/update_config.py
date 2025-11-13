from bilby_pipe.bilbyargparser import BilbyConfigFileParser
from bilby_pipe.utils import convert_prior_string_input, convert_string_to_dict
from pe_automator.utils.parse_config import clean_string_array, convert_dict_to_string
from jinja2 import Template


def update_config(config_file, template_file, label, approximant, eventname, slurm_extra_lines, 
                  scheduler_analysis_time, memory, priors=None, mode_array=None, dist_margin=None,
                  minimum_frequency=None, waveform_minimum_frequency=None, waveform_reference_frequency=None,
                  npoint=1000, naccept=60, maxmcmc=20000, nact=50, npool=128):
    """
    Update the configuration file with the provided patch file.

    :param config_file: Path to the original configuration file.
    :param patch_file: Path to the patch file containing updates.
    """
    parser = BilbyConfigFileParser()

    with open(config_file, 'r') as f:
        config = parser.parse(f)[0]

    with open(template_file, 'r') as f:
        template = Template(f.read())

    detectors = clean_string_array(config.get("detectors"))

    PhenomXPY_Models = ['IMRPhenomTEHM', 'IMRPhenomTHM_20', 'IMRPhenomTHM_20mem', 'IMRPhenomTHM_20osc', 'IMRPhenomTHM', 'IMRPhenomTPHM', 'IMRPhenomTPHM_20', 'IMRPhenomXE', 'IMRPhenomXAS'] 
    ALIGN_SPIN_MODELS = ['IMRPhenomXHM_NSBH', 'IMRPhenomTEHM', 'IMRPhenomTHM_20', 'IMRPhenomTHM_20mem', 'IMRPhenomTHM_20osc', 'IMRPhenomTHM', 'IMRPhenomXE', 'IMRPhenomXHM', 'IMRPhenomXAS']
    extra_likelihood_kwargs = None
    if approximant == 'IMRPhenomXHM_NSBH':
        extra_likelihood_kwargs = {"highest_mode": 4, "linear_interpolation": True} 

    ################ waveform name setup ###############
    waveform_name_used = approximant
    if approximant in ['IMRPhenomTHM_20', 'IMRPhenomTHM_20mem', 'IMRPhenomTHM_20osc']:
        waveform_name_used = 'IMRPhenomTHM'
    if approximant in ['IMRPhenomTPHM_lal', 'IMRPhenomTPHM_20']:
        waveform_name_used = 'IMRPhenomTPHM'

    ################ waveform generator setup ###############
    waveform_generator = 'bilby.gw.waveform_generator.LALCBCWaveformGenerator'
    if approximant in ['IMRPhenomXE', 'IMRPhenomTEHM']:
        waveform_generator = 'bilby.gw.waveform_generator.WaveformGenerator'
    # if approximant == 'IMRPhenomXHM_NSBH' or approximant == 'IMRPhenomXPNR':
    #     waveform_generator = 'bilby.gw.waveform_generator.LALCBCWaveformGenerator'
    # elif approximant == 'IMRPhenomTEHM' or approximant == 'IMRPhenomTHM_20':
    #     waveform_generator = 'bilby.gw.waveform_generator.LALCBCWaveformGenerator'

    waveform_arguments_dict = None
    if approximant == 'IMRPhenomTEHM':
        waveform_arguments_dict = {'rhs_eqs':'eob_phenomT', 'force_condition':False}
    elif approximant == 'IMRPhenomTHM_20':
        waveform_arguments_dict = {'add_20_mode':True, 'contr_20':'full'}
    elif approximant == 'IMRPhenomTHM_20mem':
        waveform_arguments_dict = {'add_20_mode':True, 'contr_20':'memory'}
    elif approximant == 'IMRPhenomTHM_20osc':
        waveform_arguments_dict = {'add_20_mode':True, 'contr_20':'oscillatory'}
    elif approximant == 'IMRPhenomXE':
        waveform_arguments_dict = {'N_harmonics':2,'rhs_eqs':'eob_phenomT'}
    elif approximant == 'IMRPhenomXPHM':
        waveform_arguments_dict = {'PhenomXHMReleaseVersion': 122022, 'PhenomXPFinalSpinMod': 2, 'PhenomXPrecVersion': 320}
    elif approximant == 'IMRPhenomTPHM':
        waveform_arguments_dict = {'prec_version': "numerical"}
    elif approximant == 'IMRPhenomTPHM_20':
        waveform_arguments_dict = {'prec_version': "numerical", 'add_20_mode': True, 'contr_20': 'full', 'mem_l2': True, 'numba_rotation': "custom_modes"}

    frequency_domain_source_model = 'lal_binary_black_hole'
    if approximant == 'IMRPhenomXHM_NSBH':
        frequency_domain_source_model = 'lal_binary_neutron_star'
    # for phenomxpy models
    elif approximant in PhenomXPY_Models:
        frequency_domain_source_model = 'phenomxpy.common.bilby_frequency_phenomxpy'

    conversion_function = None
    generation_function = None
    if approximant in PhenomXPY_Models:
        conversion_function = 'bilby.gw.conversion.convert_to_lal_binary_black_hole_parameters'
        generation_function = 'bilby.gw.conversion.generate_all_bbh_parameters'

    ############### mode_array setup ###############
    if mode_array:
        mode_array_input = mode_array
    else:
        mode_array_input = [None]
        # if approximant in ['IMRPhenomTHM_20', 'IMRPhenomTHM_20mem', 'IMRPhenomTHM_20osc', 'IMRPhenomTPHM_20']:
        #     mode_array_input = [[2, 2], [2, -2], [2, 1], [2, -1], [3, 3], [3, -3], [4, 4], [4, -4], [5, 5], [5, -5], [2, 0]]
        # if approximant in ['IMRPhenomTEHM', 'IMRPhenomTHM']:
        #     mode_array_input = [[2, 2], [2, 1], [3, 3], [4, 4], [5, 5], [2, -2], [2, -1], [3, -3], [4, -4], [5, -5]]

    ################ frequencies ###############
    if config['minimum-frequency'].startswith('{'):
        minimum_frequency_dict = convert_string_to_dict(config['minimum-frequency'])
    else:
        config_minimum_frequency = float(config['minimum-frequency'])
        minimum_frequency_dict = {d: config_minimum_frequency for d in detectors}
        minimum_frequency_dict['waveform'] = config_minimum_frequency

    # update the minimum frequency for the waveform if it is provided
    if waveform_minimum_frequency is not None:
        minimum_frequency_dict['waveform'] = waveform_minimum_frequency
    
    # update the minimum frequency for each detector if it is provided
    if minimum_frequency is not None:
        for key in minimum_frequency_dict:
            if key != 'waveform':
                minimum_frequency_dict[key] = minimum_frequency

    reference_frequency = config['reference-frequency']
    if waveform_reference_frequency is not None:
        reference_frequency = waveform_reference_frequency

    ############### prior_dict setup ###############
    print(config["prior-dict"])
    prior_dict = convert_prior_string_input(config["prior-dict"])
    # for aligned spin models, replace the spin parameters with chi_1 and chi_2
    if approximant in ALIGN_SPIN_MODELS:
        keys_to_remove_for_aligned_spin = ["a_1", "a_2", "tilt_1", "tilt_2", "phi_12", "phi_jl", "spin_1x", "spin_1y", "spin_2x", "spin_2y"]
        for key in keys_to_remove_for_aligned_spin:
            if key in prior_dict:
                del prior_dict[key]
        prior_dict['chi_1'] = "bilby.gw.prior.AlignedSpin(name='chi_1', a_prior=Uniform(minimum=0, maximum=0.99))"
        prior_dict['chi_2'] = "bilby.gw.prior.AlignedSpin(name='chi_2', a_prior=Uniform(minimum=0, maximum=0.99))"

    # for the waveform approximants using phenomxpy, set the eccentricity prior to zero if the waveform model does not support eccentricity
    if approximant in ['IMRPhenomTHM_20', 'IMRPhenomTHM_20mem', 'IMRPhenomTHM_20osc', 'IMRPhenomTHM', 'IMRPhenomTPHM', 'IMRPhenomTPHM_20', 'IMRPhenomXAS']:
        prior_dict['eccentricity'] = "0"
        prior_dict['mean_anomaly'] = "0"

    # other changes required for specific approximants
    if approximant in ['IMRPhenomTEHM', 'IMRPhenomXE']:
        prior_dict['eccentricity'] = "Uniform(name='eccentricity', latex_label='$e$', minimum=0, maximum=0.65)"
        prior_dict['mean_anomaly'] = "Uniform(minimum=0, maximum=6.283185307179586, name='mean_anomaly', latex_label='$l_0$', unit=None, boundary='periodic')"
    
    if approximant == 'IMRPhenomXHM_NSBH':
        prior_dict['chirp_mass'] = "bilby.gw.prior.UniformInComponentsChirpMass(name='chirp_mass', minimum=1.45, maximum=9, latex_label='$\\mathcal{M}$', unit='$M_{\\odot}$', boundary=None)"
        prior_dict['mass_1'] = "Constraint(name='mass_1', minimum=3.0, maximum=50.0, latex_label='$m_{1}$', unit=None)"
        prior_dict['mass_2'] = "Constraint(name='mass_2', minimum=1.0, maximum=3.0, latex_label='$m_{2}$', unit=None)"
        prior_dict['chi_2'] = "bilby.gw.prior.AlignedSpin(a_prior=Uniform(name=None, minimum=0, maximum=0.05, latex_label=None, unit=None, boundary=None), z_prior=Uniform(name=None, minimum=-1, maximum=1, latex_label=None, unit=None, boundary=None), name='chi_2', latex_label='$\\chi_2$', unit=None, boundary=None)"
        prior_dict['luminosity_distance'] = "PowerLaw(alpha=2, name='luminosity_distance', minimum=10, maximum=1000, unit='Mpc')"
        prior_dict['lambda_1'] = "0"
        prior_dict['lambda_2'] = "Uniform(name='lambda_2', latex_label='$\lambda_2$', minimum=0, maximum=5000)"    

    # overwrite the default prior if a custom prior is provided
    if priors is not None:
        priors = convert_prior_string_input(priors)
        for key in priors:
            if key in prior_dict:
                prior_dict[key] = priors[key]
            else:
                print(f"Warning: Prior {key} not found in the default prior dictionary. Adding it.")
                prior_dict[key] = priors[key]

    default_prior = 'BBHPriorDict'
    if approximant in ['IMRPhenomXHM_NSBH']:
        default_prior = 'BNSPriorDict'

    ################ likelihood type setup ###############
    likelihood_type = config.get("likelihood-type", "GravitationalWaveTransient")
    if approximant in ['IMRPhenomXHM_NSBH']:
        likelihood_type = 'MBGravitationalWaveTransient'

    ################# marginalization setup ###############

    distance_marginalization = config['distance-marginalization']
    # if approximant in ['IMRPhenomTHM_20', 'IMRPhenomTHM_20mem', 'IMRPhenomTHM_20osc', 'IMRPhenomTPHM_20']:
    #     distance_marginalization = False

    if dist_margin is not None:
        distance_marginalization = dist_margin


    ################ local files ###############
    data_dict = {d: f'./framefiles/{eventname}_{d}.gwf' for d in detectors}
    psd_dict = {d: f'./psds/{eventname}_{d}_psd.txt' for d in detectors}
    spline_calibration_envelope_dict = {d: f'./spline_cal_envs/{eventname}_{d}_spline_cal_env.txt' for d in detectors}

    rendered = template.render(
        trigger_time=config.get("trigger-time"),
        detectors=detectors,
        data_dict=data_dict,
        channel_dict=config["channel-dict"],
        duration=config['duration'],
        post_trigger_duration=config['post-trigger-duration'],
        psd_dict=psd_dict,
        psd_fractional_overlap=config['psd-fractional-overlap'],
        psd_length=config['psd-length'],
        psd_maximum_duration=config['psd-maximum-duration'],
        psd_method=config['psd-method'],
        minimum_frequency=minimum_frequency_dict,
        maximum_frequency=config['maximum-frequency'],
        sampling_frequency=config['sampling-frequency'],
        tukey_roll_off=config['tukey-roll-off'],
        default_prior=default_prior,
        deltaT=config['deltaT'],
        prior_file=None,
        prior_dict=convert_dict_to_string(prior_dict),
        enforce_signal_duration=config.get('enforce-signal-duration', False),
        reference_frame=config['reference-frame'],
        time_reference=config['time-reference'],
        calibration_marginalization=config.get('calibration-marginalization', False),
        calibration_model=config['calibration-model'],
        calibration_prior_boundary=config.get('calibration-prior-boundary', 'reflective'),
        calibration_correction_type=config.get('calibration-correction-type', 'data'),
        spline_calibration_envelope_dict=spline_calibration_envelope_dict,
        spline_calibration_nodes=config['spline-calibration-nodes'],
        distance_marginalization=distance_marginalization,
        phase_marginalization=config['phase-marginalization'],
        time_marginalization=config['time-marginalization'],
        likelihood_type=likelihood_type,
        extra_likelihood_kwargs=extra_likelihood_kwargs,
        sampler_kwargs={'nlive': npoint, 'naccept': naccept, 'sample': 'acceptance-walk', 'walks': 100, 'npool': npool, 
                        'nact': nact, 'maxmcmc': maxmcmc, 
                        'check_point': True, 'check_point_plot': True, 
                        'check_point_delta_t': 3600, 'print_method': 'interval-60'},
        waveform_generator=waveform_generator,
        reference_frequency=reference_frequency,
        waveform_approximant=waveform_name_used,
        waveform_arguments_dict=waveform_arguments_dict,
        mode_array=mode_array_input,
        frequency_domain_source_model=frequency_domain_source_model,
        conversion_function=conversion_function,
        generation_function=generation_function,
        slurm_extra_lines=slurm_extra_lines,
        scheduler_analysis_time=scheduler_analysis_time,
        memory=memory,
        label=label,
        request_cpus=npool,
        outdir=f"runs/{label}",
    )

    files_to_copy = {
        'data_dict': [f for f in data_dict.values()],
        'psd_dict': [f for f in psd_dict.values()],
        'spline_calibration_envelope_dict': [f for f in spline_calibration_envelope_dict.values()],
    }

    return rendered, files_to_copy