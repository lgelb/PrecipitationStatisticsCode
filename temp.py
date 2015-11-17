# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 16:43:36 2015

@author: Lucy
"""
import numpy
import os


# 2010 of SCR is empty, 2013 throws an error
SCR = {'weatherstation': 'SCR', 'startyear': 2013, 'endyear': 2013,
       'z': 1720, 'latitude': 43.71105, 'longitude': -116.09912}

filename = os.path.join(SCR['weatherstation'],
                        "{}_HrlySummary_{}temp.csv".format(
                        SCR['weatherstation'],
                        (SCR['startyear'])))


(precipHourly, temperatureC, solarradiation, netradiation,
 relativehumidity, winddirectiondegree, windspeed, snowdepthcm) = \
 numpy.genfromtxt(filename, delimiter=',', usecols=[1, 2, 3, 4, 5, 6, 7, 8],
                   skiprows=20, unpack=True)
