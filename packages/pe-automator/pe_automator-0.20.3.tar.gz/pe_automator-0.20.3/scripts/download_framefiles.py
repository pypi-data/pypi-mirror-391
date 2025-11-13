import os
import json
import argparse
from gwpy.timeseries import TimeSeries
from gwosc.datasets import event_gps


special_events = {
    'GW230608_205047': {
        'start': 7,
        'end': 16
    },
    'GW230518_125908': {
        'start': 5,
        'end': 16
    },
}

def download_timeseries_data_local(detector, channel, start_time, end_time, eventname, local_output_path='framefiles'):
    """
    Download time series data for a given channel and time range locally.

    :param detector: The name of the detector.
    :param channel: The name of the channel to download data from.
    :param start_time: The start time for the data in GPS seconds.
    :param end_time: The end time for the data in GPS seconds.
    :return: A TimeSeries object containing the downloaded data.
    """
    output_file = os.path.join(local_output_path, f'{eventname}_{detector}.gwf')
    if os.path.exists(output_file):
        print(f"⚠️ File already exists: {output_file}")
        return

    timeseries = TimeSeries.get(f'{detector}:{channel}', start_time, end_time)
    
    if not os.path.exists(local_output_path):
        os.makedirs(local_output_path)

    timeseries.write(output_file)
    
    print(f"✅ Download complete: {output_file}")


def download_timeseries_data_gwosc(detector, start_time, end_time, eventname, local_output_path='framefiles'):
    output_file = os.path.join(local_output_path, f'{eventname}_{detector}.gwf')
    
    if os.path.exists(output_file):
        print(f"⚠️ File already exists: {output_file}")
        return
    
    timeseries = TimeSeries.fetch_open_data(detector, start_time, end_time, sample_rate=16384)
    
    if not os.path.exists(local_output_path):
        os.makedirs(local_output_path)

    timeseries.name = f'{detector}:GWOSC-16KHZ_R1_STRAIN'
    timeseries.write(output_file)

    print(f"✅ Download complete: {output_file}")


def read_events_from_dir(directory):
    """
    Read event files from a specified directory and return a list of event names.

    :param directory: The directory containing event files.
    :return: A list of event names.
    """
    events = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            event_name = filename[:-5]  # Remove the '.json' extension
            with open(os.path.join(directory, filename), 'r') as file:
                event_data = json.load(file)
                events[event_name] = event_data
    return events


def main():
    argparser = argparse.ArgumentParser(description='Download time series data for gravitational wave events.')
    argparser.add_argument('event_dir', type=str, help='Directory containing event JSON files.')
    argparser.add_argument('--output', type=str, default='framefiles', help='Output directory for downloaded data (default: framefiles).')

    args = argparser.parse_args()
    event_dir = args.event_dir
    output_dir = args.output

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    events = read_events_from_dir(event_dir)

    for event_name, event_data in events.items():
        print(f"Processing event: {event_name}")
        
        detectors = event_data.get('detectors', [])

        if event_name in special_events:
            left_offset = special_events[event_name]['start']
            right_offset = special_events[event_name]['end']
        else:
            left_offset = 16
            right_offset = 16

        for detector in detectors:
            channel = event_data['channel_dict'][detector]
            start_time = event_data['start_time'] - left_offset
            end_time = event_data['end_time'] + right_offset
            
            print(f"Downloading data for {detector} on channel {channel} from {start_time} to {end_time}")
            if event_data.get('gwosc', False):
                download_timeseries_data_gwosc(detector, start_time, end_time, event_name, output_dir)
            else:
                download_timeseries_data_local(detector, channel, start_time, end_time, event_name, output_dir)


if __name__ == "__main__":
    main()