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
import dash_daq as daq


'''
Source of Population Info: https://www.ibge.gov.br/estatisticas/sociais/populacao/9103-estimativas-de-populacao.html?edicao=25272&t=downloads
Source of Maps: https://www.ibge.gov.br/geociencias/organizacao-do-territorio/15774-malhas.html?=&t=downloads
Source of COVID data: https://brasil.io/dataset/covid19/caso?format=csv
'''


#Reading data section

## Reading maps  #Those maps were prepared before construction of these program
with open('Maps/brasil_1.json', encoding='utf-8') as geofile1:
    jdataBra_states = json.load(geofile1)


with open('Maps/brasil_2.json', encoding='utf-8') as geofile2:
    jdataBra_rgintermed = json.load(geofile2)

with open('Maps/brasil_3.json', encoding='utf-8') as geofile3:
    jdataBra_rgimed = json.load(geofile3)

   
with open('Maps/brasil_4.json', encoding='utf-8') as geofile4:
    jdataBra_municipios = json.load(geofile4)


## Reading info about geographical locations
path_info_rg = 'Tables/regioes_geograficas_composicao_por_municipios_2017_20180911.xlsx'
info_rg = pd.read_excel(path_info_rg, dtype = 'object')


## Reading info from Brasil.IO

req = Request('https://brasil.io/dataset/covid19/caso?format=csv', headers={'User-Agent': 'Mozilla/5.0'})
data_covidbr = pd.read_csv(urlopen(req), 
                      dtype = {'city_ibge_code': 'object'},
                      parse_dates = ['date'])
data_covidbr = data_covidbr[(data_covidbr['place_type'] == 'city')]

### Keeping only the updated info
current_data_covidbr = data_covidbr[data_covidbr['is_last']][:]
## is_last tells us that we are working the most up-to-date data.


#Organizing data section
current_data_covidbr.drop(axis = 1, labels = ['date', 
                                              'place_type', 
                                              'is_last', 
                                              'estimated_population_2019', 
                                              'confirmed_per_100k_inhabitants', 
                                              'death_rate'], inplace = True)


df_states_current = current_data_covidbr.groupby(by = 'state').sum()
df_mun_current = current_data_covidbr[:]

### Combining to get rgi and rgintermed info
data_covidbr_combo = current_data_covidbr.merge(info_rg, 
                                                left_on = 'city_ibge_code', 
                                                right_on = 'CD_GEOCODI', 
                                                how = 'outer')
df_rgi_current = data_covidbr_combo.groupby(by = 'nome_rgi').sum()
df_rgintermed_current = data_covidbr_combo.groupby(by = 'nome_rgint').sum()


### Summing up total numbers
total_cases = df_states_current['confirmed'].sum()
total_deaths = df_states_current['deaths'].sum()


locations_states = df_states_current.index
locations_rgintermed = df_rgintermed_current.index
locations_rgi = df_rgi_current.index
locations_mun = df_mun_current['city']




#Creating the core of the dashboard
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 

server = app.server #Disable it when in test / development mode. Enable it to Production mode
app.layout = html.Div([
        dcc.Store(id="store_data"), #later understand why this is useful
        
        html.Div(html.H1('Painel COVID-19 nas localidades brasileiras')),
        
        html.Div([
                html.Div(
                    [
                        daq.LEDDisplay(id='cases-LED-display',
                                label= 'Total de casos confirmados no Brasil',
                                value=total_cases, color = 'black')
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        daq.LEDDisplay(id='deaths-LED-display',
                                label= 'Total de óbitos confirmados no Brasil',
                                value=total_deaths, color = 'black')
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"}), #closing Div with overall scores
        
        html.Div([html.Div('Selecione o nível de organização do território:'),
                dcc.Dropdown(id = 'dropdown_geo_level', 
                               options = [
                                       {'label': 'Estados', 'value': 'states'},
                                       {'label': 'Regiões Geográficas Intermediárias', 'value': 'rgintermed'}, 
                                       {'label': 'Regiões Geográficas Intermediárias', 'value': 'rgi'}, 
                                       {'label': 'Municípios', 'value': 'cities'}
                                       ], 
                               value = 'states', 
                               multi = False)]),
        
        
        html.Div([html.Div('Selectione o tipo de informação:'),
                dcc.Dropdown(id = 'dropdown_info', 
                               options = [
                                       {'label': 'Total de casos', 'value': 'confirmed'},
                                       {'label': 'Total de óbitos', 'value': 'deaths'}, 
                                       #{'label': 'Total de casos por habitantes', 'value': 'confirmed_per_pop'}, 
                                       #{'label': 'Total de óbitos por habitantes', 'value': 'deaths_per_pop'}
                                       ], 
                               value = 'confirmed', 
                               multi = False)]), ### closing Div-Div-Dropdown
        
        
        html.Div(dcc.Graph(id = 'main_map'), #closing dcc.Graph
    #style={'width':1000, 'height':800, 'border':'2px black'}
    ), ### closing Div-Graph
    
        html.Div(dcc.Markdown('''
                              Os dados reportados neste painel foram obtidos na plataforma Brasil.IO, repositório de dados públicos disponibilizados em formato acessível. Conheça e apoie esta iniciativa.
                              
                              https://brasil.io/home/
                              
                              
                              
                              Os mapas foram obtidos no site do IBGE em formato shapefile e simplificados usando a biblioteca Geopandas.
                              ''') #closing Markdown
        ) ### closing Div-Markdown
]) #closing main html.Div
        
        
        
        
        
        
        
# Callbacks - here is where the magic happens
@app.callback(Output('main_map', 'figure'),
              [Input('dropdown_info', 'value'),
               Input('dropdown_geo_level', 'value')])
def update_figure(info, geo_level):
    ### according to the geo_level, we'll choose the right DataFrame
    if geo_level == 'states':
        df = df_states_current
        locations = locations_states
        geojson = jdataBra_states
        featureidkey = 'properties.SIGLA_UF'
    elif geo_level == 'rgintermed':
        df = df_rgintermed_current
        locations = locations_rgintermed
        geojson = jdataBra_rgintermed
        featureidkey='properties.NM_RGINT'
    elif geo_level == 'rgi':
        df = df_rgi_current
        locations = locations_rgi
        geojson = jdataBra_rgimed
        featureidkey = featureidkey='properties.NM_RGI'
    elif geo_level == 'cities':
        df = df_mun_current
        locations = locations_mun
        geojson = jdataBra_municipios
        featureidkey = featureidkey='properties.NM_MUN'
    else:  #else select states
        df = df_states_current
        locations = locations_states
        geojson = jdataBra_states
        featureidkey = 'properties.SIGLA_UF'
        
     
    figure = {'data': [go.Choroplethmapbox(geojson = geojson,
                                           locations = locations,
                                           z = df[info],
                                           featureidkey = featureidkey,
                                           colorscale = 'RdPu')],
                'layout': go.Layout(
                                           #title = 'Mapa de óbitos por estados brasileiro',
                                           hovermode = 'closest',
                                           width = 1000,
                                           height = 700,
                                           mapbox={'zoom': 3,
                                                   'style': 'carto-positron',
                                                   'center': {"lat": -15, "lon": -60}})
                                   } #closing figure
                                   
    return figure
    
    
    
    
if __name__ == '__main__':
    app.run_server()

