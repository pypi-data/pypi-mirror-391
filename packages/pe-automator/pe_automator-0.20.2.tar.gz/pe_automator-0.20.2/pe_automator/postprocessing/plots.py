from datetime import datetime
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from itertools import combinations
from pesummary.utils.utils import jensen_shannon_divergence_from_samples, jensen_shannon_divergence_from_pdfs
from .read import read_samples
from ..constants.events import (
    eccentricCandidates,
    glitchedEvents,
    problemEvents,
    waveformSystematicsLVK,
    glitchedeccentricCandidates,
    eccentricSystematics,
    eccentricAEISystematics,
    glitchedSystematics,
    multimodalities,
    newSystematics
)

model_colors = {
    'GWTC': 'grey',
    'IMRPhenomXPNR': 'royalblue',
    'IMRPhenomXE': 'orchid',
    'IMRPhenomTEHM': 'forestgreen',
    'IMRPhenomTHM_20': 'crimson',
    'IMRPhenomTHM': 'orange',
    'IMRPhenomTPHM': 'gold',
    'IMRPhenomXPHM': 'lightseagreen'
}

event_group_colors = {
    'eccentricCandidates': 'orange',
    'glitchedEvents': 'dodgerblue',
    'problemEvents': 'black',
    'waveformSystematicsLVK': 'green',
    'glitchedeccentricCandidates': 'crimson',
    'eccentricSystematics': 'darkturquoise',
    'eccentricAEISystematics': 'purple',
    'glitchedSystematics': 'peru',
    'multimodalities': 'mediumseagreen',
    'newSystematics': 'orchid'
}

def get_event_color(event):
    # if event in eccentricCandidateAEI:
    #     return event_group_colors['eccentricCandidateAEI']
    if event in eccentricCandidates:
        return event_group_colors['eccentricCandidates']
    elif event in glitchedEvents:
        return event_group_colors['glitchedEvents']
    elif event in problemEvents:
        return event_group_colors['problemEvents']
    elif event in waveformSystematicsLVK:
        return event_group_colors['waveformSystematicsLVK']
    elif event in glitchedeccentricCandidates:
        return event_group_colors['glitchedeccentricCandidates']
    elif event in eccentricSystematics:
        return event_group_colors['eccentricSystematics']
    elif event in eccentricAEISystematics:
        return event_group_colors['eccentricAEISystematics']
    elif event in glitchedSystematics:
        return event_group_colors['glitchedSystematics']
    elif event in multimodalities:
        return event_group_colors['multimodalities']
    elif event in newSystematics:
        return event_group_colors['newSystematics']
    else:
        return 'gray' 

def posteriors_1d(pe_file_dict, parameters, filename, eventnames=None):
    if eventnames is None:
        selected_pe_file_dict = dict(sorted(list(pe_file_dict.items())))
    else:
        selected_pe_file_dict = {event: pe_file_dict[event] for event in eventnames if event in pe_file_dict}

    n_events = len(selected_pe_file_dict)
    n_params = len(parameters)
    fig, axes = plt.subplots(nrows=n_events, ncols=n_params, figsize=(3*n_params, 2.5*n_events), sharex=False, sharey=False)
    fig.subplots_adjust(wspace=0.3, hspace=0.3)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plt.suptitle(f'dlogz Progress Check at {now}', fontsize=16)

    if n_events == 1:
        axes = np.expand_dims(axes, axis=0)
    if n_params == 1:
        axes = np.expand_dims(axes, axis=1)

    skip_dict = {
        'IMRPhenomTHM': ['tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'chi_p', 'eccentricity', 'mean_anomaly'],
        'IMRPhenomXPNR': ['eccentricity', 'mean_anomaly'],
        'IMRPhenomXPHM': ['eccentricity', 'mean_anomaly'],
        'IMRPhenomTPHM': ['eccentricity', 'mean_anomaly'],
        'IMRPhenomTEHM': ['tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'chi_p'],
        'IMRPhenomTHM_20': ['tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'chi_p', 'eccentricity', 'mean_anomaly'],
        'IMRPhenomXE': ['tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'chi_p'],
    }

    for i, (event, model_files) in enumerate(selected_pe_file_dict.items()):
        for j, (param_key, param_label) in enumerate(parameters.items()):
            ax = axes[i, j]
            ax.set_yticks([])
            for model in model_colors:
                if model in model_files:
                    color = model_colors[model]
                    if model in skip_dict and param_key in skip_dict[model]:
                        continue
                    try:
                        samples = read_samples(model_files[model], param_key)
                        ax.hist(samples, bins=60, density=True, histtype='step', lw=1.5,
                                label=model if i == 0 and j == 0 else "", color=color)
                    except Exception as e:
                        print(f"Missing {param_key} for {event} in {model}: {e}")
                        continue

            ax.set_xlabel(param_label, fontsize=16)

            if j == 0:
                event_color = get_event_color(event)
                event_group_label = None

                for group_name, event_list in {
                    'Eccentric Candidate': eccentricCandidates,
                    'Glitched Event': glitchedEvents,
                    'Problematic Event': problemEvents,
                    'Waveform Systematics LVK': waveformSystematicsLVK,
                    'Glitched + Eccentric Candidate': glitchedeccentricCandidates,
                    'Eccentric Candidate + Waveform Systematics LVK': eccentricSystematics,
                    'EccentricAEI + Waveform Systematics LVK': eccentricAEISystematics,
                    'Glitched Event + Waveform Systematics LVK': glitchedSystematics,
                    'Multimodalities': multimodalities,
                }.items():
                    if event in event_list:
                        event_group_label = group_name
                        break

                ax.set_ylabel(event, fontsize=14, color=event_color)

                if event_group_label is not None:
                    ax.set_title(f"{event_group_label}", fontsize=16, loc='left', pad=10, color=event_color)


    handles_models = [Patch(facecolor='none', edgecolor=model_colors[model], linewidth=2) for model in model_colors]
    labels_models = [model for model in model_colors]

    plt.tight_layout(rect=[0, 0, 1, 0.9])

    leg1 = fig.legend(
        handles_models, labels_models,
        loc='upper left', bbox_to_anchor=(0, 1.003),
        ncol=5, frameon=True, fontsize=16
    )

    fig.add_artist(leg1)

    plt.tight_layout(rect=[0, 0, 1, 1])
    if filename:
        plt.savefig(filename, transparent=True, bbox_inches='tight')
    else:
        plt.show()


def js_divergence_plot(pe_file_dict, parameters, outdir, eventnames=None, model_pairs=None):
    if eventnames is None:
        selected_pe_file_dict = pe_file_dict
    else:
        selected_pe_file_dict = {event: pe_file_dict[event] for event in eventnames if event in pe_file_dict}

    if model_pairs is None:
        all_models = set()
        for model_dict in selected_pe_file_dict.values():
            all_models.update(model_dict.keys())
        model_pairs = list(combinations(sorted(all_models), 2))

    color_list = ['royalblue', 'orange', 'forestgreen', 'crimson', 'purple', 'teal', 'brown', 'gold']
    marker_list = ['o', 's', 'D', '^', 'v', 'P', '*', 'X']

    all_jsd = {}
    all_comparisons = set()
    event_labels = []

    for event_idx, (event, model_dict) in enumerate(reversed(list(selected_pe_file_dict.items()))):
        event_labels.append(event)

        samples = {}
        for model, path in model_dict.items():
            try:
                samples[model] = read_samples(path, parameters)
            except Exception as e:
                print(f"Error reading samples for {event} {model} in file {path}: {e}")
                raise e

        for model1, model2 in model_pairs:
            if model1 not in samples or model2 not in samples:
                continue

            comp_key = f"{model1} vs {model2}"
            all_comparisons.add(comp_key)
            if comp_key not in all_jsd:
                all_jsd[comp_key] = {param: [np.nan]*event_idx for param in parameters}

            for param in parameters:
                s0 = samples[model1].get(param)
                s1 = samples[model2].get(param)

                if s0 is None or s1 is None:
                    js = np.nan
                else:
                    try:
                        js = jensen_shannon_divergence_from_samples([s0, s1])
                    except Exception as e:
                        print(f"{event} {comp_key} {param}: Error computing JSD – {e}")
                        js = np.nan

                while len(all_jsd[comp_key][param]) < event_idx:
                    all_jsd[comp_key][param].append(np.nan)
                all_jsd[comp_key][param].append(js)

    n_events = len(event_labels)
    for comp in all_comparisons:
        for param in parameters:
            while len(all_jsd[comp][param]) < n_events:
                all_jsd[comp][param].append(np.nan)

    comparisons = sorted(all_comparisons)
    colors = {comp: color_list[i % len(color_list)] for i, comp in enumerate(comparisons)}
    markers = {comp: marker_list[i % len(marker_list)] for i, comp in enumerate(comparisons)}

    n_params = len(parameters)
    fig, axes = plt.subplots(2, n_params, figsize=(3.5*n_params, 0.5*n_events + 4), gridspec_kw={"height_ratios": [1.5, n_events]}, sharex='col')

    for i, param in enumerate(parameters):
        ax_hist = axes[0, i]
        ax_main = axes[1, i]
        ax_main.set_yticks(np.arange(n_events))
        
        yticks = np.arange(n_events)
        yticklabels = event_labels
        ax_main.set_yticklabels(yticklabels if i == 0 else [])
        if i == 0:
            for tick_label, event in zip(ax_main.get_yticklabels(), event_labels):
                tick_label.set_color(get_event_color(event))

        ax_main.set_xscale("log")
        ax_hist.set_xscale("log")

        for comp in comparisons:
            js_values = np.array(all_jsd[comp][param])
            y = np.arange(n_events)
            x = js_values
            ax_main.scatter(x, y, label=comp if i == 0 else "", color=colors[comp], marker=markers[comp], s=60, alpha=0.6)

            valid = x[~np.isnan(x)]
            if valid.size > 0:
                ax_hist.hist(valid, bins=np.logspace(np.log10(valid.min()), np.log10(valid.max()), 20), histtype="step", color=colors[comp], lw=1.5, density=False)

        ax_main.axvline(0.02, color='darkred', linestyle='--', linewidth=1)
        ax_hist.axvline(0.02, color='darkred', linestyle='--', linewidth=1)
        ax_main.set_ylim(-1, n_events)
        ax_main.grid(True, axis='x', linestyle=':', alpha=0.4)

    for ax, param in zip(axes[1], parameters):
        ax.set_xlabel(parameters[param] + r" [JSD (bits)]", fontsize=14)

    handles = [Line2D([], [], marker=markers[comp], linestyle='None', color=colors[comp], markersize=10, label=comp, alpha=0.6)
        for comp in comparisons]
    handles_event_groups = [Patch(color=color, label=group)
                            for group, color in event_group_colors.items()]

    leg1 = fig.legend(
        handles, [h.get_label() for h in handles],
        loc='upper left', bbox_to_anchor=(0, 1.016),
        ncol=3, frameon=True, fontsize=16)
    leg2 = fig.legend(handles_event_groups, list(event_group_colors.keys()),
                      loc='upper left', bbox_to_anchor=(0, 1.), ncol=4,
                      frameon=True, fontsize=16)
    
    fig.add_artist(leg1)
    fig.add_artist(leg2)
    
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    if outdir:
        plt.savefig(outdir+'/js-divergence.png', transparent=True, bbox_inches='tight')
    else:
        plt.show()


def event_posterior_plot(event, model_files, parameters, axes):
    skip_dict = {
        'IMRPhenomTHM': ['tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'chi_p', 'eccentricity', 'mean_anomaly'],
        'IMRPhenomXPNR': ['eccentricity', 'mean_anomaly'],
        'IMRPhenomXPHM': ['eccentricity', 'mean_anomaly'],
        'IMRPhenomTPHM': ['eccentricity', 'mean_anomaly'],
        'IMRPhenomTEHM': ['tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'chi_p'],
        'IMRPhenomTHM_20': ['tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'chi_p', 'eccentricity', 'mean_anomaly'],
        'IMRPhenomXE': ['tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'chi_p'],
    }

    for j, (param_key, param_label) in enumerate(parameters.items()):
        ax = axes[j]
        ax.set_yticks([])
        for model in model_colors:
            if model in model_files:
                color = model_colors[model]
                if model in skip_dict and param_key in skip_dict[model]:
                    continue
                try:
                    samples = read_samples(model_files[model], param_key)
                    ax.hist(samples, bins=60, density=True, histtype='step', lw=1.5,
                            label=model if j == 0 else "", color=color)
                except Exception as e:
                    print(f"Missing {param_key} for {event} in {model}: {e}")
                    continue

        ax.set_xlabel(param_label, fontsize=16)
        if j == 0:
            event_color = get_event_color(event)
            event_group_label = None

            for group_name, event_list in {
                'Eccentric Candidate': eccentricCandidates,
                'Glitched Event': glitchedEvents,
                'Problematic Event': problemEvents,
                'Waveform Systematics LVK': waveformSystematicsLVK,
                'Glitched + Eccentric Candidate': glitchedeccentricCandidates,
                'Eccentric Candidate + Waveform Systematics LVK': eccentricSystematics,
                'EccentricAEI + Waveform Systematics LVK': eccentricAEISystematics,
                'Glitched Event + Waveform Systematics LVK': glitchedSystematics,
                'Multimodalities': multimodalities,
            }.items():
                if event in event_list:
                    event_group_label = group_name
                    break

            ax.set_ylabel(event, fontsize=14, color=event_color)

            if event_group_label is not None:
                ax.set_title(f"{event_group_label}", fontsize=16, loc='left', pad=10, color=event_color)


def catalog_posterior_plot(pe_file_dict, parameters, outdir, eventnames=None):
    n_params = len(parameters)
    event_data = {}
    for event, model_files in pe_file_dict.items():
        fig, axes = plt.subplots(nrows=1, ncols=n_params, figsize=(3*n_params, 2.5*1), sharex=False, sharey=False)
        fig.subplots_adjust(wspace=0.3, hspace=0.3)
        event_posterior_plot(event, model_files, parameters, axes)
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"plots/{event}_posteriors.png"), transparent=True, bbox_inches='tight')
        plt.close()

        event_group_label = []
        for group_name, event_list in {
            'Eccentric Candidate': eccentricCandidates,
            'Glitched Event': glitchedEvents,
            'Problematic Event': problemEvents,
            'Waveform Systematics LVK': waveformSystematicsLVK,
        }.items():
            if event in event_list:
                event_group_label.append(group_name)
        event_data[event] = {
            'labels': event_group_label,
            'eccentricity': {
                'median': 0.1,
            },
            'total_mass': {
                'median': 50,
            },
            'mass_ratio': {
                'median': 0.5,
            },
            'snr_H1': {
                'median': 100,
            },
            'snr_L1': {
                'median': 100,
            },
            'snr_network': {
                'median': 100,
            },
        }

        html_str = plot_page(event_data)
        with open(os.path.join(outdir, f"plots/{event}_posteriors.html"), 'w') as f:
            f.write(html_str)


def plot_page(data_dict):
    template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Event Viewer</title>
<style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }
    th { background-color: #f4f4f4; }
    .label-badge { 
        background-color: #eee; 
        border-radius: 4px; 
        padding: 2px 6px; 
        margin: 0 4px; 
        font-size: 0.85em;
    }
    .plot-row td {
        text-align: center;
        background-color: #fafafa;
    }
    .plot-row img {
        max-width: 100%;
        height: auto;
    }
    .sortable { cursor: pointer; color: blue; text-decoration: underline; }
    .filters { margin-bottom: 15px; }
</style>
</head>
<body>

<h1>Event Viewer</h1>

<div class="filters">
    <label for="labelFilter">Filter by Label:</label>
    <select id="labelFilter">
        <option value="">-- All --</option>
    </select>
</div>

<table id="eventsTable">
    <thead>
        <tr>
            <th>Event</th>
            <th>Labels</th>
            <th class="sortable" onclick="sortTable('eccentricity')">Eccentricity (median)</th>
            <th class="sortable" onclick="sortTable('total_mass')">Total Mass (median)</th>
            <th class="sortable" onclick="sortTable('mass_ratio')">Mass Ratio (median)</th>
            <th class="sortable" onclick="sortTable('snr_H1')">SNR H1 (median)</th>
            <th class="sortable" onclick="sortTable('snr_L1')">SNR L1 (median)</th>
            <th class="sortable" onclick="sortTable('snr_network')">SNR Network (median)</th>
        </tr>
    </thead>
    <tbody></tbody>
</table>

<script>
const data = {};

let sortDirection = 1;

function populateTable() {
    const tbody = document.querySelector("#eventsTable tbody");
    tbody.innerHTML = "";
    const selectedLabel = document.getElementById("labelFilter").value;

    for (const [name, event] of Object.entries(data)) {
        if (selectedLabel && !event.labels.includes(selectedLabel)) continue;

        // Metadata row
        const metaRow = document.createElement("tr");
        metaRow.innerHTML = `
            <td>${name}</td>
            <td>${event.labels.map(l => `<span class="label-badge">${l}</span>`).join("")}</td>
            <td>${event.eccentricity.median}</td>
            <td>${event.total_mass.median}</td>
            <td>${event.mass_ratio.median}</td>
            <td>${event.snr_H1.median}</td>
            <td>${event.snr_L1.median}</td>
            <td>${event.snr_network.median}</td>
        `;
        tbody.appendChild(metaRow);

        // Plot row
        const plotRow = document.createElement("tr");
        plotRow.className = "plot-row";
        const plotCell = document.createElement("td");
        plotCell.colSpan = 8;
        plotCell.innerHTML = `<img src="${name}_posteriors.png" alt="${name}_posteriors plot">`;
        plotRow.appendChild(plotCell);
        tbody.appendChild(plotRow);
    }
}

function populateLabelFilter() {
    const select = document.getElementById("labelFilter");
    const labels = new Set();
    for (const event of Object.values(data)) {
        event.labels.forEach(l => labels.add(l));
    }
    for (const label of labels) {
        const option = document.createElement("option");
        option.value = label;
        option.textContent = label;
        select.appendChild(option);
    }
}

function sortTable(param) {
    const entries = Object.entries(data);
    entries.sort((a, b) => sortDirection * (a[1][param].median - b[1][param].median));
    sortDirection *= -1;
    const sortedData = {};
    for (const [name, event] of entries) sortedData[name] = event;
    Object.assign(data, sortedData);
    populateTable();
}

document.getElementById("labelFilter").addEventListener("change", populateTable);

populateLabelFilter();
populateTable();
</script>

</body>
</html>"""
    return template.replace("data = {};", f"data = {json.dumps(data_dict, indent=4)};")