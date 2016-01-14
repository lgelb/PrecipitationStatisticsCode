# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 12:48:04 2016

This script reads in the MACA CSVs for each model, strips years before 2070 and
the leap days (Feb 29th), then finds the daily average across all models.
The CSVs are labels as '.nc.' but are really .csv. Just go with it.
@author: Lucy
"""
import pandas
import glob

# creates a list of all available model csvs'
tasmin_files = glob.glob('agg_macav2metdata_tasmin_*')
tasmax_files = glob.glob('agg_macav2metdata_tasmax_*')

'''finds daily min temperature'''
tasmin = pandas.DataFrame()
for i, elem in enumerate(tasmin_files):

    # reads in one model's data for 100 years
    df = pandas.read_csv(tasmin_files[i], names=['date', 'mintemp'],
                         sep=",", skiprows=8)
    # deletes data so only use 2070-2099
    df = df[df.date > '2069-12-31']
    # deletes leap days (Feb 29th)
    df = df[~df["date"].str.contains('02-29')]
    # converts from kelvin to celcius
    df['mintemp'] = df['mintemp']-273.15
    # adds data to main dataframe
    tasmin = tasmin.append(df)

# strip out year
tasmin['monthday'] = tasmin['date'].map(lambda x: x[5:])
# group by day of year
by_date = tasmin.groupby('monthday')
# average min temp by day of year
dailymin = by_date.mean()

'''finds daily max temperature'''
tasmax = pandas.DataFrame()
for i, elem in enumerate(tasmax_files):

    # reads in one model's data for 100 years
    df = pandas.read_csv(tasmax_files[i], names=['date', 'maxtemp'],
                         sep=",", skiprows=8)
    # deletes data so only use 2070-2099
    df = df[df.date > '2069-12-31']
    # deletes leap days (Feb 29th)
    df = df[~df["date"].str.contains('02-29')]
    # converts from kelvin to celcius
    df['maxtemp'] = df['maxtemp']-273.15
    # adds data to main dataframe
    tasmax = tasmax.append(df)

# strip out year
tasmax['monthday'] = tasmax['date'].map(lambda x: x[5:])
# group by day of year
by_date = tasmax.groupby('monthday')
# average min temp by day of year
dailymax = by_date.mean()

'''finds daily mean temperature'''
dailymean = pandas.concat((dailymax, dailymin), axis=1)
dailymean = dailymean.mean(axis=1)

'''plotting just to check'''
ax = dailymin.plot()
dailymean.plot(ax=ax)
dailymax.plot(ax=ax)
ax.set_ylabel('temperature (*C)')
