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
import pandas as pd
import json
import dash_daq as daq
import dash_table
from dash_table.Format import Format, Group, Scheme, Symbol
import datetime as dt

'''
Source of Population Info: https://www.ibge.gov.br/estatisticas/sociais/populacao/9103-estimativas-de-populacao.html?edicao=25272&t=downloads
Source of Maps: https://www.ibge.gov.br/geociencias/organizacao-do-territorio/15774-malhas.html?=&t=downloads
Source of COVID data: https://brasil.io/dataset/covid19/caso?format=csv
'''


#Reading data section

## Reading last update info
readfile = open('last_update.txt', 'r')
last_update = readfile.readlines()
readfile.close()


## Reading maps  #Those maps were prepared before construction of these program
with open('Maps/brasil_1.json', encoding='utf-8') as geofile1:
    jdataBra_states = json.load(geofile1)


with open('Maps/brasil_2.json', encoding='utf-8') as geofile2:
    jdataBra_rgintermed = json.load(geofile2)

with open('Maps/brasil_3.json', encoding='utf-8') as geofile3:
    jdataBra_rgimed = json.load(geofile3)

   
with open('Maps/brasil_4.json', encoding='utf-8') as geofile4:
    jdataBra_municipios = json.load(geofile4)


## Reading info from the hard drive previously downloaded and manipulated file

tdf = pd.read_csv('Tables/tdf.csv',
                  parse_dates = ['data'], 
                  dtype = {'total_casos': 'int64',
                           'total_obitos': 'int64',
                           'novos_casos': 'int64',
                           'novos_obitos': 'int64',
                           'cod_rgi': 'object',
                           'cod_rgint': 'object',
                           'cod_uf': 'object'},
                           encoding = 'latin1', 
                           compression = 'gzip')
tdf = tdf.drop(axis = 1, labels = ['Unnamed: 0'])


tdf_rgi = pd.read_csv('Tables/tdf_rgi.csv',
                  parse_dates = ['data'], 
                  dtype = {'total_casos': 'int64',
                           'total_obitos': 'int64',
                           'novos_casos': 'int64',
                           'novos_obitos': 'int64'},
                           encoding = 'latin1', 
                           compression = 'gzip')
tdf_rgi = tdf_rgi.drop(axis = 1, labels = ['Unnamed: 0'])

tdf_rgint = pd.read_csv('Tables/tdf_rgint.csv',
                  parse_dates = ['data'], 
                  dtype = {'total_casos': 'int64',
                           'total_obitos': 'int64',
                           'novos_casos': 'int64',
                           'novos_obitos': 'int64'},
                           encoding = 'latin1', 
                           compression = 'gzip')
tdf_rgint = tdf_rgint.drop(axis = 1, labels = ['Unnamed: 0'])


tdf_estados = pd.read_csv('Tables/tdf_estados.csv',
                  parse_dates = ['data'], 
                  dtype = {'total_casos': 'int64',
                           'total_obitos': 'int64',
                           'novos_casos': 'int64',
                           'novos_obitos': 'int64'},
                           encoding = 'latin1', 
                           compression = 'gzip')
tdf_estados = tdf_estados.drop(axis = 1, labels = ['Unnamed: 0'])






### Keeping only the updated info

df_hoje = tdf[tdf['data'] == tdf['data'].max()].copy()
df_estados_hoje = tdf_estados[tdf_estados['data'] == tdf_estados['data'].max()].copy()
df_rgint_hoje = tdf_rgint[tdf_rgint['data'] == tdf_rgint['data'].max()].copy()
df_rgi_hoje = tdf_rgi[tdf_rgi['data'] == tdf_rgi['data'].max()].copy()

### Summing up total numbers
total_cases = df_estados_hoje['total_casos'].sum()
total_deaths = df_estados_hoje['total_obitos'].sum()




### Creating the locations for each level of geo organization
locations_states = df_estados_hoje['sigla_estado']
locations_rgintermed = df_rgint_hoje['cod_rgint']
locations_rgi =df_rgi_hoje['cod_rgi']
locations_mun = df_hoje['codigo_ibge']

#Creating the core of the dashboard
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 

server = app.server #Disable it when in test / development mode. Enable it to Production mode
app.layout = html.Div([
        #dcc.Store(id="store_data"), #later understand why this is useful
        
        html.Div(html.H1('Painel COVID-19 nas localidades brasileiras')),
        
        html.Div(html.H6(last_update)),
        
        html.Div([
                html.Div(
                    [
                        daq.LEDDisplay(id='cases-LED-display',
                                label= 'Total de casos confirmados no Brasil',
                                value=total_cases, 
                                color = 'black')
                    ],
                ),
            
                html.Div(
                    [
                        daq.LEDDisplay(id='deaths-LED-display',
                                label= 'Total de óbitos confirmados no Brasil',
                                value=total_deaths, 
                                color = 'black')
                    ]
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
                                       {'label': 'Regiões Geográficas Imediatas', 'value': 'rgi'}, 
                                       {'label': 'Municípios', 'value': 'cities'}
                                       ], 
                               value = 'states', 
                               multi = False)]),
        
        
        html.Div([html.Div('Selectione o tipo de informação:'),
                dcc.Dropdown(id = 'dropdown_info', 
                               options = [
                                       {'label': 'A - Total de casos', 'value': 'total_casos'},
                                       {'label': 'B - Total de óbitos', 'value': 'total_obitos'},
                                       {'label': 'C - Novos casos', 'value': 'novos_casos'},
                                       {'label': 'D - Novos óbitos', 'value': 'novos_obitos'},
                                       {'label': 'E - Média móvel dos novos casos - 7 dias', 'value': 'mm_7dias_novos_casos'},
                                       {'label': 'F - Média móvel dos novos óbitos - 7 dias', 'value': 'mm_7dias_novos_obitos'},
                                       {'label': 'G - Total de casos por 100.000 habitantes', 'value': 'total_casos%'},
                                       {'label': 'H - Total de óbitos por 100.000 habitantes', 'value': 'total_obitos%'},
                                       {'label': 'I - Novos casos por 100.000 habitantes', 'value': 'novos_casos%'},
                                       {'label': 'K - Novos óbitos por 100.000 habitantes', 'value': 'novos_obitos%'},
                                       {'label': 'K - Média móvel dos novos casos - 7 dias - por 100.000 habitantes', 'value': 'mm_7dias_novos_casos%'},
                                       {'label': 'L - Média móvel dos novos óbitos - 7 dias - por 100.000 habitantes', 'value': 'mm_7dias_novos_obitos%'}], 
                               value = 'total_casos', 
                               multi = False)]), ### closing Div-Div-Dropdown
        
        
        html.Div(dcc.Graph(id = 'main_map'), #closing dcc.Graph
    #style={'width':1000, 'height':800, 'border':'2px black'}
                ), ### closing Div-Graph
    
        html.Div(dash_table.DataTable(id='table', 
                                      export_format = 'csv',
                                      style_cell={'textAlign': 'right'},
                                      style_data_conditional=[
                                              {
                                                'if': {'row_index': 'odd'},
                                                'backgroundColor': 'rgb(248, 248, 248)'
                                                }, 
                                              {
                                                    'if': {'column_id': 'Localidade'},
                                                    'textAlign': 'left'
                                                }], 
                                      style_header={
                                              'backgroundColor': 'rgb(230, 230, 230)',
                                              'fontWeight': 'bold'}
                                      )),
        html.Div(dcc.Markdown(
                            '''
                              Os dados reportados neste painel foram obtidos na plataforma Brasil.IO, repositório de dados públicos disponibilizados em formato acessível. Conheça e apoie esta iniciativa.
                              
                              https://brasil.io/home/
                              
                              
                              
                              Os mapas foram obtidos no site do IBGE em formato shapefile e simplificados usando a biblioteca Geopandas.
                              '''
                              ) #closing Markdown
        ) ### closing Div-Markdown
]) #closing main html.Div
        
        
        
        
        
        
        
# Callbacks - here is where the magic happens
@app.callback([Output('main_map', 'figure'),
               Output('table', 'data'),
               Output('table', 'columns')],
              [Input('dropdown_info', 'value'),
               Input('dropdown_geo_level', 'value')])
def update_figure(info, geo_level):
    ### according to the geo_level, we'll choose the right DataFrame
    if geo_level == 'states':
        df = df_estados_hoje
        locations = locations_states
        geojson = jdataBra_states
        featureidkey = 'properties.SIGLA_UF'
    elif geo_level == 'rgintermed':
        df = df_rgint_hoje
        locations = locations_rgintermed
        geojson = jdataBra_rgintermed
        featureidkey='properties.CD_RGINT'
    elif geo_level == 'rgi':
        df = df_rgi_hoje
        locations = locations_rgi
        geojson = jdataBra_rgimed
        featureidkey = featureidkey='properties.CD_RGI'
    elif geo_level == 'cities':
        df = df_hoje
        locations = locations_mun
        geojson = jdataBra_municipios
        featureidkey = featureidkey='properties.CD_MUN'
    else:  #else select states
        df = df_estados_hoje
        locations = locations_states
        geojson = jdataBra_states
        featureidkey = 'properties.SIGLA_UF'
        
     
    figure = {'data': [go.Choroplethmapbox(geojson = geojson,
                                           locations = locations,
                                           z = df[info],
                                           featureidkey = featureidkey,
                                           colorscale = 'RdPu',
                                           #hovertemplate = '<b>%{customdata[0]}</b><br>z2:%{customdata[1]:.3f} <br>z3: %{customdata[2]:.3f} ',
                                           customdata=df)],
                'layout': go.Layout(
                                           #title = 'Mapa de óbitos por estados brasileiro',
                                           hovermode = 'closest',
                                           width = 1000,
                                           height = 700,
                                           mapbox={'zoom': 3,
                                                   'style': 'carto-positron',
                                                   'center': {"lat": -15, "lon": -60}})
                                   } #closing figure
                
    
    
    
    data=df.sort_values(by = info, ascending = False).to_dict('records')
    
    formatlocale_ptBR_int = Format(
            scheme = Scheme.fixed,
            precision = 0,
            group = Group.yes,
            groups = 3,
            group_delimiter = '.',
            decimal_delimiter = ',',
            symbol = Symbol.no,
            symbol_prefix = u'R$')
  
    formatlocale_ptBR_float = Format(
            scheme = Scheme.fixed,
            precision = 1,
            group = Group.yes,
            groups = 3,
            group_delimiter = '.',
            decimal_delimiter = ',',
            symbol = Symbol.no,
            symbol_prefix = u'R$')
    
    
    if geo_level == 'states':
        columns=[{'id': 'estado', 'name': 'Estado', 'type': 'text'},
                 {'id': 'sigla_estado', 'name': 'Sigla', 'type': 'text'},
                 {'id': 'pop', 'name': 'População', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_casos', 'name': 'A', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_obitos', 'name': 'B', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_casos', 'name': 'C', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_obitos', 'name': 'D', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_casos', 'name': 'E', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos', 'name': 'F', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'total_casos%', 'name': 'G', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_obitos%', 'name': 'H', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_casos%', 'name': 'I', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_obitos%', 'name': 'J', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_casos%', 'name': 'K', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos%', 'name': 'L', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 
                 ]
    elif geo_level == 'rgintermed':
        columns=[{'id': 'nome_rgint', 'name': 'Região Intermediária', 'type': 'text'},
                 {'id': 'estado', 'name': 'Estado', 'type': 'text'},
                 {'id': 'pop', 'name': 'População', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_casos', 'name': 'A', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_obitos', 'name': 'B', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_casos', 'name': 'C', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_obitos', 'name': 'D', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_casos', 'name': 'E', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos', 'name': 'F', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'total_casos%', 'name': 'G', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_obitos%', 'name': 'H', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_casos%', 'name': 'I', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_obitos%', 'name': 'J', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_casos%', 'name': 'K', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos%', 'name': 'L', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 
                 ]
    elif geo_level == 'rgi':
        columns=[{'id': 'nome_rgi', 'name': 'Região Imediata', 'type': 'text'},
                 {'id': 'nome_rgint', 'name': 'Região Intermediária', 'type': 'text'},
                 {'id': 'estado', 'name': 'Estado', 'type': 'text'},
                 {'id': 'pop', 'name': 'População', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_casos', 'name': 'A', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_obitos', 'name': 'B', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_casos', 'name': 'C', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_obitos', 'name': 'D', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_casos', 'name': 'E', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos', 'name': 'F', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'total_casos%', 'name': 'G', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_obitos%', 'name': 'H', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_casos%', 'name': 'I', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_obitos%', 'name': 'J', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_casos%', 'name': 'K', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos%', 'name': 'L', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 
                 ]
    else: #municipios
        columns=[{'id': 'nome_mun', 'name': 'Município', 'type': 'text'},
                 {'id': 'nome_rgi', 'name': 'Região Imediata', 'type': 'text'},
                 {'id': 'nome_rgint', 'name': 'Região Intermediária', 'type': 'text'},
                 {'id': 'sigla_estado', 'name': 'Estado', 'type': 'text'},
                 {'id': 'pop', 'name': 'População', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_casos', 'name': 'A', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_obitos', 'name': 'B', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_casos', 'name': 'C', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_obitos', 'name': 'D', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_casos', 'name': 'E', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos', 'name': 'F', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'total_casos%', 'name': 'G', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_obitos%', 'name': 'H', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_casos%', 'name': 'I', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_obitos%', 'name': 'J', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_casos%', 'name': 'K', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos%', 'name': 'L', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 
                 ]

    
    
                                   
    return figure, data, columns
    
    
    
    
if __name__ == '__main__':
    app.run_server(debug = True)


