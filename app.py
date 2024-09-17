#!/usr/bin/env python
# coding: utf-8

import os
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests

# Your Mapbox access token
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiZGFyZGV2IiwiYSI6ImNsdWNnbTltcDExdmYyam5pazdtOGZ1MGwifQ.IBDBUPNj10UCQ9jMTV-pjA"
px.set_mapbox_access_token(MAPBOX_ACCESS_TOKEN)

# Modified link for direct download from Google Drive
google_drive_link = "https://drive.google.com/uc?export=download&id=1ZMR271ltgXgYfBNmzd4rb49H2IzpqJXx"

# Download the file from the link with error handling
try:
    response = requests.get(google_drive_link)
    response.raise_for_status()  # Raise an error for bad responses
except requests.RequestException as e:
    print(f"Error downloading CSV: {e}")
    df = pd.DataFrame()  # Create an empty DataFrame if the download fails

# Save the downloaded content to a local file
data_file = os.path.join(os.getcwd(), "Total.csv")
with open(data_file, "wb") as f:
    f.write(response.content)

# Read the CSV file into a Pandas DataFrame
df = pd.read_csv(data_file, encoding='ISO-8859-1', on_bad_lines='skip')

# Further processing...
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the layout of the app
app.layout = html.Div([
    html.H1("Mapping of Companies House Northern Ireland", style={'font-family': 'Roboto', 'font-weight': '500', 'textAlign': 'center'}),
    html.Div(id='point-count', style={'textAlign': 'center'}),
    html.Div(style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'stretch', 'marginBottom': '20px'}, children=[
        html.Div(style={'flex': '3', 'height': '90vh'}, children=[
            dcc.Graph(id="map", style={'height': '100%', 'width': '100%'}),
        ]),
        html.Div(style={
            'flex': '1',
            'minWidth': '250px',
            'font-family': 'Roboto',
            'padding': '20px',
            'backgroundColor': 'white',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'overflowY': 'auto',
            'height': '500px'
        }, children=[
            html.H2("Filters", style={'font-family': 'Roboto', 'font-weight': '500'}),
            dcc.Dropdown(
                id='siccode-dropdown',
                options=[{'label': sic, 'value': sic} for sic in df['SICCode'].unique()],
                value=None,
                placeholder="Select a SICCode",
                multi=True
            ),
            dcc.Dropdown(
                id='companyname-dropdown',
                options=[{'label': name, 'value': name} for name in sorted(df['CompanyName'].unique())],
                value=None,
                placeholder="Select a Company Name",
                multi=True
            ),
            html.Button('Reset Filters', id='reset-button', n_clicks=0),
        ])
    ]),
    html.Div(id='table-container', style={'width': '80%', 'margin': '0 auto', 'marginTop': '20px'}),
], style={'padding': '20px', 'backgroundColor': '#f0f0f0', 'font-family': 'Roboto', 'margin': '0 auto', 'width': '90%'})

# Callback to update the map and the table based on filters
@app.callback(
    [Output('map', 'figure'),
     Output('point-count', 'children'),
     Output('table-container', 'children')],
    [Input('siccode-dropdown', 'value'),
     Input('companyname-dropdown', 'value'),
     Input('reset-button', 'n_clicks')]
)
def update_content(selected_siccodes, selected_companynames, n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]['prop_id'].split('.')[0] == 'reset-button':
        selected_siccodes = selected_companynames = None  # Resetting filters
    
    filtered_df = df
    if selected_siccodes:
        filtered_df = filtered_df[df['SICCode'].isin(selected_siccodes)]
    if selected_companynames:
        filtered_df = filtered_df[filtered_df['CompanyName'].isin(selected_companynames)]

    fig = px.scatter_mapbox(filtered_df, lat="Latitude", lon="Longitude",
                            hover_name="CompanyName",
                            hover_data={"CompanyNumber": True, "SICCode": True, "RegAddress.AddressLine1": True},
                            zoom=7.4,
                            mapbox_style="mapbox://styles/mapbox/satellite-streets-v12")
    fig.update_layout(mapbox_center={"lat": 54.637039, "lon": -6.627607},
                      margin={"r":0,"t":0,"l":0,"b":0}, autosize=True)

    point_count = f"Number of points plotted: {len(filtered_df)}"

    # Generate table only if there is data to show
    table = dash_table.DataTable(
        data=filtered_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in filtered_df.columns],
        page_size=10,  # Show 10 rows per page
        style_table={'overflowX': 'auto'},
    ) if not filtered_df.empty else html.Div()

    return fig, point_count, table

# Callback to reset the dropdowns when the reset button is clicked
@app.callback(
    [Output('siccode-dropdown', 'value'),
     Output('companyname-dropdown', 'value')],
    [Input('reset-button', 'n_clicks')],
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    # Reset the values of the dropdowns to None
    return [None, None]

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=int(os.environ.get('PORT', 8050)))  # Adjust port for Heroku
