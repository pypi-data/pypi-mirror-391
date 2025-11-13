# conda install pandas
# conda install tabulate

import pandas as pd
import re
from datetime import timedelta
from pe_automator.actions.gitlab import fetch_runs


emojis = {'completed': '✅', 'failed': '❌', 'running': '🚧'}


def parse_time_to_seconds(t: str) -> int:
    """Converts 'HH:MM:SS' or '1 day, HH:MM:SS' to seconds"""
    if "day" in t:
        day_part, time_part = t.split(", ")
        days = int(day_part.split()[0])
    else:
        days = 0
        time_part = t

    h, m, s = map(int, time_part.split(":"))
    return int(timedelta(days=days, hours=h, minutes=m, seconds=s).total_seconds())


def parse_progress(log_lines):
    """
    Parses the log lines to extract iteration, time, and dlogz values.
    
    Args:
        log_lines (list of str): Lines from the log file.
        
    Returns:
        list of dict: Parsed results with iteration, time, and dlogz.
    """
    log_lines = log_lines.strip().splitlines()
    pattern = re.compile(
        r"(?P<iteration>\d+)it \[(?P<time>(?:\d{1,2}:\d{2}:\d{2}|\d+ days?, \d{1,2}:\d{2}:\d{2})).*?dlogz:(?P<dlogz>[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)>"
    )
    
    results = []
    
    for line in log_lines:
        match = pattern.search(line)
        if match:
            results.append({
                "iteration": int(match.group("iteration")),
                "time": parse_time_to_seconds(match.group("time")),
                "dlogz": float(match.group("dlogz")),
            })
    
    return results


def generate_event_list():
    """
    Fetches and flattens run data from the GitLab project.

    Returns:
    - pd.DataFrame: Flattened DataFrame with each run labels.
    """

    run_dict = fetch_runs(private_access_token)
    runs = []
   
    for status, entries in run_dict.items():
        for entry in entries:
            run = entry.copy()
            run['status'] = status
            runs.append(run)

    df = pd.DataFrame(runs)
    return df

def generate_markdown_event_table():
    """
    Builds a Markdown table of events with status and issue links.

    Returns:
        str: Markdown-formatted string.
    """

    df = generate_event_list()

    # Empty DataFrame
    data = pd.DataFrame(index=df['eventname'].unique(), columns=df['approximant'].unique())

    for _, row in df.iterrows():
        event = row['eventname']
        approximant = row['approximant']
        job_status = row['job_status']
        web = row['issue'].web_url
        label = row['title'].rsplit(" - ", 1)[-1]

        info = f"{emojis.get(job_status, '❓')} [{label}]({web})"

        current = data.at[event, approximant]
        data.at[event, approximant] = f"{current}\n{info}" if pd.notna(current) else info

    return data.to_markdown(index=True)