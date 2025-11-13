from pe_automator.actions.gitlab import fetch_runs
from pe_automator.postprocessing.jobs import get_jobs, get_full_eventnames, read_results_catalog
import gitlab
import yaml
import json
import os


approximants = ['IMRPhenomTEHM', 'IMRPhenomXPNR',  'IMRPhenomXE', 'IMRPhenomTPHM', 'IMRPhenomTHM', 'IMRPhenomTHM_20']
key_approximants = ['IMRPhenomTEHM', 'IMRPhenomXPNR', 'IMRPhenomTPHM', 'IMRPhenomTHM', 'IMRPhenomTHM_20']
core_approximants = ['IMRPhenomTEHM', 'IMRPhenomXPNR', 'IMRPhenomTHM_20']

def get_data(data_folder, private_token):
    with open(os.path.join(data_folder, 'project', 'project.json'), 'r') as f:
        project_config = json.load(f)
    print(f"Loaded project configuration: {project_config}")
    gitlab_url, gitlab_project = project_config['gitlab_url'], project_config['gitlab_project']

    full_eventnames = get_full_eventnames(data_folder)
    runs = fetch_runs(gitlab_url=gitlab_url, gitlab_project=gitlab_project, private_token=private_token)

    all_runs_flattern = [run for sublist in [runs['completed'], runs['ongoing'], runs['failed']] for run in sublist]

    for run in all_runs_flattern:
        if 'job::completed' in run['issue'].labels:
            run['status'] = 'completed'
        elif 'job::hold' in run['issue'].labels or 'job::pending' in run['issue'].labels:
            run['status'] = 'hold'
        elif 'job::running' in run['issue'].labels:
            run['status'] = 'running'
        elif 'job::failed' in run['issue'].labels:
            run['status'] = 'failed'
        elif 'job::cancelled' in run['issue'].labels:
            run['status'] = 'failed'
        else:
            run['status'] = 'pending'


    data = {}

    for eventname in full_eventnames:
        data[eventname] = {}
        for approximant in approximants:
            data[eventname][approximant] = {}
            related_runs = [run for run in all_runs_flattern if eventname == run['eventname'] and approximant == run['approximant']]

            ODProd_runs = [run for run in related_runs if run['run_label'].startswith('ODProd')]
            if ODProd_runs:
                ODProd_runs.sort(key=lambda x: x['issue'].iid, reverse=True)
                data[eventname][approximant]['ODProd'] = {
                    'label': ODProd_runs[0]['run_label'],
                    'link': f'https://git.ligo.org/yumeng.xu/uib-o4a-catalog/-/issues/{ODProd_runs[0]["issue"].iid}',
                    'status': ODProd_runs[0]['status']
                }
            prod_runs = [run for run in related_runs if run['run_label'].startswith('prod')]
            if prod_runs:
                prod_runs.sort(key=lambda x: x['issue'].iid, reverse=True)
                data[eventname][approximant]['Prod'] = {
                    'label': prod_runs[0]['run_label'],
                    'link': f'https://git.ligo.org/yumeng.xu/uib-o4a-catalog/-/issues/{prod_runs[0]["issue"].iid}',
                    'status': prod_runs[0]['status']
                }
            postprod_runs = [run for run in related_runs if run['run_label'].startswith('PostProd')]
            if postprod_runs:
                postprod_runs.sort(key=lambda x: x['issue'].iid, reverse=True)
                data[eventname][approximant]['PostProd'] = {
                    'label': postprod_runs[0]['run_label'],
                    'link': f'https://git.ligo.org/yumeng.xu/uib-o4a-catalog/-/issues/{postprod_runs[0]["issue"].iid}',
                    'status': postprod_runs[0]['status']
                }
            other_completed_runs = [run for run in related_runs if run['status'] == 'completed' and not (run['run_label'].startswith('ODProd') or run['run_label'].startswith('prod') or run['run_label'].startswith('PostProd'))]
            if other_completed_runs:
                other_completed_runs.sort(key=lambda x: x['issue'].iid, reverse=True)
                data[eventname][approximant]['OtherCompleted'] = [{
                    'label': run['run_label'],
                    'link': f'https://git.ligo.org/yumeng.xu/uib-o4a-catalog/-/issues/{run["issue"].iid}',
                    'status': run['status']
                } for run in other_completed_runs]


            if data[eventname][approximant].get('ODProd') and data[eventname][approximant].get('ODProd').get('status') == 'completed':
                data[eventname][approximant]['status'] = 'completed'
            elif data[eventname][approximant].get('Prod') or data[eventname][approximant].get('OtherCompleted'):
                data[eventname][approximant]['status'] = 'explored'
            else:
                data[eventname][approximant]['status'] = 'not_started'
        
        completed = True
        for approx in key_approximants:
            if data[eventname][approx].get('status') != 'completed':
                completed = False
                break

    return data


def getEventCategories(private_token, gitlab_url, gitlab_project):
    gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
    project = gl.projects.get(gitlab_project)
    page = project.wikis.get('/results/labelled-events')
    data = yaml.safe_load(page.content)
    return data


# status → color map
status_colors = {
    'completed': 'lightgreen',
    'hold': 'orange',
    'failed': 'lightcoral',
    'pending': 'lightgray',
    'running': 'white'
}

approx_status_colors = {
    'completed': 'lightgreen',
    'explored': 'orange',
    'not_started': 'white'
}

event_status_colors = {
    'completed': 'lightgreen',
    'explored': 'orange',
    'unexplored': 'lightcoral'
}

def get_pesummary_url(eventname, label, approx):
    # http://escorpora.uib.es/uib-o4a/plots/pesummary/GW230601_224134/html/IMRPhenomTHM_20_test_cat0_1_IMRPhenomTHM_20_test_cat0_1.html
    return f"http://escorpora.uib.es/uib-o4a/plots/pesummary/{eventname}/html/{approx}_{label}_{approx}_{label}.html"

def generate_html(data, labels, outfile="waveforms.html"):
    html = ["<html><head><style>",
            "table { border-collapse: collapse; width: 100%; }",
            "th, td { border: 1px solid #ccc; padding: 6px; text-align: left; }",
            "th { background: #f4f4f4; }",
            ".hidden { display: none; }",
            "</style></head><body>",
            "<h2>Event Processing Table</h2>"]
    # add instructions about event column color, and waveform color
    html.append("<p>Event column colors indicate the status of the event:</p>")
    html.append("<ul>")
    for status, color in event_status_colors.items():
        html.append(f"<li style='color:{color};'>{status}</li>")
    html.append("</ul>")
    html.append("<p>Waveform colors indicate the status of the approximants:</p>")
    html.append("<ul>")
    for status, color in approx_status_colors.items():
        html.append(f"<li style='color:{color};'>{status}</li>")
    html.append("</ul>")
    
    # Dropdown filter
    html.append("<label for='eventFilter'>Filter events: </label>")
    html.append("<select id='eventFilter' onchange='filterEvents()'>")
    html.append("<option value='all'>All</option>")
    for category in labels.keys():
        html.append(f"<option value='{category}'>{category}</option>")
    html.append("</select>")

    # Table header
    html.append("<table id='eventTable'>")
    html.append("<tr><th>Event</th><th>Approximant</th><th>ODProd Run</th>"
                "<th>Prod Run</th><th>PostProd Run</th><th>Other Completed</th></tr>")

    for event, approx_dict in data.items():
        approx_list = list(approx_dict.items())
        rowspan = len(approx_list)
        first_row = True

        # classify event into categories
        category_class = []
        for cat, events in labels.items():
            if event in events:
                category_class.append(cat)
        category_class = " ".join(category_class) if category_class else "uncategorized"

        completed = True
        for approx in key_approximants:
            if data[event][approx].get('status') != 'completed':
                completed = False
        explored = True
        for approx in core_approximants:
            if data[event][approx].get('status') != 'explored' and data[event][approx].get('status') != 'completed':
                explored = False
        status = 'unexplored'
        if completed:
            status = 'completed'
        elif explored:
            status = 'explored'

        for approx, runs in approx_list:
            row = []

            if first_row:
                row.append(f"<td rowspan='{rowspan}' style='background:{event_status_colors.get(status, 'white')}'>{event}</td>")
                first_row = False

            row.append(f"<td style='background:{approx_status_colors.get(runs['status'], 'white')}'>{approx}</td>")
            
            if runs.get('ODProd'):
                val = runs['ODProd']
                status = val.get('status', 'pending')
                color = status_colors.get(status, 'white')
                label = val.get('label', 'N/A')
                link = val.get('link', '#')
                cell = f"<a href='{link}' style='background:{color}; padding:2px 6px; display:inline-block;'>{label}</a> (<a href='{get_pesummary_url(event, label, approx)}'>PESummary</a>)"
            else:
                cell = ""
            row.append(f"<td>{cell}</td>")
            if runs.get('Prod'):
                val = runs['Prod']
                status = val.get('status', 'pending')
                color = status_colors.get(status, 'white')
                label = val.get('label', 'N/A')
                link = val.get('link', '#')
                cell = f"<a href='{link}' style='background:{color}; padding:2px 6px; display:inline-block;'>{label}</a> (<a href='{get_pesummary_url(event, label, approx)}'>PESummary</a>)"
            else:
                cell = ""
            row.append(f"<td>{cell}</td>")
            if runs.get('PostProd'):
                val = runs['PostProd']
                status = val.get('status', 'pending')
                color = status_colors.get(status, 'white')
                label = val.get('label', 'N/A')
                link = val.get('link', '#')
                cell = f"<a href='{link}' style='background:{color}; padding:2px 6px; display:inline-block;'>{label}</a> (<a href='{get_pesummary_url(event, label, approx)}'>PESummary</a>)"
            else:
                cell = ""
            row.append(f"<td>{cell}</td>")
            if runs.get('OtherCompleted'):
                cell = ""
                for run in runs['OtherCompleted']:
                    val = run
                    status = val.get('status', 'pending')
                    color = status_colors.get(status, 'white')
                    label = val.get('label', 'N/A')
                    link = val.get('link', '#')
                    cell += f"<a href='{link}' style='background:{color}; padding:2px 6px; display:inline-block; margin: 1px'>{label}</a> (<a href='{get_pesummary_url(event, label, approx)}'>PESummary</a>)"
                cell = f"<div>{cell}</div>"
            else:
                cell = ""
            row.append(f"<td>{cell}</td>")
            # html.append("<tr>" + "".join(row) + "</tr>")
            html.append("<tr class='event-row " + category_class + "'>" + "".join(row) + "</tr>")

    # html.append("</table></body></html>")
    html.append("</table>")

    # JavaScript filter
    html.append("""
<script>
function filterEvents() {
  var filter = document.getElementById('eventFilter').value;
  var rows = document.querySelectorAll('#eventTable .event-row');
  rows.forEach(function(row) {
    if (filter === 'all') {
      row.style.display = '';
    } else {
      if (row.classList.contains(filter)) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    }
  });
}
</script>
""")

    html.append("</body></html>")
    
    with open(outfile, "w") as f:
        f.write("\n".join(html))

    print(f"HTML table written to {outfile}")


def run_webpage(data_folder, private_token, output_html):
    with open(os.path.join(data_folder, 'project', 'project.json'), 'r') as f:
        project_config = json.load(f)
    print(f"Loaded project configuration: {project_config}")
    gitlab_url, gitlab_project = project_config['gitlab_url'], project_config['gitlab_project']

    data = get_data(data_folder, private_token)
    labels = getEventCategories(private_token, gitlab_url=gitlab_url, gitlab_project=gitlab_project)
    generate_html(data, labels, outfile=output_html)