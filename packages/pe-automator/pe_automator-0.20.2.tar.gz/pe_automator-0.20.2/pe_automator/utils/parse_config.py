import configparser


class FlexibleKeyDict(dict):
    """
    A dictionary that allows flexible key access, replacing '-' with '_' and vice versa, to handle the different key formats
    used in bilby pipe
    """
    def get(self, key, default=None):
        if key in self:
            return super().get(key, default)

        # Try replacing - with _ and vice versa
        alt_key_1 = key.replace('-', '_')
        alt_key_2 = key.replace('_', '-')

        if alt_key_1 in self:
            return super().get(alt_key_1, default)
        elif alt_key_2 in self:
            return super().get(alt_key_2, default)

        return default


def parse_dict_from_string(dict_string):
    dict_string = dict_string.strip('{} \n')
    # Split into key-value pairs
    dict_items = [item for item in dict_string.split(',') if item.strip()]
    # Build the dictionary
    parsed_dict = {}
    for item in dict_items:
        if ':' in item:
            key, value = item.split(':', 1)
            key = key.strip().strip('"').strip("'")
            value = value.strip().strip('"').strip("'")
           
            parsed_dict[key] = value

    return parsed_dict


def parse_array_from_string(array_string):
    if array_string.startswith('['):
        output_arr = eval(array_string)
    else:
        output_arr = [array_string]
    
    output_arr = [item.strip("'") for item in output_arr]
    
    return output_arr


def clean_string_array(input_array):
    """
    Clean an array of strings by removing leading and trailing whitespace and quotes.
    
    :param input_array: List of strings to clean.
    :return: List of cleaned strings.
    """
    return [item.strip().strip('"').strip("'") for item in input_array if item.strip()]


def convert_dict_to_string(input_dict):
    """
    Convert a dictionary to a string representation suitable for configuration files.
    
    :param input_dict: Dictionary to convert.
    :return: String representation of the dictionary.
    """
    return '{' + ', '.join(f'{k}: {v}' for k, v in input_dict.items()) + '}'


def parse_config(config_file):
    """
    Parse the configuration file and return a FlexibleKeyDict.
    
    :param config_file: Path to the configuration file.
    :return: FlexibleKeyDict containing the parsed configuration.
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    parsed_config = FlexibleKeyDict()

    for section in config.sections():
        for key, value in config.items(section):
            if value.startswith('{') and value.endswith('}'):
                value = parse_dict_from_string(value)
            elif value.startswith('[') and value.endswith(']'):
                value = parse_array_from_string(value)
            parsed_config[f"{section}-{key}"] = value

    return parsed_config