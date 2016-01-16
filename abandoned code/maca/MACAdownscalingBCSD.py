# -*- coding: utf-8 -*-
"""

Created on Fri Jan 15 10:56:49 2016
This code reads in historical modeled and measured data for Treeline in DCEW
and finds the correction needed to bias correct the ensemble of MACA models

@author: Lucy
"""
import pandas
import glob
import os
import numpy

# creates a list of all available model csvs'
tasmin_files = glob.glob('historical\\agg_macav2metdata_tasmin_*')
tasmax_files = glob.glob('historical\\agg_macav2metdata_tasmax_*')

'''MACA daily min temperature'''
tasmin = pandas.DataFrame()
for i, elem in enumerate(tasmin_files):

    # reads in one model's data for 100 years
    df = pandas.read_csv(tasmin_files[i], names=['date', 'mintemp'],
                         sep=",", skiprows=8)
    # deletes data so only use 2070-2099
    df = df[df.date > '1998-12-31']
#    # deletes leap days (Feb 29th)
#    df = df[~df["date"].str.contains('02-29')]
    # converts from kelvin to celcius
    df['mintemp'] = df['mintemp']-273.15
    # adds data to main dataframe
    tasmin = tasmin.append(df)
# group mins by day
by_date = tasmin.groupby('date')
# average min temp by day of year
minMOD = by_date.mean()


'''MACA daily max temperture'''
tasmax = pandas.DataFrame()
for i, elem in enumerate(tasmax_files):

    # reads in one model's data for 100 years
    df = pandas.read_csv(tasmax_files[i], names=['date', 'maxtemp'],
                         sep=",", skiprows=8)
    # deletes data so only use 2070-2099
    df = df[df.date > '1998-12-31']
#    # deletes leap days (Feb 29th)
#    df = df[~df["date"].str.contains('02-29')]
    # converts from kelvin to celcius
    df['maxtemp'] = df['maxtemp']-273.15
    # adds data to main dataframe
    tasmax = tasmax.append(df)
# group maxs by day
by_date = tasmax.groupby('date')
# average min temp by day of year
maxMOD = by_date.mean()

'''DCEW historical measured data'''
# loads in historical Treeline measured data that corrsponds with MACA
DCEW_files = glob.glob(os.path.join(os.pardir,
                                    'Treeline\\Treeline_HrlySummary_*'))
# arrays to hold successive years worth of daily min/maxs
amin = []
amax = []
# loops through files 199-2005 (0-7), which have complete data
for i in range(7):

    # reads in 1 year's hourly temp data
    a = numpy.loadtxt(DCEW_files[i], delimiter=',', skiprows=20,
                      usecols=[2])
    # converts missing data to NaNs
    a[a == -6999.0] = numpy.nan
    # find daily min, append it to main array
    amin = numpy.append(amin, numpy.nanmin(a.reshape(-1, 24), axis=1))
    # find daily max, apped it to main array
    amax = numpy.append(amax, numpy.nanmax(a.reshape(-1, 24), axis=1))
# convert those arrays to data frames for easier manipulation
minOBS = pandas.DataFrame(index=minMOD.index,
                          data=amin, columns=['mintemp'])
maxOBS = pandas.DataFrame(index=maxMOD.index,
                          data=amax, columns=['maxtemp'])

'''now look at it by month, not overall date'''
# strip out year and day
minOBS['month'] = minOBS.index.map(lambda x: x[5:7])
by_monthOBS = pandas.DataFrame(index=minOBS.index)
# get 12 monthly columns of data (rest are nans)
for i in range(9):
    by_monthOBS[i] = minOBS.mintemp[minOBS['month'] == '0{}'.format(i)]
for i in range(10, 13):
    by_monthOBS[i] = minOBS.mintemp[minOBS['month'] == '{}'.format(i)]
by_monthOBS.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                       'Sep', 'Oct', 'Nov', 'Dec']
# get cdf of a month
by_monthOBS.Dec.hist(cumulative=True, histtype='step', normed=1, bins=100)

minMOD['month'] = minMOD.index.map(lambda x: x[5:7])
by_monthMOD = pandas.DataFrame(index=minMOD.index)
# get 12 monthly columns of data (rest are nans)
for i in range(9):
    by_monthMOD[i] = minMOD.mintemp[minMOD['month'] == '0{}'.format(i)]
for i in range(10, 13):
    by_monthMOD[i] = minMOD.mintemp[minMOD['month'] == '{}'.format(i)]
by_monthMOD.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                       'Sep', 'Oct', 'Nov', 'Dec']
# get cdf of a month
by_monthMOD.Dec.hist(cumulative=True, histtype='step', normed=1, bins=100)












