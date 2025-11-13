from packaging import version
import requests
import json
from pe_automator._version import __version__
import os

def is_version_newer(project_json):
    # get the version URL from the project JSON
    if not os.path.exists(project_json):
        print(f"Project JSON file does not exist: {project_json}")
        return False
    try:
        with open(project_json, 'r') as f:
            project_data = json.load(f)
        version_url = project_data.get('version_url')
        if not version_url:
            print("Version URL not found in the project JSON.")
            return False
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return False

    # Get the content of the version file
    try:
        response = requests.get(version_url)
        response.raise_for_status()  # Raise an error for HTTP errors
        min_version = response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching version file: {e}")
        return False
    
    is_new = version.parse(__version__.lstrip('v')) >= version.parse(min_version.lstrip('v'))

    print(f"Current version: {__version__}, Minimum required version: {min_version}")
    return is_new