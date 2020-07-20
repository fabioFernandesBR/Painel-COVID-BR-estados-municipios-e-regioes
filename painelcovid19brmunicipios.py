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
import dash_table
from dash_table.Format import Format, Group, Scheme, Symbol
import datetime as dt
import numpy as np

'''
Source of Population Info: https://www.ibge.gov.br/estatisticas/sociais/populacao/9103-estimativas-de-populacao.html?edicao=25272&t=downloads
Source of Maps: https://www.ibge.gov.br/geociencias/organizacao-do-territorio/15774-malhas.html?=&t=downloads
Source of COVID data: https://brasil.io/dataset/covid19/caso?format=csv
'''


#Reading data section

## Reading last update info
readfile = open('last_update.txt', 'r')
last_update = readfile.readlines()
last_update_message = 'Dados atualizados em: ' + last_update[0]
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
    
estados = pd.read_csv('Tables/uf.csv', encoding = 'latin1', dtype = 'object')    
rgint = pd.read_csv('Tables/rgintermed.csv', encoding = 'latin1', dtype = 'object') 
rgi = pd.read_csv('Tables/rgi.csv', encoding = 'latin1', dtype = 'object') 
cidades = pd.read_csv('Tables/municipios.csv', encoding = 'latin1', dtype = 'object')
cidades['localidade'] = cidades['nome_mun'] + ' / ' + cidades['sigla']

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
                           'novos_obitos': 'int64',
                           'cod_rgi': 'object',
                           'cod_rgint': 'object',
                           'cod_uf': 'object'},
                           encoding = 'latin1', 
                           compression = 'gzip')
tdf_rgi = tdf_rgi.drop(axis = 1, labels = ['Unnamed: 0'])

tdf_rgint = pd.read_csv('Tables/tdf_rgint.csv',
                  parse_dates = ['data'], 
                  dtype = {'total_casos': 'int64',
                           'total_obitos': 'int64',
                           'novos_casos': 'int64',
                           'novos_obitos': 'int64',
                           'cod_rgint': 'object',
                           'cod_uf': 'object'},
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
df_hoje = tdf[tdf['atualizado']].copy()


df_estados_hoje = tdf_estados[tdf_estados['data'] == tdf_estados['data'].max()].copy()
df_rgint_hoje = tdf_rgint[tdf_rgint['data'] == tdf_rgint['data'].max()].copy()
df_rgi_hoje = tdf_rgi[tdf_rgi['data'] == tdf_rgi['data'].max()].copy()

'''
NOTA:
Os dados de município carregam apenas as informações mais atuais de cada município.
Os dados agrupados de regiões e estados consideram a soma dos dados mais atuais de cada município que os compõem.
Isso significa que possivelmente os dados dessas regiões estarão um pouco desatualizadas.
'''

##### including a column to make identification easier
df_hoje['name'] = df_hoje['nome_mun'] + ' / ' + df_hoje['sigla']
df_rgi_hoje['name'] = df_rgi_hoje['nome_rgi'] + ' / ' + df_rgi_hoje['sigla']
df_rgint_hoje['name'] = df_rgint_hoje['nome_rgint'] + ' / ' + df_rgint_hoje['sigla']
df_estados_hoje['name'] = df_estados_hoje['estado']

### Summing up total numbers
total_cases = df_estados_hoje['total_casos'].sum()
total_deaths = df_estados_hoje['total_obitos'].sum()




### Creating the locations for each level of geo organization
locations_states = df_estados_hoje['sigla']
locations_rgintermed = df_rgint_hoje['cod_rgint']
locations_rgi =df_rgi_hoje['cod_rgi']
locations_mun = df_hoje['codigo_ibge']


### Creating options for the filters
opcoes_estados = estados.sort_values(by = 'estado')[['estado', 'sigla']].rename(columns = {'estado': 'label', 'sigla': 'value'}).to_dict(orient = 'records')




#Creating the core of the dashboard
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 

server = app.server #Disable it when in test / development mode. Enable it to Production mode
app.layout = html.Div([
        #dcc.Store(id="store_data"), #later understand why this is useful
        
        html.Div(html.H1('Painel COVID-19 nas localidades brasileiras')),
        
        html.Div(html.Label(last_update_message)),
        
        html.Div([
                html.Div(
                    [html.Label('Total de casos confirmados no Brasil'),
                     html.H1(total_cases)
                    ]),
            
                html.Div(
                    [html.Label('Total de óbitos confirmados no Brasil'),
                     html.H1(total_deaths)
                    ]),
                    ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"}), #closing Div with overall scores
        
                
        html.Div([
            html.Div(html.H3('Configure o mapa:')),
            html.Div([html.Div('Nível de organização do território:'),
                    dcc.Dropdown(id = 'dropdown_geo_level', 
                                   options = [
                                           {'label': 'Estados', 'value': 'states'},
                                           {'label': 'Regiões Geográficas Intermediárias', 'value': 'rgintermed'}, 
                                           {'label': 'Regiões Geográficas Imediatas', 'value': 'rgi'}, 
                                           {'label': 'Municípios', 'value': 'cities'}
                                           ], 
                                   value = 'states', 
                                   multi = False)]),
            
            
            html.Div([html.Div('Variável de interesse:'),
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
                                           {'label': 'J - Novos óbitos por 100.000 habitantes', 'value': 'novos_obitos%'},
                                           {'label': 'K - Média móvel dos novos casos - 7 dias - por 100.000 habitantes', 'value': 'mm_7dias_novos_casos%'},
                                           {'label': 'L - Média móvel dos novos óbitos - 7 dias - por 100.000 habitantes', 'value': 'mm_7dias_novos_obitos%'},
                                           {'label': 'M - Variação percentual da média móvel dos novos casos - 7 dias', 'value': 'var_casos_7dias'},
                                           {'label': 'N - Variação percentual da média móvel dos novos óbitos - 7 dias', 'value': 'var_obitos_7dias'}], 
                                   value = 'total_casos', 
                                   multi = False)]), ### closing Div-Div-Dropdown
           
            html.Div(html.H3('E aplique filtros:')),
            html.Div([
                    html.Div('Estado:'),
                    dcc.Dropdown(id = 'dropdown_state', 
                                   options = opcoes_estados, 
                                   value = 'all',
                                   searchable = True,
                                   clearable = True,
                                   placeholder = 'Todos os Estados',
                                   multi = True),
                    
                    html.Div('Região Geográfica Intermediária:'),
                    dcc.Dropdown(id = 'dropdown_rgint', 
                                   value = 'all',
                                   searchable = True,
                                   clearable = True,
                                   placeholder = 'Todas as Regiões Geográficas Intermediárias',
                                   multi = True),
                                 
                    html.Div('Região Geográfica Imediata:'),
                    dcc.Dropdown(id = 'dropdown_rgi',
                                   value = 'all',
                                   searchable = True,
                                   clearable = True,
                                   placeholder = 'Todas as Regiões Geográficas Imediatas',
                                   multi = True),
                                 
                    html.Div('Município:'),
                    dcc.Dropdown(id = 'dropdown_city',
                                   value = 'all',
                                   searchable = True,
                                   clearable = True,
                                   placeholder = 'Todos os Municípios',
                                   multi = True)
                                 
                                 
                                 ]),
             
                
        ]),  ### closing configuring and filtering section.
        
        html.Div(dcc.Graph(id = 'main_map')), ### closing Div-Graph - Map
                 
        
        html.Div(dcc.Graph(id = 'main_lineplot')), ### closing Div-Graph - Line plot
                 
        html.Div([html.H6('Legenda:'),
                  html.Div('A - Total de casos'),
                  html.Div('B - Total de óbitos'),
                  html.Div('C - Novos casos'),
                  html.Div('D - Novos óbitos'),
                  html.Div('E - Média móvel dos novos casos - 7 dias'),
                  html.Div('F - Média móvel dos novos óbitos - 7 dias'),
                  html.Div('G - Total de casos por 100.000 habitantes'),
                  html.Div('H - Total de óbitos por 100.000 habitantes'),
                  html.Div('I - Novos casos por 100.000 habitantes'),
                  html.Div('J - Novos óbitos por 100.000 habitantes'),
                  html.Div('K - Média móvel dos novos casos - 7 dias - por 100.000 habitantes'),
                  html.Div('L - Média móvel dos novos óbitos - 7 dias - por 100.000 habitantes'),
                  html.Div('M - Variação percentual da média móvel dos novos casos - 7 dias'),
                  html.Div('N - Variação percentual da média móvel dos novos óbitos - 7 dias')
                                    ]),
    
        
        html.Div(dash_table.DataTable(id='table', 
                                      export_format = 'csv',
                                      style_cell={'textAlign': 'left'},
                                      style_data_conditional=[
                                                {
                                                'if': {'row_index': 'odd'},
                                                'backgroundColor': 'rgb(248, 248, 248)'
                                                }, 
                                                {
                                                    'if': {'column_id': 'pop'},
                                                    'textAlign': 'right'
                                                },
                                                {
                                                    'if': {'column_id': 'total_casos'},
                                                    'textAlign': 'right'
                                                },
                                                {
                                                    'if': {'column_id': 'total_obitos'},
                                                    'textAlign': 'right'
                                                },
                                                {
                                                    'if': {'column_id': 'novos_casos'},
                                                    'textAlign': 'right'
                                                },
                                                {
                                                    'if': {'column_id': 'novos_obitos'},
                                                    'textAlign': 'right'
                                                },
                                                {
                                                    'if': {'column_id': 'mm_7dias_novos_casos'},
                                                    'textAlign': 'right'
                                                },
                                                 {
                                                    'if': {'column_id': 'mm_7dias_novos_obitos'},
                                                    'textAlign': 'right'
                                                },
                                                {
                                                    'if': {'column_id': 'total_casos%'},
                                                    'textAlign': 'right'
                                                },
                                                {
                                                    'if': {'column_id': 'total_obitos%'},
                                                    'textAlign': 'right'
                                                },
                                                {
                                                    'if': {'column_id': 'novos_casos%'},
                                                    'textAlign': 'right'
                                                },
                                                {
                                                    'if': {'column_id': 'novos_obitos%'},
                                                    'textAlign': 'right'
                                                },
                                                {
                                                    'if': {'column_id': 'mm_7dias_novos_casos%'},
                                                    'textAlign': 'right'
                                                },
                                                {
                                                    'if': {'column_id': 'mm_7dias_novos_obitos%'},
                                                    'textAlign': 'right'
                                                }                                                                                                                                                      
                                              ], 
                                      style_header= [
                                              {
                                              'backgroundColor': 'rgb(230, 230, 230)',
                                              'fontWeight': 'bold'
                                              },
                                              {
                                               'if': {'column_id': 'pop'},
                                               'textAlign': 'right'
                                                }
                                              ]
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
               Output('dropdown_rgint', 'options'),
               Output('dropdown_rgint', 'disabled'),
               Output('dropdown_rgi', 'options'),
               Output('dropdown_rgi', 'disabled'),
               Output('dropdown_city', 'options'),
               Output('dropdown_city', 'disabled'),
               Output('table', 'data'),
               Output('table', 'columns'),
               Output('main_lineplot', 'figure')],
              [Input('dropdown_info', 'value'),
               Input('dropdown_geo_level', 'value'),
               Input('dropdown_state', 'value'),
               Input('dropdown_rgint', 'value'),
               Input('dropdown_rgi', 'value'),
               Input('dropdown_city', 'value')])
def update_figure(info, geo_level, filtro_estados, filtro_rgint, filtro_rgi, filtro_cidades):
     ## Managing filters:
    if filtro_estados == 'all':
        estados_selecionados = estados['sigla']
    elif filtro_estados == []:
        estados_selecionados = estados['sigla']
    elif filtro_estados == '':
        estados_selecionados = estados['sigla']
    else:
        estados_selecionados = filtro_estados
        
    if filtro_rgint == 'all':
        rgint_selecionadas = rgint['cod_rgint']
    elif filtro_rgint == []:
        rgint_selecionadas = rgint['cod_rgint']
    elif filtro_rgint == '':
        rgint_selecionadas = rgint['cod_rgint']
    else:
        rgint_selecionadas = filtro_rgint
        
    if filtro_rgi == 'all':
        rgi_selecionadas = rgi['cod_rgi']
    elif filtro_rgi == []:
        rgi_selecionadas = rgi['cod_rgi']
    elif filtro_rgi == '':
        rgi_selecionadas = rgi['cod_rgi']        
    else:
        rgi_selecionadas = filtro_rgi
        
    if filtro_cidades == 'all':
        cidades_selecionadas = cidades['CD_GEOCODI']
    elif filtro_cidades == []:
        cidades_selecionadas = cidades['CD_GEOCODI']
    elif filtro_cidades == '':
        cidades_selecionadas = cidades['CD_GEOCODI']
    else:
        cidades_selecionadas = filtro_cidades
 
   
    ### according to the geo_level, we'll choose the right DataFrame
    if geo_level == 'states':
        df = df_estados_hoje
        locations = locations_states
        geojson = jdataBra_states
        featureidkey = 'properties.SIGLA_UF'
        key = 'sigla'
        time_df = tdf_estados
        rgint_disabled = True
        rgi_disabled = True
        city_disabled = True
        ## Applying filters
        filtered_df = df[df['sigla'].isin(estados_selecionados)]
        
    elif geo_level == 'rgintermed':
        df = df_rgint_hoje
        locations = locations_rgintermed
        geojson = jdataBra_rgintermed
        featureidkey='properties.CD_RGINT'
        key = 'cod_rgint'
        time_df = tdf_rgint
        rgint_disabled = False
        rgi_disabled = True
        city_disabled = True
        ## Applying filters
        filtered_df = df[(df['sigla'].isin(estados_selecionados)) & (df['cod_rgint'].isin(rgint_selecionadas))]
         
    elif geo_level == 'rgi':
        df = df_rgi_hoje
        locations = locations_rgi
        geojson = jdataBra_rgimed
        featureidkey = featureidkey='properties.CD_RGI'
        key = 'cod_rgi'
        time_df = tdf_rgi
        rgint_disabled = False
        rgi_disabled = False
        city_disabled = True
        ## Applying filters
        filtered_df = df[(df['sigla'].isin(estados_selecionados)) & 
                         (df['cod_rgint'].isin(rgint_selecionadas)) & 
                         (df['cod_rgi'].isin(rgi_selecionadas))]
        
    else: #else select cities
        df = df_hoje
        locations = locations_mun
        geojson = jdataBra_municipios
        featureidkey = featureidkey='properties.CD_MUN'
        key = 'codigo_ibge'
        time_df = tdf
        rgint_disabled = False
        rgi_disabled = False
        city_disabled = False
        ## Applying filters
        filtered_df = df[(df['sigla'].isin(estados_selecionados)) & 
                         (df['cod_rgint'].isin(rgint_selecionadas)) & 
                         (df['cod_rgi'].isin(rgi_selecionadas)) &
                         (df['codigo_ibge'].isin(cidades_selecionadas))]
        
    
    
    ## arranging the dataframe to be shown
    blank_df = pd.DataFrame(index = locations)
    df_to_show = blank_df.merge(filtered_df, left_index = True, right_on = key, how = 'left').fillna(0)
    
    if info in ['var_casos_7dias', 'var_obitos_7dias']:
        color_sequence = 'Picnic'
    else:
        color_sequence = 'RdPu'
    
    
    ## Creating the map figure 
    figure_map = {'data': [go.Choroplethmapbox(geojson = geojson,
                                           locations = locations,
                                           z = df_to_show[info],
                                           featureidkey = featureidkey,
                                           text = df_to_show['name'],
                                           colorscale = color_sequence 
                                           )],
                  'layout': go.Layout(title = 'Mapa da COVID-19 no Brasil',
                                      hovermode = 'closest',
                                      width = 1500,
                                      height = 1000,
                                      mapbox={'zoom': 3,
                                              'style': 'carto-positron',
                                              'center': {"lat": -15, "lon": -60}})
                                   } #closing figure
                
     
    table_data=filtered_df.sort_values(by = info, ascending = False).to_dict('records')
    
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
    
    formatlocale_ptBR_percent = Format(
            scheme = Scheme.fixed,
            precision = 1,
            group = Group.yes,
            groups = 3,
            group_delimiter = '.',
            decimal_delimiter = ',',
            symbol = Symbol.no,
            symbol_prefix = u'R$')
    
    ### Organizing the format of the table
    if geo_level == 'states':
        columns=[{'id': 'estado', 'name': 'Estado', 'type': 'text'},
                 {'id': 'sigla', 'name': 'Sigla', 'type': 'text'},
                 {'id': 'pop', 'name': 'População', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_casos', 'name': 'A', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_obitos', 'name': 'B', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_casos', 'name': 'C', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_obitos', 'name': 'D', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'mm_7dias_novos_casos', 'name': 'E', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos', 'name': 'F', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'total_casos%', 'name': 'G', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'total_obitos%', 'name': 'H', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_casos%', 'name': 'I', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_obitos%', 'name': 'J', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_casos%', 'name': 'K', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos%', 'name': 'L', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'var_casos_7dias', 'name': 'M', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'var_obitos_7dias', 'name': 'N', 'type': 'numeric', 'format': formatlocale_ptBR_float}
                 ]
    elif geo_level == 'rgintermed':
        columns=[{'id': 'nome_rgint', 'name': 'Região Intermediária', 'type': 'text'},
                 {'id': 'estado', 'name': 'Estado', 'type': 'text'},
                 {'id': 'pop', 'name': 'População', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_casos', 'name': 'A', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_obitos', 'name': 'B', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_casos', 'name': 'C', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_obitos', 'name': 'D', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'mm_7dias_novos_casos', 'name': 'E', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos', 'name': 'F', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'total_casos%', 'name': 'G', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'total_obitos%', 'name': 'H', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_casos%', 'name': 'I', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_obitos%', 'name': 'J', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_casos%', 'name': 'K', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos%', 'name': 'L', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'var_casos_7dias', 'name': 'M', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'var_obitos_7dias', 'name': 'N', 'type': 'numeric', 'format': formatlocale_ptBR_float}
                 ]
    elif geo_level == 'rgi':
        columns=[{'id': 'nome_rgi', 'name': 'Região Imediata', 'type': 'text'},
                 {'id': 'nome_rgint', 'name': 'Região Intermediária', 'type': 'text'},
                 {'id': 'estado', 'name': 'Estado', 'type': 'text'},
                 {'id': 'pop', 'name': 'População', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_casos', 'name': 'A', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_obitos', 'name': 'B', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_casos', 'name': 'C', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_obitos', 'name': 'D', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'mm_7dias_novos_casos', 'name': 'E', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos', 'name': 'F', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'total_casos%', 'name': 'G', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'total_obitos%', 'name': 'H', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_casos%', 'name': 'I', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_obitos%', 'name': 'J', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_casos%', 'name': 'K', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos%', 'name': 'L', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'var_casos_7dias', 'name': 'M', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'var_obitos_7dias', 'name': 'N', 'type': 'numeric', 'format': formatlocale_ptBR_float}
                 ]
    else: #municipios
        columns=[{'id': 'nome_mun', 'name': 'Município', 'type': 'text'},
                 {'id': 'nome_rgi', 'name': 'Região Imediata', 'type': 'text'},
                 {'id': 'nome_rgint', 'name': 'Região Intermediária', 'type': 'text'},
                 {'id': 'sigla', 'name': 'Estado', 'type': 'text'},
                 {'id': 'pop', 'name': 'População', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_casos', 'name': 'A', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'total_obitos', 'name': 'B', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_casos', 'name': 'C', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'novos_obitos', 'name': 'D', 'type': 'numeric', 'format': formatlocale_ptBR_int},
                 {'id': 'mm_7dias_novos_casos', 'name': 'E', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos', 'name': 'F', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'total_casos%', 'name': 'G', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'total_obitos%', 'name': 'H', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_casos%', 'name': 'I', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'novos_obitos%', 'name': 'J', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_casos%', 'name': 'K', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'mm_7dias_novos_obitos%', 'name': 'L', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'var_casos_7dias', 'name': 'M', 'type': 'numeric', 'format': formatlocale_ptBR_float},
                 {'id': 'var_obitos_7dias', 'name': 'N', 'type': 'numeric', 'format': formatlocale_ptBR_float}
                 ]
      
    
    ## creating the line plot
    top_places = filtered_df.sort_values(by = info, ascending = False).head(5)
    data = []
    for i, place in top_places.iterrows():
        trace = go.Scatter(x = time_df[time_df[key] == place[key]]['data'],
                           y = time_df[time_df[key] == place[key]][info],
                           mode = 'lines+markers',
                           name = place['name'])
        data.append(trace)
    
    
    figure_line = go.Figure(data=data,
                       layout=go.Layout(title = 'Curva de evolução da COVID nas localidades selecionadas'))

    figure_line = figure_line.update_xaxes(rangeslider_visible=True, 
                                 range = ['2020-02-25', time_df['data'].max()],
                                 rangeselector=dict(buttons=list([
                                         dict(count=7, label="7d", step="day", stepmode="backward"),
                                         dict(count=14, label="14d", step="day", stepmode="backward"),
                                         dict(count=1, label="1m", step="month", stepmode="backward"),
                                         dict(count=6, label="6m", step="month", stepmode="backward"),
                                         dict(count=1, label="YTD", step="year", stepmode="todate"),
                                         dict(step="all")])))
     


    figure_line.update_layout(
            autosize=True,
            #width=1500,
            #height=1200,
            margin=dict(
                l=50,
                r=50,
                b=100,
                t=100,
                pad=4),
                    paper_bgcolor="LightSteelBlue")
    
    
    ## Managing dropdown options
    ####opcoes_estados = estados.sort_values(by = 'estado')[['estado', 'sigla']].rename(columns = {'estado': 'label', 'sigla': 'value'}).to_dict(orient = 'records')
    rgint_options = rgint[rgint['sigla'].isin(estados_selecionados)].sort_values(by = ['estado', 'nome_rgint'])[['nome_rgint', 'cod_rgint']].rename(columns = {'nome_rgint': 'label', 'cod_rgint': 'value'}).to_dict(orient = 'records')
    
    rgi_options = rgi[(rgi['sigla'].isin(estados_selecionados)) & 
                      (rgi['cod_rgint'].isin(rgint_selecionadas))].sort_values(by = ['estado', 'nome_rgi'])[['nome_rgi', 'cod_rgi']].rename(columns = {'nome_rgi': 'label', 'cod_rgi': 'value'}).to_dict(orient = 'records')
    
    city_options = cidades[(cidades['sigla'].isin(estados_selecionados)) & 
                           (cidades['cod_rgint'].isin(rgint_selecionadas)) &
                           (cidades['cod_rgi'].isin(rgi_selecionadas))].sort_values(by = ['localidade'])[['localidade', 'CD_GEOCODI']].rename(columns = {'localidade': 'label', 'CD_GEOCODI': 'value'}).to_dict(orient = 'records')
    
    
    
    
                               
    return figure_map, rgint_options, rgint_disabled, rgi_options, rgi_disabled, city_options, city_disabled, table_data, columns, figure_line

if __name__ == '__main__':
    app.run_server(debug = True)


