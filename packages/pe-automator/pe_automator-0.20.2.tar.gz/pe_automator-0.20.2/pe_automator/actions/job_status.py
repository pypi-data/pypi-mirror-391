import re
from datetime import datetime
from pe_automator.actions.remote import run_command
from pe_automator.utils.parse_ssh_output import clean_env_in_string


def check_data_generated(run_info, ssh_client):
    """
    Check if the data generation has been completed for the given run information.
    
    Parameters:
    - run_info: Dictionary containing run information including 'run_dir' and 'remote'.
    
    Returns:
    - bool: True if data generation is complete, False otherwise.
    """
    
    run_dir = run_info['run_dir']
    
    # Command to check the last line of the error log file
    command = f'ls {run_dir}/log_data_generation/*.err 1> /dev/null 2>&1 && tail -n 1 {run_dir}/log_data_generation/*.err || echo "NO_ERR_FILES_FOUND"'
    
    # Execute the command on the remote server
    # remote = f"{user}@{run_info['hostname']}"
    # result = run_command(command, remote, silent=True)
    result, err = ssh_client.execute(command, get_output=True)

    if result.strip() == "NO_ERR_FILES_FOUND":
        return 'pending', ''
    
    if "Completed data generation" in result:
        # This means the data generation has completed successfully and moving the next stage. So no status should be recorded.
        return '', ''
    elif "Error" in result:
        # If there is an error in the log, return the error message
        return 'failed', result
    else:
        # If the log does not indicate completion or error, assume it is still running
        return 'pending', ''



def get_data_analysis_log(run_info, ssh_client):
    """
    Get the last line of the data analysis log for the given run information.
    
    Parameters:
    - run_info: Dictionary containing run information including 'run_dir' and 'remote'.
    
    Returns:
    - str: The last line of the data analysis log.
    """
    # remote = f"{user}@{run_info['hostname']}"
    run_dir = run_info['run_dir']

    # Execute the command on the remote server
    log_files_str, err = ssh_client.execute(f'bash -c "ls {run_dir}/log_data_analysis/*.err 1> /dev/null 2>&1 && stat --format=\'%Y %n\' {run_dir}/log_data_analysis/*  || echo \"NO_ERR_FILES_FOUND\""')
    log_files_str = clean_env_in_string(log_files_str)  # Clean the output to remove unwanted lines

    if log_files_str.strip() == "NO_ERR_FILES_FOUND":
        return []
    files = []

    for line in log_files_str.split('\n'):
        if not line.strip():
            continue
        parts = line.split()
        timestamp = int(parts[0])
        filename = ' '.join(parts[1:])
        file_info = {
            'timestamp': timestamp,
            'filename': filename,
            'datetime': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        }

        if filename.endswith('.err'):
            file_info['type'] = 'err'
        elif filename.endswith('.out'):
            file_info['type'] = 'out'

        if re.search(r'par\d+\.(err|out)', filename):
            file_info['job_type'] = 'analysis'
        elif re.search(r'merge.(err|out)', filename):
            file_info['job_type'] = 'merge'
        elif re.search(r'merge_plot.(err|out)', filename):
            file_info['job_type'] = 'merge_plot'
        elif re.search(r'merge_final_result.(err|out)', filename):
            file_info['job_type'] = 'merge_final_result'
        
        timestamp_now = int(datetime.now().timestamp())
        file_info['recent'] = (timestamp_now - timestamp) < 60 * 30
        files.append(file_info)

    return files


def check_data_analysis(run_info, ssh_client):
    """
    Check if the data analysis has been completed for the given run information.
    
    Parameters:
    - run_info: Dictionary containing run information including 'run_dir' and 'remote'.
    
    Returns:
    - bool: True if data analysis is complete, False otherwise.
    """
    status = None

    files = get_data_analysis_log(run_info, ssh_client)

    if not files:
        # this means the generation is done but no analysis has been started yet
        return 'pending', ''

    merge_logs = [f for f in files if f['job_type'] == 'merge' and f['type'] == 'err']

    # if reached the merge stage, check the last merge log
    if len(merge_logs) > 0:
        merge_log = merge_logs[-1]

        result, err = ssh_client.execute(f"tail -n 10 {merge_log['filename']}", get_output=True)

        # if 'Combined results have \d+\ samples' in result:
        if re.search(r'Combined results have \d+ samples', result):
            status = 'completed'
            return status, ''
        else:
            if merge_log['recent']:
                status = 'merging'
                return status, ''
            else:
                status = 'failed'
                return status, result

    # if not reached the merge stage, check the analysis logs
    # first check if any partial analysis logs finished      
    partial_err_logs = [f for f in files if f['job_type'] == 'analysis' and f['type'] == 'err']
    is_analysis_completed = []
    is_analysis_failed = []
    messages = []
    for log in partial_err_logs:
        result, err = ssh_client.execute(f"tail -n 10 {log['filename']}", get_output=True)
  
        if re.search(r'Run completed', result):
            is_analysis_completed.append(True)
        else:
            is_analysis_completed.append(False)
            if re.search(r'Error', result):
                is_analysis_failed.append(True)
            else:
                is_analysis_failed.append(False)
        messages.append(result)
    if is_analysis_completed and all(is_analysis_completed):
        status = 'analysis_completed'
        return status, ''
    if any(is_analysis_failed):
        status = 'failed'
        return status, messages
    
    # TODO: if not failed nor completed, check if any analysis logs are still running
    if any(f['recent'] for f in files if f['job_type'] == 'analysis'):
        # if any analysis logs are recent, assume it is still running
        status = 'running'
        return status, ''
    # if no analysis logs are recent, assume it is might be hung
    else:
        # check if there are any recent logs
        if any(f['recent'] for f in files):
            status = 'running'
            return status, ''
        else:
            # no recent logs, assume it is failed
            status = 'hold'
            return status, ''
    
