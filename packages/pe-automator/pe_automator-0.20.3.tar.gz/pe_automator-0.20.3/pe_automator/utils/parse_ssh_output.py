import re


def clean_env_in_string(string):
    """
    Remove lines starting with 'Set ', 'load ', 'unload ', and 'remove ' from the given string.
    """
    # lines = string.splitlines()

    # Regex to filter out unwanted lines
    pattern = r'^(load|unload|remove)\s+[^\(]+\([\s\S]*?\)\n?'

    # Filter the output
    cleaned_text = re.sub(pattern, '', string, flags=re.MULTILINE)


    cleaned_lines = [
        line for line in cleaned_text.splitlines()
        if line and not (line.startswith('Set ') or line.startswith('load ') or line.startswith('unload ') or line.startswith('remove '))
    ]
    
    return '\n'.join(cleaned_lines)
