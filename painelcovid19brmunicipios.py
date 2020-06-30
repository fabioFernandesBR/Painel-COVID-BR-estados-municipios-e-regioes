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
from urllib.request import Request, urlopen
import dash_daq as daq
import dash_table
from dash_table.Format import Format, Group, Scheme, Symbol


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


## Reading info about geographical locations
path_info_rg = 'Tables/regioes_geograficas_composicao_por_municipios_2017_20180911.xlsx'
info_rg = pd.read_excel(path_info_rg, dtype = 'object')

## Reading info about population in cities:
path_info_pop = 'Tables/population_estimations.xls'
info_pop = pd.read_excel(path_info_pop, dtype = 'object')
info_pop['CD_GEOCODI'] = info_pop['COD. UF'].astype(str) + info_pop['COD. MUNIC'].astype(str)


### Generating population estimations
info_rg = info_rg.merge(info_pop[['CD_GEOCODI', 'POPULAÇÃO ESTIMADA']], on = 'CD_GEOCODI') #including the population inside the dataframe
pop_rgi = info_rg.groupby('nome_rgi').sum()['POPULAÇÃO ESTIMADA']
pop_rgintermed = info_rg.groupby('nome_rgint').sum()['POPULAÇÃO ESTIMADA']
pop_uf = info_pop.groupby('UF').sum()['POPULAÇÃO ESTIMADA']



## Reading info from Brasil.IO
'''
##### https://brasil.io/dataset/covid19/caso/?format=csv
req = Request('https://brasil.io/dataset/covid19/caso/?format=csv', headers={'User-Agent': 'Mozilla/5.0'})
data_covidbr = pd.read_csv(urlopen(req), 
                      dtype = {'city_ibge_code': 'object'},
                      parse_dates = ['date'])
'''

## Alternatively reading from the hard drive previously downloaded file

data_covidbr = pd.read_csv('Tables/covid19original.csv', 
                      dtype = {'city_ibge_code': 'object'},
                      parse_dates = ['date'])



data_covidbr_city = data_covidbr[(data_covidbr['place_type'] == 'city')]

### Keeping only the updated info
current_data_covidbr_city = data_covidbr_city[data_covidbr['is_last']][:]
## is_last tells us that we are working the most up-to-date data.


#Organizing data section
current_data_covidbr_city.drop(axis = 1, labels = ['date', 
                                              'place_type', 
                                              'is_last', 
                                              'estimated_population_2019', 
                                              'confirmed_per_100k_inhabitants', 
                                              'death_rate'], inplace = True)


df_states_current = current_data_covidbr_city.groupby(by = 'state').sum()
df_mun_current = current_data_covidbr_city[:]

### Combining to get rgi and rgintermed info
data_covidbr_combo = current_data_covidbr_city.merge(info_rg, 
                                                left_on = 'city_ibge_code', 
                                                right_on = 'CD_GEOCODI', 
                                                how = 'outer')
df_rgi_current = data_covidbr_combo.groupby(by = 'nome_rgi').sum()
df_rgintermed_current = data_covidbr_combo.groupby(by = 'nome_rgint').sum()


### Summing up total numbers
total_cases = df_states_current['confirmed'].sum()
total_deaths = df_states_current['deaths'].sum()

### including population info and calculating rates
df_states_current = df_states_current.merge(pop_uf, 
                                            left_index = True, 
                                            right_on = 'UF', 
                                            how = 'inner').rename(columns = {'POPULAÇÃO ESTIMADA': 'pop'})
df_states_current['death_rate'] = 10**5 * df_states_current['deaths'] / df_states_current['pop'] ### deaths per 100.000 inhabitantes
df_states_current['case_rate'] = 10**5 * df_states_current['confirmed'] / df_states_current['pop'] ### cases per 100.000 inhabitantes


df_rgintermed_current = df_rgintermed_current.merge(pop_rgintermed, 
                                                    left_index = True, 
                                                    right_on = 'nome_rgint', 
                                                    how = 'inner').rename(columns = {'POPULAÇÃO ESTIMADA': 'pop'})
df_rgintermed_current['death_rate'] = 10**5 * df_rgintermed_current['deaths'] / df_rgintermed_current['pop'] ### deaths per 100.000 inhabitantes
df_rgintermed_current['case_rate'] = 10**5 * df_rgintermed_current['confirmed'] / df_rgintermed_current['pop'] ### cases per 100.000 inhabitantes


df_rgi_current = df_rgi_current.merge(pop_rgi,
                                      left_index = True,
                                      right_on = 'nome_rgi', 
                                      how = 'inner').rename(columns = {'POPULAÇÃO ESTIMADA': 'pop'})
df_rgi_current['death_rate'] = 10**5 * df_rgi_current['deaths'] / df_rgi_current['pop'] ### deaths per 100.000 inhabitantes
df_rgi_current['case_rate'] = 10**5 * df_rgi_current['confirmed'] / df_rgi_current['pop'] ### cases per 100.000 inhabitantes



df_mun_current = df_mun_current.merge(info_pop[['POPULAÇÃO ESTIMADA', 'CD_GEOCODI']], 
                                      left_on = 'city_ibge_code', 
                                      right_on = 'CD_GEOCODI', 
                                      how = 'inner').rename(columns = {'POPULAÇÃO ESTIMADA': 'pop'})
df_mun_current['death_rate'] = 10**5 * df_mun_current['deaths'] / df_mun_current['pop'] ### deaths per 100.000 inhabitantes
df_mun_current['case_rate'] = 10**5 * df_mun_current['confirmed'] / df_mun_current['pop'] ### cases per 100.000 inhabitantes




### Creating the locations for each level of geo organization
locations_states = df_states_current.index
locations_rgintermed = df_rgintermed_current.index
locations_rgi = df_rgi_current.index
locations_mun = df_mun_current['city']




### organizing the datasets to be shown:
df_rgi_current = df_rgi_current.reset_index()
df_rgintermed_current = df_rgintermed_current.reset_index()
df_states_current = df_states_current.reset_index()
df_mun_current['complete_address'] = df_mun_current['city'] + '/' + df_mun_current['state']

df_mun_current_2 = df_mun_current.loc[ : , ['complete_address', 'confirmed', 'deaths', 'pop', 'death_rate', 'case_rate']]


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
                                value=total_cases, color = 'black')
                    ],
                ),
            
                html.Div(
                    [
                        daq.LEDDisplay(id='deaths-LED-display',
                                label= 'Total de óbitos confirmados no Brasil',
                                value=total_deaths, color = 'black')
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
                                       {'label': 'Total de casos', 'value': 'confirmed'},
                                       {'label': 'Total de óbitos', 'value': 'deaths'}, 
                                       {'label': 'Total de casos por 100.000 habitantes', 'value': 'case_rate'}, 
                                       {'label': 'Total de óbitos por 100.000 habitantes', 'value': 'death_rate'}
                                       ], 
                               value = 'case_rate', 
                               multi = False)]), ### closing Div-Div-Dropdown
        
        
        html.Div(dcc.Graph(id = 'main_map'), #closing dcc.Graph
    #style={'width':1000, 'height':800, 'border':'2px black'}
                ), ### closing Div-Graph
    
        html.Div(dash_table.DataTable(id='table', 
                                      export_format = 'xslx',
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
        df = df_mun_current_2
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
    
    
    
    
    columns=[{'id': df.columns[0], 'name': 'Localidade', 'type': 'text'},
              {'id': 'confirmed', 'name': 'Total de casos confirmados', 'type': 'numeric', 'format': formatlocale_ptBR_int},
              {'id': 'deaths', 'name': 'Total de óbitos confirmados', 'type': 'numeric', 'format': formatlocale_ptBR_int},
              {'id': 'pop', 'name': 'População', 'type': 'numeric', 'format': formatlocale_ptBR_int},
              {'id': 'death_rate', 'name': 'Taxa de óbitos por 100.000 hab', 'type': 'numeric', 'format': formatlocale_ptBR_float},
              {'id': 'case_rate', 'name': 'Taxa de casos por 100.000 hab', 'type': 'numeric', 'format': formatlocale_ptBR_float}]
    
                                   
    return figure, data, columns
    
    
    
    
if __name__ == '__main__':
    app.run_server(debug = True)

