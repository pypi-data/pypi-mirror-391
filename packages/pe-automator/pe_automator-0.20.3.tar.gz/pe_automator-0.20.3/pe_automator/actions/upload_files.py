import os
import shutil


def upload_files(remote, remote_path, event_name, config, psds, calibration_envelopes, framefiles):
    """
    Upload PSDs, calibration envelopes, and framefiles to the specified destination.

    Args:
        remote (str): Remote server address.
        remote_path (str): Path on the remote server where files will be uploaded.
        event_name (str): Name of the event for which files are being uploaded.
        config (str): Path to the configuration file.
        psds (list): List of PSD file paths to upload.
        calibration_envelopes (list): List of calibration envelope file paths to upload.
        framefiles (list): List of framefile paths to upload.
    """
    # test with local as remote

    upload_file(remote, config, os.path.join(remote_path, event_name, "config"))
    for psd in psds:
        upload_file(remote, psd, os.path.join(remote_path, event_name, "psds"))
    for envelope in calibration_envelopes:
        upload_file(remote, envelope, os.path.join(remote_path, event_name, "calibration_envelopes"))
    for framefile in framefiles:
        upload_file(remote, framefile, os.path.join(remote_path, event_name, "framefiles"))


def upload_file(remote, file, remote_path):
    shutil.copy(file, remote_path)
    print(f"✅ Uploaded {file} to {remote_path}")
