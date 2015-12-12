# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 17:50:53 2015

@author: Lucy
"""

import numpy as np
import numpy
import os
import matplotlib.pyplot as plt


BRW = {'weatherstation': 'BRW', 'startyear': 2011, 'endyear': 2014,
       'z': 2114, 'latitude': 43.75876, 'longitude': -116.090404}  # z in m
# 2014 LDP is off
LDP = {'weatherstation': 'LDP', 'startyear': 2007, 'endyear': 2013,
       'z': 1850, 'latitude': 43.737078, 'longitude': -116.1221131}
Treeline = {'weatherstation': 'Treeline', 'startyear': 1999,
            'endyear': 2014, 'z': 1610, 'latitude': 43.73019,
            'longitude': -116.140143}
# 2010 of SCR is empty,
SCR = {'weatherstation': 'SCR', 'startyear': 2010, 'endyear': 2013,
           'z': 1720, 'latitude': 43.71105, 'longitude': -116.09912}
# 2013 and 2014 of Lower Weather are off
LowerWeather = {'weatherstation': 'LowerWeather', 'startyear': 1999,
                'endyear': 2012, 'z': 1120, 'latitude': 43.6892464,
                'longitude': -116.1696892}

stationstats = Treeline
numyears = stationstats['endyear']-stationstats['startyear']+1
N = 12

for n in range(1):

    filename = os.path.join(stationstats['weatherstation'],
                            "{}_HrlySummary_{}.csv".format(
                            stationstats['weatherstation'],
                            (n+stationstats['startyear'])))

    (precipHourly, temperatureC, solarradiation, netradiation,
     relativehumidity, winddirectiondegree, windspeed, snowdepthcm) = \
     numpy.loadtxt(filename, delimiter=',', usecols=[1, 2, 3, 4, 5, 6, 7, 8],
                   skiprows=20, unpack=True)

    data = windspeed


    '''this removes all missing data'''
    for i, elem in enumerate(data):
        if data[i] == -6999:
            data[i] = numpy.NAN
            
    plt.figure()
    plt.plot(data)
    plt.xlim(0,8760)

    # rolling mean
    y = np.zeros((len(data),))
    for ctr in range(len(data)):
        y[ctr] = np.sum(data[ctr:(ctr+N)])
    final = y/N

    final = numpy.nanmin(final.reshape(-1, 24), axis=1)

    plt.figure()
    plt.plot(final)
    plt.xlim(0,365)
    plt.xlabel('Julian Day')
    plt.ylabel('windspeed')
    plt.title('{} {} (window = {}) frequency in time domain'.format(
              stationstats['weatherstation'], n+stationstats['startyear'],
              N))
