# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 18:13:21 2020

@author: FFernandes
"""


# Libbraries importing section
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import requests
import pandas as pd
import json
from urllib.request import Request, urlopen



#Reading data section

## Reading maps  #Those maps were prepared before construction of these program
with open('Maps/brasil_1.json', encoding='utf-8') as geofile1:
    jdataBra_states = json.load(geofile1)

'''
with open('Deployment\brasil_2.json', encoding='utf-8') as geofile2:
    jdataBra_rgintermed = json.load(geofile2)

with open('Deployment\brasil_3.json', encoding='utf-8') as geofile3:
    jdataBra_rgimed = json.load(geofile3)
    
with open('Deployment\brasil_4.json', encoding='utf-8') as geofile4:
    jdataBra_municipios = json.load(geofile4)
'''


## Reading info from Brasil.IO

req = Request('https://brasil.io/dataset/covid19/caso?format=csv', headers={'User-Agent': 'Mozilla/5.0'})
data_covidbr = pd.read_csv(urlopen(req), 
                      dtype = {'city_ibge_code': 'object'},
                      parse_dates = ['date'])

### Keeping only the needed info
data_covidbr = data_covidbr[(data_covidbr['place_type'] == 'city') & (data_covidbr['is_last'])]
## is_last tells us that we are working the most up-to-date data.


#Organizing data section
data_covidbr.drop(axis = 1, labels = ['date', 
                                      'place_type', 
                                      'is_last', 
                                      'estimated_population_2019', 
                                      'confirmed_per_100k_inhabitants', 
                                      'death_rate'], inplace = True)
    
df_states = data_covidbr.groupby(by = 'state').sum()
locations_states = df_states.index



#Creating the core of the dashboard
app = dash.Dash()

server = app.server #Disable it when in test / development mode. Enable it to Production mode
app.layout = html.Div([
        html.Div(html.H1('Painel COVID-19 nos municípios, regiões geográficas imediatas e intermediárias e estados brasileiros')),
        html.Div(dcc.Graph(id = 'main_map',
                           figure = {
                                   'data': [go.Choroplethmapbox(geojson = jdataBra_states,
                                                                locations = locations_states,
                                                                z = df_states['deaths'],
                                                                featureidkey = 'properties.SIGLA_UF',
                                                                colorscale = 'RdPu')],
                                   'layout': go.Layout(
                                           title = 'Mapa de óbitos por estados brasileiro',
                                           hovermode = 'closest',
                                           mapbox={'zoom': 3,
                                                   'style': 'carto-positron',
                                                   'center': {"lat": -15, "lon": -60}})
                                   } #closing figure
    )) #closing html.Div
    ]) #closing main html.Div

    
    
if __name__ == '__main__':
    app.run_server()

'''
@app.callback(Output('counter_text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_layout(n):
    url = "https://data-live.flightradar24.com/zones/fcgi/feed.js?faa=1\
           &mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&stats=1"
    # A fake header is necessary to access the site:
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = res.json()
    counter = 0
    for element in data["stats"]["total"]:
        counter += data["stats"]["total"][element]
    counter_list.append(counter)
    return 'Active flights worldwide: {}'.format(counter)

@app.callback(Output('live-update-graph','figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph(n):
    fig = go.Figure(
        data = [go.Scatter(
        x = list(range(len(counter_list))),
        y = counter_list,
        mode='lines+markers'
        )])
    return fig

if __name__ == '__main__':
    app.run_server()
'''