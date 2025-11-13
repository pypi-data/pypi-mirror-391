#!/usr/bin/env python

"""
This is an example script to run PESummary from within a python script for
non-gravitational wave data.
"""
from pesummary.core import command_line, inputs, finish
from pesummary.core.file import meta_file
from pesummary.cli.summarypages import main


def generate_summary_page(run_info):
    """
    Generate a summary page for the given run information.

    Parameters
    ----------
    run_info : dict
        A dictionary containing the run information, including 'file_path',
        'eventname', and 'title'.
    """

    from pesummary.cli.summarypages import main

    main_args = [
        "--samples", run_info['file_path'],
        "--webdir", f'pesummary/{run_info["eventname"]}',
        "--label", run_info['title'],
        "--gw", "true"
    ]
    
    main(main_args)

