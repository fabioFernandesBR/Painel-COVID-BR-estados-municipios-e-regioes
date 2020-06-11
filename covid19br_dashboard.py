# -*- coding: utf-8 -*-
"""
Created on Tue May  5 22:35:41 2020

@author: FFernandes
"""

import pandas as pd
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import datetime as dt

## opening dashboard
app = dash.Dash()

'''
## reading and treating dataset
covidbr = pd.read_csv("https://brasil.io/dataset/covid19/caso?format=csv", 
                      dtype = {'city_ibge_code': 'object'},
                      parse_dates = ['date'] )

covidbr['address'] = covidbr['city'] + ' / ' + covidbr['state']
covidbr['deaths_100k'] = 100000 * covidbr['deaths'] / covidbr['estimated_population_2019']

### creating the list of options
states_options =  []
for state in covidbr['state'].unique().tolist():
    states_options.append({'label':state,'value':state})
'''

## creating the html
app.layout = html.Div([
        html.H1(id='dashboard_header', children = 'Dashboard COVID-19 Brasil - Experimental'),
        dcc.Markdown('Esta página usa dados disponibilizados pelo projeto Brasil.IO'),
        html.Pre(
                id='update_text',
                children='Atualizado em:'),
        dcc.Interval(
                id='interval-component',
                n_intervals = 0,
                interval=1000 * 60 * 5), # 1000 milliseconds = 1 second / refresh every 4 hours
        dcc.Dropdown(id='chosen_state',
                     options = states_options,
                     value = 'RJ'),
        dcc.Graph(id='bar-chart'), 
        dcc.Graph(id='timeline-chart')    
])



## managing the callbacks
### bar chart top 10 cities
@app.callback(Output('bar-chart', 'figure'),
              [Input('chosen_state', 'value')])
def update_bar_chart(selected_state):
    selected_cities = covidbr[(covidbr['is_last']) & 
                              (covidbr['place_type'] == 'city') & 
                              (covidbr['state'] == selected_state)].sort_values(by = ['confirmed_per_100k_inhabitants'], ascending = False)[['address', 'confirmed_per_100k_inhabitants']].head(10)
    data_bar = [go.Bar(orientation='h', 
                      x = selected_cities['confirmed_per_100k_inhabitants'], 
                      y = selected_cities['address'])]
    
    layout_bar = go.Layout(title = '10 cidades com maior número de casos por 100.000 habitantes')


    return {
        'data': data_bar,
        'layout': layout_bar
    }


### line chart plotting evolution
@app.callback(Output('timeline-chart', 'figure'),
              [Input('chosen_state', 'value')])
def update_timeline_chart(selected_state):
    selected_cities = covidbr[(covidbr['is_last']) & 
                              (covidbr['place_type'] == 'city') & 
                              (covidbr['state'] == selected_state)].sort_values(by = ['confirmed_per_100k_inhabitants'], 
                              ascending = False)[['address', 'confirmed_per_100k_inhabitants']].head(10)
    top10_cities = selected_cities['address']
    
    time_df = pd.DataFrame()
    for city in top10_cities:
        timeline = covidbr[covidbr['address'] == city][['date', 'confirmed_per_100k_inhabitants']].rename(columns = {'confirmed_per_100k_inhabitants': city}).set_index('date')
        time_df = time_df.join(other = timeline, how = 'outer')
    
    data_time = []
    for city in top10_cities:
        trace = go.Scatter(x = time_df.index, 
                           y = time_df.loc[ : ,city], 
                           mode = 'lines', 
                           name = city)
        data_time.append(trace)
        layout_time = go.Layout(title = 'evolução do surto nas 10 cidades com maior número de casos por 100.000 habitantes', 
                                xaxis={'title': 'Tempo'},
                                yaxis={'type': 'linear', 'title': 'Casos por 100.000 habitantes - escala logarítmica'},
                                hovermode='closest')
    
    return {
        'data': data_time,
        'layout': layout_time
    }

### updating the dataset
@app.callback(Output('update_text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_inform(n):
    covidbr = pd.read_csv("https://brasil.io/dataset/covid19/caso?format=csv", 
                      dtype = {'city_ibge_code': 'object'},
                      parse_dates = ['date'] )

    covidbr['address'] = covidbr['city'] + ' / ' + covidbr['state']
    covidbr['deaths_100k'] = 100000 * covidbr['deaths'] / covidbr['estimated_population_2019']
   
    states_options =  []
    for state in covidbr['state'].unique().tolist():
        states_options.append({'label':state,'value':state})
    
    
    timenow = dt.datetime.strftime(dt.datetime.now(), format = '%a %d-%B-%Y %H:%M')
    return 'Atualizado em: {}'.format(timenow)



## running
if __name__ == '__main__':
    app.run_server()




