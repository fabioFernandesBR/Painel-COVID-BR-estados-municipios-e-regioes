# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 18:13:21 2020

@author: FFernandes
"""


# Libbraries importing section
import pandas as pd
from urllib.request import Request, urlopen
from datetime import datetime

#Reading data section 

## Reading info from Brasil.IO
url = 'https://data.brasil.io/dataset/covid19/caso.csv.gz'
    
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data_covidbr = pd.read_csv(urlopen(req), 
                           dtype = {'city_ibge_code': 'object'},
                           parse_dates = ['date'],
                           compression = 'gzip')

data_covidbr = data_covidbr[(data_covidbr['place_type'] == 'city')]
data_covidbr.dropna(inplace = True)
data_covidbr.drop(labels = ['order_for_place', 'estimated_population_2019', 'confirmed_per_100k_inhabitants', 'death_rate', 'place_type', 'state', 'city', 'is_last'], axis = 1, inplace = True)

### Registering the updating time
now_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")



## Reading info about geographical locations
dicionario_municipios = pd.read_csv('Tables/municipios.csv', encoding = 'latin1', dtype = 'object')
dicionario_uf = pd.read_csv('Tables/uf.csv', encoding = 'latin1', dtype = 'object')
dicionario_rgi = pd.read_csv('Tables/rgi.csv', encoding = 'latin1', dtype = 'object')
dicionario_rgint = pd.read_csv('Tables/rgintermed.csv', encoding = 'latin1', dtype = 'object')



## Reading info about population in cities:
info_pop = pd.read_csv('Tables/pop.csv', dtype = {'COD. UF': 'object', 'COD. MUNIC': 'object', 'pop': 'int64'}, encoding = 'latin1')
info_pop['CD_GEOCODI'] = info_pop['COD. UF'].astype(str) + info_pop['COD. MUNIC'].astype(str)
info_pop.drop(axis = 1, labels = ['COD. UF', 'COD. MUNIC'], inplace = True)

### Generating population estimations
info_rg = dicionario_municipios.merge(info_pop, on = 'CD_GEOCODI') #including the population inside the dataframe
pop_rgi = info_rg.groupby('cod_rgi').sum()['pop']
pop_rgintermed = info_rg.groupby('cod_rgint').sum()['pop']
pop_uf = info_rg.groupby('sigla_estado').sum()['pop']


# Complete info for all dates
#### whenever a date is missing, fill it with previous date info.
initial_date = data_covidbr['date'].min()
last_date = data_covidbr['date'].max()

time_index = pd.date_range(initial_date, last_date)

tdf = pd.DataFrame()


for city in data_covidbr['city_ibge_code'].unique():
    print(city)
    provisory_df_city = data_covidbr[data_covidbr['city_ibge_code'] == city].copy()
    provisory_df_filled = pd.DataFrame(index = time_index).merge(right = provisory_df_city,
                                      left_index= True,
                                      right_on= 'date',
                                      how = 'left').set_index('date')
    provisory_df_filled.ffill(inplace = True)
    provisory_df_filled.dropna(inplace = True)
    
    provisory_df_filled['novos_casos'] = 0
    provisory_df_filled.iloc[0, 3] = provisory_df_filled.iloc[0, 0]
    provisory_df_filled.iloc[1: , 3] = provisory_df_filled['confirmed'].diff().dropna()
    
    provisory_df_filled['novos_obitos'] = 0
    provisory_df_filled.iloc[0, 4] = provisory_df_filled.iloc[0, 1]
    provisory_df_filled.iloc[1: , 4] = provisory_df_filled['deaths'].diff().dropna()
    
    provisory_df_filled['mm_7dias_novos_casos'] = provisory_df_filled['novos_casos'].rolling(window = 7).mean()
    provisory_df_filled['mm_7dias_novos_obitos'] = provisory_df_filled['novos_obitos'].rolling(window = 7).mean()
    
    
    tdf = pd.concat([tdf, provisory_df_filled.reset_index()])
    
tdf = tdf.merge(info_rg, left_on= 'city_ibge_code', right_on = 'CD_GEOCODI', how = 'left')
tdf['rgi'] = tdf['nome_rgi'] + ' / ' + tdf['sigla_estado']
tdf['rgintermed'] = tdf['nome_rgint'] + ' / ' + tdf['sigla_estado']

tdf.rename(inplace = True, columns = {'date': 'data', 
                                      'confirmed': 'total_casos',
                                      'deaths': 'total_obitos',
                                      'city_ibge_code': 'codigo_ibge'
                                      })
tdf.drop(labels = ['CD_GEOCODI'], axis = 1, inplace = True)

### Creating the dataframe related to states
tdf_estados = tdf.groupby(by = ['data', 'sigla_estado'], as_index=False).sum()
tdf_estados.drop(labels = ['pop'], axis = 1, inplace = True)
tdf_estados = tdf_estados.merge(pop_uf, left_on = 'sigla_estado', right_index = True, how = 'left')
tdf_estados = tdf_estados.merge(dicionario_uf, left_on = 'sigla_estado', right_on = 'sigla_estado', how = 'left')


### Creating the dataframe related to rgintermed
tdf_rgint = tdf.groupby(by = ['data', 'cod_rgint'], as_index=False).sum()
tdf_rgint.drop(labels = ['pop'], axis = 1, inplace = True)
tdf_rgint = tdf_rgint.merge(pop_rgintermed, left_on = 'cod_rgint', right_index = True, how = 'left')
tdf_rgint = tdf_rgint.merge(dicionario_rgint, on = 'cod_rgint', how = 'left')

### Creating the dataframe related to rg imediate
tdf_rgi = tdf.groupby(by = ['data', 'cod_rgi'], as_index=False).sum()
tdf_rgi.drop(labels = ['pop'], axis = 1, inplace = True)
tdf_rgi = tdf_rgi.merge(pop_rgi, left_on = 'cod_rgi', right_index = True, how = 'left')
tdf_rgi = tdf_rgi.merge(dicionario_rgi, on = 'cod_rgi', how = 'left')

## calculating rates
tdf['total_casos%'] = 10**5 * tdf['total_casos'] / tdf['pop']
tdf['total_obitos%'] = 10**5 * tdf['total_obitos'] / tdf['pop']
tdf['novos_casos%'] = 10**5 * tdf['novos_casos'] / tdf['pop']
tdf['novos_obitos%'] = 10**5 * tdf['novos_obitos'] / tdf['pop']
tdf['mm_7dias_novos_casos%'] = 10**5 * tdf['mm_7dias_novos_casos'] / tdf['pop']
tdf['mm_7dias_novos_obitos%'] = 10**5 * tdf['mm_7dias_novos_obitos'] / tdf['pop']

tdf_rgi['total_casos%'] = 10**5 * tdf_rgi['total_casos'] / tdf_rgi['pop']
tdf_rgi['total_obitos%'] = 10**5 * tdf_rgi['total_obitos'] / tdf_rgi['pop']
tdf_rgi['novos_casos%'] = 10**5 * tdf_rgi['novos_casos'] / tdf_rgi['pop']
tdf_rgi['novos_obitos%'] = 10**5 * tdf_rgi['novos_obitos'] / tdf_rgi['pop']
tdf_rgi['mm_7dias_novos_casos%'] = 10**5 * tdf_rgi['mm_7dias_novos_casos'] / tdf_rgi['pop']
tdf_rgi['mm_7dias_novos_obitos%'] = 10**5 * tdf_rgi['mm_7dias_novos_obitos'] / tdf_rgi['pop']

tdf_rgint['total_casos%'] = 10**5 * tdf_rgint['total_casos'] / tdf_rgint['pop']
tdf_rgint['total_obitos%'] = 10**5 * tdf_rgint['total_obitos'] / tdf_rgint['pop']
tdf_rgint['novos_casos%'] = 10**5 * tdf_rgint['novos_casos'] / tdf_rgint['pop']
tdf_rgint['novos_obitos%'] = 10**5 * tdf_rgint['novos_obitos'] / tdf_rgint['pop']
tdf_rgint['mm_7dias_novos_casos%'] = 10**5 * tdf_rgint['mm_7dias_novos_casos'] / tdf_rgint['pop']
tdf_rgint['mm_7dias_novos_obitos%'] = 10**5 * tdf_rgint['mm_7dias_novos_obitos'] / tdf_rgint['pop']

tdf_estados['total_casos%'] = 10**5 * tdf_estados['total_casos'] / tdf_estados['pop']
tdf_estados['total_obitos%'] = 10**5 * tdf_estados['total_obitos'] / tdf_estados['pop']
tdf_estados['novos_casos%'] = 10**5 * tdf_estados['novos_casos'] / tdf_estados['pop']
tdf_estados['novos_obitos%'] = 10**5 * tdf_estados['novos_obitos'] / tdf_estados['pop']
tdf_estados['mm_7dias_novos_casos%'] = 10**5 * tdf_estados['mm_7dias_novos_casos'] / tdf_estados['pop']
tdf_estados['mm_7dias_novos_obitos%'] = 10**5 * tdf_estados['mm_7dias_novos_obitos'] / tdf_estados['pop']


## Saving files
tdf.to_csv('Tables/tdf.csv', encoding = 'latin1')
tdf_rgi.to_csv('Tables/tdf_rgi.csv', encoding = 'latin1')
tdf_rgint.to_csv('Tables/tdf_rgint.csv', encoding = 'latin1')
tdf_estados.to_csv('Tables/tdf_estados.csv', encoding = 'latin1')
with open('last_update.txt', 'w') as f:
        f.write(now_string)