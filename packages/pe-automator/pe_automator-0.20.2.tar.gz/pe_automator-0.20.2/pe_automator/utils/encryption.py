import json

def encrypted_name(data_dir, eventname, approximant, run_label, date):
    # load data_dir/project/lookup_table.json
    lookup_file = f"{data_dir}/project/lookup_table.json"
    try:
        with open(lookup_file, 'r') as f:
            lookup_table = json.load(f)
    except FileNotFoundError:
        print(f"Lookup table file {lookup_file} does not exist. Please generate it first.")
        return None
    
    # get the animal name from the lookup table
    animal_name = lookup_table.get(eventname)
    if not animal_name:
        print(f"Event name {eventname} not found in the lookup table.")
        raise ValueError(f"Event name {eventname} not found in the lookup table.")
    
    # create the encrypted name
    encrypted_name = f"{animal_name}_{approximant}_{run_label}_{date}"

    return encrypted_name
    