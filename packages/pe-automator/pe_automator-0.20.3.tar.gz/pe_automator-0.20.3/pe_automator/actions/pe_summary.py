import os
import datetime

def check_summary_exists(event_summary_dir: str) -> bool:
    # check if the summary file exists for the given event
    return os.path.isdir(event_summary_dir)


def check_if_posterior_exists(event_summary_dir: str, label: str) -> bool:
    # check if the posterior file exists for the given event
    event_posterior_file = os.path.join(event_summary_dir, "config", f"{label}_config.ini")
    return os.path.isfile(event_posterior_file)


def generate_label(run_info: dict) -> str:
    # Generate a label for the given run information
    label = f"{run_info['approximant']}_{run_info['run_label']}"
    return label


def get_summary_command(runs: list, labels: list, event_summary_dir: str) -> str:
    # Generate the summary command for the given event
    # summarypages --webdir plots/pe_summary/GW230709_122727 --existing_webdir plots/pe_summary/GW230709_122727 --add_to_existing --samples results/GW230709_122727/Sparrow_IMRPhenomTEHM_test_cat0_ext_prior_20250804_data0_1372940865-202158_analysis_H1L1_merge_result.hdf5 results/GW230709_122727/Sparrow_IMRPhenomXE_test_xe_1_20250814_data0_1372940865-202158_analysis_H1L1_merge_result.hdf5 results/GW230709_122727/Sparrow_IMRPhenomXPNR_test_cat0_1_20250728_data0_1372940865-202158_analysis_H1L1_merge_result.hdf5  --gw --multi_process 4 --disable_expert --disable_interactive --no_ligo_skymap --labels IMRPhenomTEHM_test_cat0 IMRPhenomXE_test_xe_1 IMRPhenomXPNR_test_cat0_1
    existing_option = ''
    if check_summary_exists(event_summary_dir):
        existing_option = f"--existing_webdir {event_summary_dir} --add_to_existing"
    command = f"summarypages --webdir {event_summary_dir} {existing_option} --samples {' '.join(runs)} --labels {' '.join(labels)} --gw --multi_process 4 --disable_expert --disable_interactive --no_ligo_skymap"
    return command


def generate_summary_command(eventname: str, event_entry: list, summary_folder: str) -> str:
    print(f"Generating summary command for event: {eventname}")
    # get the latest entry for each approximant
    approximants = set([run_info['approximant'] for run_info in event_entry])
    event_summary_dir = os.path.join(summary_folder, eventname)

    runs_tba = []
    labels_tba = []

    for approximant in approximants:
        latest_run = max(
            (run_info for run_info in event_entry if run_info['approximant'] == approximant),
            key=lambda x: datetime.datetime.fromisoformat(x['created_at'].replace("Z", "+00:00")),
            default=None
        )

        if not latest_run:
            continue

        label = generate_label(latest_run)

        if not check_if_posterior_exists(event_summary_dir, label):
            runs_tba.append(latest_run['file_path'])
            labels_tba.append(label)
        else:
            print(f"Posterior for {label} already exists, skipping.")

    if not runs_tba:
        return ''
    
    print(f"Runs to be added: {labels_tba}")

    summary_command = get_summary_command(runs_tba, labels_tba, event_summary_dir)
    return summary_command
