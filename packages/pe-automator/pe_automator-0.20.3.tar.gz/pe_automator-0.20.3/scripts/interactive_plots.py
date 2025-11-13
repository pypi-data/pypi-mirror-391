import streamlit as st
import pandas as pd
import plotly.express as px
import h5py
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder
# import streamlit_authenticator as stauth

st.set_page_config(layout="wide")


def collapse_with_error(df):
    result = pd.DataFrame(index=df.index)
    if 'superevent_id' in df.columns:
        result['superevent_id'] = df['superevent_id'].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)

    for base in set(col.rsplit('_', 1)[0] for col in df.columns):
        try:
            result[base] = df[f"{base}_median"].round(3).astype(str) + \
                           " (" + df[f"{base}_lower"].round(3).astype(str) + \
                           " - " + df[f"{base}_upper"].round(3).astype(str) + ")"
        except KeyError:
            pass  # In case any xxx_lower/upper is missing
    return result

def collapse_without_error(df):
    result = pd.DataFrame(index=df.index)
    if 'superevent_id' in df.columns:
        result['superevent_id'] = df['superevent_id'].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)

    for base in set(col.rsplit('_', 1)[0] for col in df.columns):
        try:
            result[base] = df[f"{base}_median"].round(3)
        except KeyError:
            pass  # In case any xxx_median is missing
    return result


gwtc4 = h5py.File('../data/IGWN-GWTC4-fbbc2a80e_720-PESummaryTable.hdf5', 'r')
summary_info = gwtc4['summary_info']
# Convert to a pandas DataFrame
df = pd.DataFrame(summary_info[:])

event_list = set(df['gw_name'])

df_filtered = df.copy()
for event in event_list:
    if event == b'GW230529_181500':
        df_filtered = df_filtered[(df_filtered['gw_name'] != event) | (df_filtered['result_samples_key'] == b'C00:IMRPhenomXPHM:LowSpinSecondary:Mixed')]
    elif event == b'GW230518_125908':
        df_filtered = df_filtered[(df_filtered['gw_name'] != event) | (df_filtered['result_samples_key'] == b'C00:IMRPhenomXPHM-SpinTaylor')]
    else:
        df_filtered = df_filtered[(df_filtered['gw_name'] != event) | (df_filtered['result_samples_key'] == b'C00:Mixed')]

df = df_filtered.reset_index(drop=True)


# Assume df is your original DataFrame
display_df = collapse_without_error(df)
display_df['mass_ratio'] = display_df['mass_1_source'] / display_df['mass_2_source']
display_df['mass_ratio'] = display_df['mass_ratio'].round(3)

st.title("Sortable & Filterable Table with Errors")

# AgGrid for sortable, filterable table
gb = GridOptionsBuilder.from_dataframe(display_df)
gb.configure_default_column(filterable=True, sortable=True, resizable=True)
grid_options = gb.build()

AgGrid(display_df, gridOptions=grid_options, height=400, enable_enterprise_modules=True)

# plot total_mass_source - SNR 2d plot with superevent_id as hover data
st.title("2D Plot of the Parameters")

# plot the mass_1_source - mass_2_source 2d plot with superevent_id as hover data, SNR as color
fig = px.scatter(display_df,
                x='mass_1_source', 
                y='mass_2_source', 
                color='network_matched_filter_snr', 
                    color_continuous_scale=px.colors.sequential.Viridis,
                hover_data=['superevent_id', 'mass_1_source', 'mass_2_source', 'mass_ratio'],
                title="Mass 1 Source vs Mass 2 Source (Colored by SNR)")
# plot the reference line for mass_1_source = mass_2_source, mass_1_source = 2 * mass_2_source
fig.add_shape(type='line', 
            x0=0, y0=0, x1=140, y1=140, 
            line=dict(color='red', width=1, dash='dash'), 
            name='q=1')
# add the text annotation for the line
fig.add_annotation(x=130, y=130, text='q=1', showarrow=False, font=dict(color='red'))
fig.add_shape(type='line',
            x0=0, y0=0, x1=140, y1=70, 
            line=dict(color='blue', width=1, dash='dash'), 
            name='q=2')
# add the text annotation for the line
fig.add_annotation(x=130, y=65, text='q=2', showarrow=False, font=dict(color='blue'))
# set the x range to be the same as y range
# fig.update_xaxes(type='log',range=[0.1, np.log10(140)], title_text='Mass 1 Source (Solar Masses)')
# fig.update_yaxes(type='log',range=[0.1, np.log10(140)], title_text='Mass 2 Source (Solar Masses)')
fig.update_xaxes(range=[0.1, 140], title_text='Mass 1 Source (Solar Masses)')
fig.update_yaxes(range=[0.1, 140], title_text='Mass 2 Source (Solar Masses)')


st.plotly_chart(fig)

fig = px.scatter(display_df, 
                x='total_mass_source', 
                y='network_matched_filter_snr', 
                color='mass_ratio', 
                hover_data=['superevent_id', 'mass_ratio'],
                title="Total Mass Source vs Network Matched Filter SNR")
st.plotly_chart(fig)

# plot mass_ratio - SNR 2d plot with superevent_id as hover data
fig = px.scatter(display_df, 
                x='mass_ratio', 
                y='network_matched_filter_snr', 
                color='total_mass_source', 
                hover_data=['superevent_id', 'total_mass_source'],
                title="Mass Ratio vs Network Matched Filter SNR")
st.plotly_chart(fig)

# plot the total_mass_source - mass_ratio 2d plot with superevent_id as hover data, SNR as color
fig = px.scatter(display_df, 
                x='total_mass_source', 
                y='mass_ratio', 
                color='network_matched_filter_snr', 
                hover_data=['superevent_id'],
                title="Total Mass Source vs Mass Ratio (Colored by SNR)")
st.plotly_chart(fig)


# Select columns for distribution plots
selected_columns = [
    'total_mass_source', 
    'chirp_mass_source',
    'mass_1_source',
    'mass_2_source',
    'final_mass_source',
    'chi_eff',
    'final_spin',
    'luminosity_distance',
    'redshift', 
    'network_matched_filter_snr']


# Loop through columns and plot distribution if numeric
for col in display_df.select_dtypes(include='number').columns:
    st.subheader(f"Distribution of {col}")
    fig = px.histogram(display_df, x=col, nbins=30, title=f"{col} Distribution")
    st.plotly_chart(fig)


# names = ['UIB']
# usernames = ['uib']
# passwords = ['imrphenomxxx']

# config = {
#     'credentials': {
#         'usernames': {username: {'name': name, 'password': password} for name, username, password in zip(names, usernames, passwords)}
#     },
#     'cookie': {
#         'expiry_days': 30,
#         'key': 'cookie_key',
#         'name': 'cookie_name'
#     },
# }
# authenticator = stauth.Authenticate(
#     config['credentials'],
#     config['cookie']['name'],
#     config['cookie']['key'],
#     config['cookie']['expiry_days'],
# )

# try:
#     authenticator.login()
# except Exception as e:
#     st.error(f"An error occurred during authentication: {e}")
#     st.stop()

# if st.session_state.get('authentication_status'):
#     authenticator.logout()
# elif st.session_state.get('authentication_status') is False:
#     st.error('Username/password is incorrect')
# elif st.session_state.get('authentication_status') is None:
#     st.warning('Please enter your username and password')
# else:
#     st.error('An unexpected error occurred during authentication.')
#     st.stop()