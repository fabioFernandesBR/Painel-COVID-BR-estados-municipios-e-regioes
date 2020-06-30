# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 18:13:21 2020

@author: FFernandes
"""


# Libbraries importing section
from urllib.request import Request, urlopen
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime


sched = BlockingScheduler()

@sched.scheduled_job('interval', hours=4)
def scheduled_job():
    #Reading data section
    ## Reading info from Brasil.IO
    req = Request('https://brasil.io/dataset/covid19/caso/?format=csv', headers={'User-Agent': 'Mozilla/5.0'})
    data_covidbr = pd.read_csv(urlopen(req), 
                      dtype = {'city_ibge_code': 'object'},
                      parse_dates = ['date'])

    data_covidbr_city = data_covidbr[(data_covidbr['place_type'] == 'city')]
    
    now = datetime.now()
    now_string = now.strftime("%d/%m/%Y %H:%M:%S")
    
       
    # Saving files
    path_to_save = 'Tables/covid19original.csv'
    data_covidbr_city.to_csv(path_to_save)
    
    file = open('last_update.txt', 'w')
    file.write(now_string)
    file.close()
    
    
    
sched.start()











