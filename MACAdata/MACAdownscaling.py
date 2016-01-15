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
minmodeled = by_date.mean()


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
maxmodeled = by_date.mean()

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
minmeasured = pandas.DataFrame(index=minmodeled.index,
                               data=amin, columns=['mintemp'])
maxmeasured = pandas.DataFrame(index=maxmodeled.index,
                               data=amax, columns=['maxtemp'])

'''find the difference between measured and modelled'''
mindifference = minmeasured.subtract(minmodeled, axis = 'mintemp')
maxdifference = maxmeasured.subtract(maxmodeled, axis = 'maxtemp')

ax = maxdifference.plot(kind='hist', alpha=0.5, title='difference between modeled and measured')
mindifference.plot(ax=ax, kind='hist', alpha=0.5)

'''now look at it by day of year, not overall date'''
# strip out year
mindifference['monthday'] = mindifference.index.map(lambda x: x[5:])
# groups by day of year
by_date = mindifference.groupby('monthday')
# average difference between measured and modeled by day of year
minbydate = by_date.mean()

# strip out year
maxdifference['monthday'] = maxdifference.index.map(lambda x: x[5:])
# groups by day of year
by_date = maxdifference.groupby('monthday')
# average difference between measured and modeled by day of year
maxbydate = by_date.mean()

ax = maxbydate.plot(title='difference between modeled and measured')
minbydate.plot(ax=ax)
ax.set_ylabel('temp *C')
ax.set_xlabel('day of year')
