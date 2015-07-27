# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 12:52:15 2015
this code cleans the csv meteorlogical files from DCEW to just a column of precip for cleanweatherdata.py
@author: lucyB570
"""

import numpy,pandas


date_time = pandas.read_csv("BRW_HrlySummary_2014.csv", parse_dates=[0], \
    header=None, usecols=[0],skiprows=20)
(precipmm,tempC,solarradiation,totalradiation,relativehumidity, \
    winddirectiondegree,windspeed,snowdepthcm)= \
    numpy.loadtxt("BRW_HrlySummary_2014.csv",delimiter=",", \
    usecols=[1,2,3,4,5,6,7,8],skiprows=20,unpack=True)

#maybe write a /txt at some point?