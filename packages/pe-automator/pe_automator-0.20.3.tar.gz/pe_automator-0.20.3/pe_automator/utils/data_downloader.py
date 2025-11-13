import subprocess
import os


def download_timeseries_data(remote_user, detector, channel, start_time, end_time, eventname, remote_host='ldas-pcdev12.ligo.caltech.edu', local_output_path='data'):
    """
    Download time series data for a given channel and time range.

    :param channel: The name of the channel to download data from.
    :param start_time: The start time for the data in GPS seconds.
    :param end_time: The end time for the data in GPS seconds.
    :return: A TimeSeries object containing the downloaded data.
    """
    python_code = f"""from gwpy.timeseries import TimeSeries
timeseries = TimeSeries.get('{detector}:{channel}', {start_time}, {end_time})
timeseries.write('{eventname}_{detector}.gwf')
"""
    
    escaped_code = python_code.replace('"', '\\"').replace("\n", "; ")
    ssh_command = f'ssh {remote_user}@{remote_host} "source /cvmfs/oasis.opensciencegrid.org/ligo/sw/conda/etc/profile.d/conda.sh; conda activate igwn; python3 -c \\"{escaped_code}\\""'

    print(f"Executing command: {ssh_command}")

    try:
        result = subprocess.run(
            ssh_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Remote execution succeeded.")
        print("Remote STDOUT:\n", result.stdout)

    except subprocess.CalledProcessError as e:
        print("❌ Remote execution failed.")
        print("Exit code:", e.returncode)
        print("Remote STDERR:\n", e.stderr)
        print("Remote STDOUT:\n", e.stdout)
        exit(1)

    # Now download the result
    if not os.path.exists(local_output_path):
        os.makedirs(local_output_path)

    scp_command = f"scp {remote_user}@{remote_host}:~/{eventname}_{detector}.gwf {local_output_path}/"

    try:
        print("Downloading result...")
        subprocess.run(scp_command, shell=True, check=True)
        print("✅ Download complete:", local_output_path)
    except subprocess.CalledProcessError as e:
        print("❌ SCP failed.")
        print("Exit code:", e.returncode)
        print("SCP STDERR:\n", e.stderr)


def download_timeseries_data_local(detector, channel, start_time, end_time, eventname, local_output_path='data'):
    """
    Download time series data for a given channel and time range locally.

    :param detector: The name of the detector.
    :param channel: The name of the channel to download data from.
    :param start_time: The start time for the data in GPS seconds.
    :param end_time: The end time for the data in GPS seconds.
    :return: A TimeSeries object containing the downloaded data.
    """
    from gwpy.timeseries import TimeSeries

    timeseries = TimeSeries.get(f'{detector}:{channel}', start_time, end_time)
    
    if not os.path.exists(local_output_path):
        os.makedirs(local_output_path)

    output_file = os.path.join(local_output_path, f'{eventname}_{detector}.gwf')
    timeseries.write(output_file)
    
    print(f"✅ Download complete: {output_file}")


if __name__ == "__main__":
    # Example usage
    # download_timeseries_data(
    #     remote_user='yumeng.xu',
    #     detector='H1',
    #     channel='GDS-CALIB_STRAIN_CLEAN_AR',
    #     start_time=1368449840.166504,
    #     end_time=1368449968.166504,
    #     eventname='GW230518_125908'
    # )

    download_timeseries_data_local(
        detector='H1',
        channel='GDS-CALIB_STRAIN_CLEAN_AR',
        start_time=1368449840.166504,
        end_time=1368449968.166504,
        eventname='GW230518_125908'
    )