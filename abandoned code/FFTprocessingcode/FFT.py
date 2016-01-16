# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 16:43:36 2015

@author: Lucy
"""
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
cutoffFrequency = 5

for n in range(numyears):

    filename = os.path.join(stationstats['weatherstation'],
                            "{}_HrlySummary_{}.csv".format(
                            stationstats['weatherstation'],
                            (n+stationstats['startyear'])))

    (precipHourly, temperatureC, solarradiation, netradiation,
     relativehumidity, winddirectiondegree, windspeed, snowdepthcm) = \
     numpy.loadtxt(filename, delimiter=',', usecols=[1, 2, 3, 4, 5, 6, 7, 8],
                   skiprows=20, unpack=True)

    data = windspeed
    for i, elem in enumerate(data):
        if data[i] == -6999:
            data[i] = numpy.NAN

    tm = [i for i in range(len(data))]  # time vector
    npts = len(tm)
    dt = 0.001

    frq = numpy.zeros(npts+1)  # +1 because 0 indexing

    # this loop creates a frequency vector for plotting in the frequency domain
    for j in range(npts+1):
        frq[j] = (j-1)/(npts*dt)
    frq = frq[1:]  # gets rid of the +1 for 0 indexin`g

    hk = numpy.fft.fft(data)
    df = 1/(npts*dt)
    Jc = numpy.int((cutoffFrequency/df)+1)  # define cutoff frequency
    W = numpy.zeros(npts)  # weighting vector
    W[0] = 1

    W[2:Jc] = 1
    W[npts+1-Jc:npts+1] = 1

    # multiply weight by original signal
    windowed_signal = hk*W
    # inverse fft to go back to time domain
    wind_sig_tm = abs(numpy.fft.ifft(windowed_signal))

    if max(wind_sig_tm) < 10:
        break
    else:
        # zero out weighting factor again
        W = numpy.zeros(npts)  # weighting vector
        W[npts/2-Jc:npts/2+Jc] = 1

        # multiply weight by original signal
        windowed_signal = hk*W
        # inverse fft to go back to time domain
        wind_sig_tm = abs(numpy.fft.ifft(windowed_signal))
    # if neither top nor bottom work
    if max(wind_sig_tm) >10:
        break

    # windowed signal in the time domain
    plt.figure()
    plt.plot(frq, abs(hk))
#    plt.xlim(min(frq), max(frq))
    plt.xlabel('frequency')
    plt.ylabel('amplitude FFT')
    plt.title('{} {} (cutoff = {})'.format(stationstats['weatherstation'],
              n+stationstats['startyear'], cutoffFrequency))

    # windowed signal in the time domain
    plt.figure()
    plt.plot(tm, wind_sig_tm)
    plt.xlim(min(tm), max(tm))
    plt.xlabel('Julian Hour')
    plt.ylabel('windspeed')
    plt.title('{} {} (cutoff = {}) frequency in time domain'.format(
              stationstats['weatherstation'], n+stationstats['startyear'],
              cutoffFrequency))
