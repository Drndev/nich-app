#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests

# Your Mapbox access token
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiZGFyZGV2IiwiYSI6ImNsdWNnbTltcDExdmYyam5pazdtOGZ1MGwifQ.IBDBUPNj10UCQ9jMTV-pjA"
px.set_mapbox_access_token(MAPBOX_ACCESS_TOKEN)

# Modified link for direct download from Google Drive
google_drive_link = "https://drive.google.com/uc?export=download&id=1ZMR271ltgXgYfBNmzd4rb49H2IzpqJXx"

# Download the file from the link
response = requests.get(google_drive_link)

# Save the downloaded content to a local file
with open("Total.csv", "wb") as f:
    f.write(response.content)

# Read the CSV file into a Pandas DataFrame
df = pd.read_csv("Total.csv", encoding='ISO-8859-1', on_bad_lines='skip')

# Further processing...
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests

# Your Mapbox access token
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiZGFyZGV2IiwiYSI6ImNsdWNnbTltcDExdmYyam5pazdtOGZ1MGwifQ.IBDBUPNj10UCQ9jMTV-pjA"
px.set_mapbox_access_token(MAPBOX_ACCESS_TOKEN)

# Modified link for direct download from Google Drive
google_drive_link = "https://drive.google.com/uc?export=download&id=1ZMR271ltgXgYfBNmzd4rb49H2IzpqJXx"

# Download the file from the link
response = requests.get(google_drive_link)

# Save the downloaded content to a local file
with open("Total.csv", "wb") as f:
    f.write(response.content)

# Read the CSV file into a Pandas DataFrame
df = pd.read_csv("Total.csv", encoding='ISO-8859-1', on_bad_lines='skip')

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
    html.Div(id='point-count', style={'textAlign': 'center'}),  # Div to display the point count
    html.Div(style={'display': 'flex', 'flexDirection': 'row', 'height': 'calc(100vh - 40px)'}, children=[
        # Map container
        html.Div(style={'flex': 3}, children=[
            dcc.Graph(id="map", style={'height': '100%'})
        ]), 
        # Filters container with adjusted width
        html.Div(style={
            'flex': 1,
            'flexBasis': '350px',  # The ideal/initial width
            'maxWidth': '400px',  
            'marginLeft': '20px',
            'verticalAlign': 'top',
            'font-family': 'Roboto',
            'padding': '20px',
            'backgroundColor': 'white',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'overflowY': 'auto',
            'maxHeight': 'calc(100vh - 60px)'  # Max height to ensure it does not overflow the viewport
        }, children=[
            html.H2("Filters", style={'font-family': 'Roboto', 'font-weight': '500', 'textAlign': 'center'}),
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
            )
        ])
    ])
], style={'padding': '20px', 'backgroundColor': '#f0f0f0', 'font-family': 'Roboto', 'height': '100vh', 'margin': '0'})

# Callback to update the map based on filters and display the point count
@app.callback(
    [Output('map', 'figure'),
     Output('point-count', 'children')],
    [Input('siccode-dropdown', 'value'),
     Input('companyname-dropdown', 'value')]
)
def update_map(selected_siccodes, selected_companynames):
    filtered_df = df
    if selected_siccodes:
        filtered_df = filtered_df[df['SICCode'].isin(selected_siccodes)]
    if selected_companynames:
        filtered_df = filtered_df[filtered_df['CompanyName'].isin(selected_companynames)]

    fig = px.scatter_mapbox(filtered_df, lat="Latitude", lon="Longitude",
                            hover_name="CompanyName",
                            hover_data={"CompanyNumber": True, "SICCode": True, "RegAddress.AddressLine1": True},
                            zoom=7,
                            mapbox_style="mapbox://styles/mapbox/satellite-streets-v12",
                            title="NI Companies House")
    fig.update_layout(mapbox_center={"lat": 54.637039, "lon": -6.627607},
                      margin={"r":0,"t":0,"l":0,"b":0}, autosize=True)

    point_count = f"Number of points plotted: {len(filtered_df)}"  # Generate point count string
    return fig, point_count

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
