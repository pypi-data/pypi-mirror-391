from pe_automator.postprocessing.jobs import get_jobs, get_full_eventnames, read_results_catalog, get_gwtc_hdf5_filename
import json
from pe_automator.actions.gitlab import fetch_runs


def get_data_for_table(private_token, result_dir='results', data_path='data'):
    eventnames = sorted(get_full_eventnames(data_path))
    runs = fetch_runs(private_token=private_token)

    flatten_runs = runs['completed'] + runs['ongoing'] + runs['failed']
    wf_models = set([run['approximant'] for run in flatten_runs])
    data_dict = []
    for eventname in eventnames:
        data_dict.append({
            'eventname': eventname,
            '_children': [
                { 'approximant': approximant, 
                '_children': [
                    {
                        'run_label': run['run_label'],
                        'allocation': run['allocation'],
                        'npoint': run.get('npoint', 1000),
                        'naccept': run.get('naccept', 50),
                        'comment': run.get('comment', ''),
                        'issue_id': run['issue'].iid,
                        'status': run['job_status'],
                    } for run in flatten_runs if run['eventname'] == eventname and run['approximant'] == approximant
                ] } for approximant in wf_models]
        })

    table_data_json = json.dumps(data_dict, indent=4)

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>PEsummary Table</title>
        <link href="https://unpkg.com/tabulator-tables/dist/css/tabulator.min.css" rel="stylesheet">
        <script type="text/javascript" src="https://unpkg.com/tabulator-tables/dist/js/tabulator.min.js"></script>
        <style>

            .tabulator-completed {
                color: green;
            }
            .tabulator-failed {
                color: red;
            }
            .tabulator-hold {
                color: orange;
            }
            .tabulator-pending {
                color: blue;
            }
        </style>
    </head>
    <body>
        <h1>PEsummary Table</h1>
        <div id="example-table"></div>
    </body>
    <script>
        var tableDataNested = ;
        var table = new Tabulator("#example-table", {
            // height:"311px",
            data:tableDataNested,
            dataTree:true,
            dataTreeStartExpanded:true,
            columns:[
            {title:"Event Name", field:"eventname", width:150, responsive:0}, //never hide this column
            {title:"Approximant", field:"approximant", width:150, responsive:0}, //never hide this column
            {title:"Status", field:"status", width:80, responsive:0, formatter:function(cell){
                var status = cell.getValue();
                if (status === 'completed') {
                    return "<span class='tabulator-completed'>Completed</span>";
                } else if (status === 'failed') {
                    return "<span class='tabulator-failed'>Failed</span>";
                } else if (status === 'hold') {
                    return "<span class='tabulator-hold'>Hold</span>";
                } else if (status === 'pending') {
                    return "<span class='tabulator-pending'>Pending</span>";
                } else {
                    return status;
                }
            }
            }, 
            {title:"Run Label", field:"run_label", width:80, responsive:0}, //never hide this column
            {title:"Allocation", field:"allocation", width:120, responsive:0}, //never hide this column
            {title:"Npoint", field:"npoint", width:40, responsive:0}, //never hide this column
            {title:"Naccept", field:"naccept", width:40, responsive:0}, //never hide this column
            {title:"Comment", field:"comment", width:200, responsive:0}, //never hide this column
            {title:"Issue ID", field:"issue_id", width:40, responsive:0}, //never hide this column
            
            ],
        });
    </script>
    </html>
    """

    html_output = template.replace("var tableDataNested = ;", f"var tableDataNested = {table_data_json};")
    
    with open(f"{result_dir}/pe_summary_table.html", 'w') as f:
        f.write(html_output)