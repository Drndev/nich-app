#!/usr/bin/env python
# coding: utf-8

# In[2]:


import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Your Mapbox access token
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiZGFyZGV2IiwiYSI6ImNsdWNnbTltcDExdmYyam5pazdtOGZ1MGwifQ.IBDBUPNj10UCQ9jMTV-pjA"
px.set_mapbox_access_token(MAPBOX_ACCESS_TOKEN)

# Read in the data
df = pd.read_csv('Downloads/Finished/Total.csv', encoding='ISO-8859-1')
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Mapping of Companies House Northern Ireland", style={'font-family': 'Roboto', 'font-weight': '500', 'textAlign': 'center'}),
    html.Div(style={'display': 'flex', 'flexDirection': 'row', 'height': 'calc(100vh - 40px)'}, children=[
        # Map container
        html.Div(style={'flex': 3}, children=[
            dcc.Graph(id="map", style={'height': '100%'})
        ]), 
        # Filters container with adjusted width
        html.Div(style={
            'flex': 1,
            'flexBasis': '350px',  # The ideal or initial width
            'maxWidth': '350px',  # Ensures the filter box doesn't grow beyond this width
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

# Callback to update the map based on filters
@app.callback(
    Output('map', 'figure'),
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

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:





# In[1]:


pip freeze


# In[2]:


jupyter nbconvert --to script MyDashApp.ipynb


# In[3]:


print(os.getcwd())


# In[4]:


pwd


# In[ ]:




