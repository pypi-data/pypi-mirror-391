import requests
import argparse
import os


def get_prefered_pe(event_name, detail_url):
    response = requests.get(detail_url)
    if response.status_code == 200:
        data = response.json()
    else:
        raise Exception(f"Failed to fetch event info: {response.status_code} - {response.text}")
    is_GWTC1 = data.get('catalog').startswith('GWTC-1-confident')
    parameters_url = data.get('parameters_url', None)
    response = requests.get(parameters_url + '?pagesize=1000')
    if response.status_code == 200:
        event_data = response.json()
    else:
        raise Exception(f"Failed to fetch event parameters: {response.status_code} - {response.text}")
    if event_data['num_pages'] > 1:
        raise NotImplementedError("Pagination not implemented yet for event listing.")
    
    if not event_data:
        raise ValueError(f"No data found for event {event_name} with parameters URL {parameters_url}")

    results = event_data.get('results', [])

    # get the combined PE (labelled as 'preferred' in the gwosc) and the XPHM for extracting config
    gwosc_preferred_pe = None

    for result in results:
        if is_GWTC1 and result.get('name', '').startswith('GWTC-1-confident') and result.get('name', '').endswith('R2_pe_combined'):
            gwosc_preferred_pe = result
            break

        if result.get('is_preferred', False):
            gwosc_preferred_pe = result
            break

    return gwosc_preferred_pe


def get_all_event(catalog = 'GWTC'):
    url = f"https://gwosc.org/api/v2/catalogs/{catalog}/events?pagesize=1000"
    print(f"Fetching event list from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
    else:
        raise Exception(f"Failed to fetch event info: {response.status_code} - {response.text}")    
    
    if data['num_pages'] > 1:
        raise NotImplementedError("Pagination not implemented yet for event listing.")
    print(f"Found {len(data['results'])} events in catalog {catalog}")
    # return sort by name in data['results']
    return sorted(data['results'], key=lambda x: x['name'])


def download_file(url, output_path):
    # check if the file already exists
    if os.path.exists(output_path):
        print(f"File {output_path} already exists, skipping download.")
        return

    # download the file
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded {url} to {output_path}")
    else:
        raise Exception(f"Failed to download file: {response.status_code} - {response.text}")


def extract_info(data_dir, catalog = 'GWTC'):
    # create the sample directory if it does not exist
    os.makedirs(f"{data_dir}/samples", exist_ok=True)

    # get the event list from gwosc
    events = {}
    for event in get_all_event(catalog=catalog):
        event_name = event['name']
        version = event['version']
        if event_name not in events:
            events[event_name] = event
        elif version > events[event_name]['version']:
            events[event_name] = event
        else:
            print(f"Skipping {event_name} version {version} as it is not the latest version.")

    # get the information for each event and download the preferred PE samples
    for event_name, event in events.items():
        print(event_name, f"v{event['version']}")
        # urls = get_event_urls(f"{event_name}-v{event['version']}", sample_rate=16384)
        
        gwosc_preferred_pe = get_prefered_pe(event_name, event["detail_url"])
        if gwosc_preferred_pe:
            print(f"{gwosc_preferred_pe['name']} data url: {gwosc_preferred_pe['data_url']}")

            outfile = f"{data_dir}/samples/{event_name}_combined_PEDataRelease.hdf"
            if os.path.exists(outfile):
                print(f"File {outfile} already exists, skipping download.")
            else:
                download_file(gwosc_preferred_pe['data_url'], outfile)
        else:
            print(f"⚠️ Event: {event_name}, Version: {event['version']}, No preferred PE found.")

def main():
    parser = argparse.ArgumentParser(description="Download GWOSC data for PE Automator")
    parser.add_argument('--data_dir', '-d', type=str, default='.', help='Path to the data directory where the samples will be downloaded')
    parser.add_argument('--catalog', '-c', type=str, default='GWTC', help='Catalog to use for event extraction')
    args = parser.parse_args()

    # extract information and download the preferred PE samples
    extract_info(args.data_dir, catalog=args.catalog)


if __name__ == "__main__":
    main()