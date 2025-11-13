import json


def get_allocation_info(allocation, data_path):
    """
    Get the allocation information based on the provided allocation string.
    """
    allocations = get_all_allocations(data_path)

    if allocation not in allocations:
        raise ValueError(f"Allocation '{allocation}' not found in the allocations file.")
    
    allocation_info = allocations[allocation]

    # Ensure the allocation info has the required keys
    required_keys = ['group_name', 'scratch']
    for key in required_keys:
        if key not in allocation_info:
            raise ValueError(f"Allocation info for '{allocation}' is missing the required key: {key}")

    return allocation_info


def get_all_allocations(data_path):
    """
    Get all allocations from the allocations file.
    """
    allocation_file = f"{data_path}/project/allocations.json"

    try:
        with open(allocation_file, 'r') as f:
            allocations = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Allocation file {allocation_file} not found.")    
    
    # remove allocations that are ignored
    allocations = {key: value for key, value in allocations.items() if not value.get('ignore', False)}

    return allocations


def get_env_path(allocation):
    """
    Get the environment path for the given allocation.
    """
    maintainer = allocation.get('maintainer')
    scratch = allocation.get('scratch')

    env_path = f"{scratch}/{maintainer}/envs"

    return env_path