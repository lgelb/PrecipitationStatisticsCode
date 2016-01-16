# -*- coding: utf-8 -*-
"""

Created on Fri Jan 15 10:56:49 2016
This codes compares MACA historical to forecasted data (by Month) and then
applies that relationship to DCEW observed data to get DCEW forecasted

@author: Lucy
"""
import pandas
import glob
import os
import numpy


def diffchecker(variable):

    '''this function finds the monthly difference between MACA historical and
    modeled data'''

    '''MACA modeled historical data'''
    # creates a list of all available model csvs'
    files = glob.glob('historical\\agg_macav2metdata_{}_*'.format(variable))

    histMOD = pandas.DataFrame()
    for i, elem in enumerate(files):
        # reads in one model's data for 100 years
        df = pandas.read_csv(files[i], names=['doy', 'historical'],
                             sep=",", skiprows=8)
        # deletes data so only use 1999-2005
        df = df[df.doy > '1998-12-31']
        # converts from kelvin to celcius
        df['historical'] = df['historical']-273.15
        # adds data to main dataframe
        histMOD = histMOD.append(df)
    # strip out year
    histMOD['month'] = histMOD['doy'].map(lambda x: x[5:7])
    # group by month
    by_doy = histMOD.groupby('month')
    # average data value by month
    histMODmonth = by_doy.mean()

    '''MACA modeled forcasting data'''
    # creates a list of all available model csvs'
    files = glob.glob('RCP45\\agg_macav2metdata_{}_*'.format(variable))
    rcp45MOD = pandas.DataFrame()
    for i, elem in enumerate(files):
        # reads in one model's data for 100 years
        df = pandas.read_csv(files[i], names=['doy', 'rcp45'],
                             sep=",", skiprows=8)
        # deletes data so only use 1999-2005
        df = df[df.doy > '1998-12-31']
        # converts from kelvin to celcius
        df['rcp45'] = df['rcp45']-273.15
        # adds data to main dataframe
        rcp45MOD = rcp45MOD.append(df)
    # strip out year
    rcp45MOD['month'] = rcp45MOD['doy'].map(lambda x: x[5:7])
    # group by month
    by_doy = rcp45MOD.groupby('month')
    # average data value by month
    rcp45MODmonth = by_doy.mean()

    '''difference between the two'''
    diff = pandas.DataFrame()
    diff['diff'] = rcp45MODmonth['rcp45'] - histMODmonth['historical']

    '''plotting just to check'''
    #ax = rcp45MODmonth.plot(title='monthly MACA ensemble averages (min temp)')
    #histMODmonth.plot(ax=ax)
    #diff.plot(ax=ax)
    #ax.set_ylabel('temperature (*C)')
    
    return diff, rcp45MOD

if __name__ == '__main__':

    MODdiffmin, rcp45MOD = diffchecker('tasmin')
    MODdiffmax, rcp45MOD = diffchecker('tasmax')

    '''load historically observed DCEW data'''
    '''DCEW historical measured data'''
    # loads in historical Treeline measured data that corrsponds with MACA
    DCEW_files = glob.glob(os.path.join(os.pardir,
                                        'Treeline\\Treeline_HrlySummary_*'))
    # arrays to hold successive years worth of data
    dcewOBSmin = []
    dcewOBSmax = []
    # loops through files 199-2005 (0-7), which have complete data
    for i in range(7):
        # reads in 1 year's hourly temp data
        a = numpy.loadtxt(DCEW_files[i], delimiter=',', skiprows=20,
                          usecols=[2])
        # converts missing data to NaNs
        a[a == -6999.0] = numpy.nan
        # find daily min, append it to main array
        dcewOBSmin = numpy.append(dcewOBSmin,
                                  numpy.nanmin(a.reshape(-1, 24), axis=1))
        # find daily max, apped it to main array
        dcewOBSmax = numpy.append(dcewOBSmax,
                                  numpy.nanmax(a.reshape(-1, 24), axis=1))
    # convert those arrays to data frames for easier manipulation
    # used the rcp45MOD array just to make date sorting easier
    data = rcp45MOD[0:2557]
    data = data.drop('rcp45', 1)
    data['dcewOBSmin']=dcewOBSmin
    data['dcewOBSmax']=dcewOBSmax
    data['dcewMODmin']=numpy.nan
    data['dcewMODmax']=numpy.nan
                            
    '''add difference between historical and forecasted MACA data to DCEW obs'''
    for i in range(len(data)):
        month = int(data.iloc[i,1]) - 1
        data.loc[i,'dcewMODmin'] = MODdiffmin.iloc[month,0] + data.loc[i,'dcewOBSmin']
        data.loc[i,'dcewMODmax'] = MODdiffmax.iloc[month,0] + data.loc[i,'dcewOBSmax']

    # find mean
    data['dcewMODmean'] = data[['dcewMODmin','dcewMODmax']].mean(axis=1)

    data.to_csv('MODTreelineDCEW.csv', float_format='%.2f')

#    '''plot, just to check'''
#    ax = data.dcewMODmin.plot(title='historical and modified DCEW data')
#    data.dcewOBSmin.plot(ax=ax)
#    ax.set_ylabel('temperature (*C)')
