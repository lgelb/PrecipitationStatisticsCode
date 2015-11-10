# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 12:17:47 2015
This code takes in cleaned DCEW weather data and returns the PET value in
mm/day for that area based on 4 different pfts (bare,grass,shrub,tree)
thanks to: http://edis.ifas.ufl.edu/pdffiles/ae/ae45900.pdf
and: http://www.luiw.ethz.ch/labor2/experimente/exp4/Presentation/Net_Longwave_Radiation
and: http://edis.ifas.ufl.edu/ae459
@author: lucyB570
"""

import numpy, os, warnings, pandas
from scipy import signal
import matplotlib.pyplot as plt

def pftPET_(pft,albedo):

    #gets daily PET for all years
    for n in range(numyears): # +1 exclusive
        filename = os.path.join(stationstats['weatherstation'], \
            "{}_HrlySummary_{}.csv".format(stationstats['weatherstation'], \
            (n+stationstats['startyear'])))
        PET[:,(n)]= calcPET_(filename,stationstats,n,albedo)

    if plotyearlyPET:
        plotPET_(pft,PET,stationstats)

    #finds wet and dry season PET for each year
    (PETwet,PETdry)=seasonalPET_(PET)

    output=range(stationstats['startyear'],stationstats['endyear']+1)
    output=numpy.vstack((output,PETwet,PETdry))
    output=output.transpose()
    totmeans=numpy.nanmean(output,axis=0)

    #saves calculated PET values in the weather station's folder as '<station>_PET_values.csv'
    if saveyearlyPET:
        with open(os.path.join(stationstats['weatherstation'],
                  ('PET_{}.csv'.format(stationstats['weatherstation']))),
                  'a') as text_file:
            text_file.write('\nPFT: {}\n'.format(pft))
            text_file.write('wet season average = {:.3f}, dry season average = {:.3f}\n' \
                .format(totmeans[1],totmeans[2]))

def calcPET_(filename,stationstats,n,a):

    P=101.3*(((293-0.0065*stationstats['z'])/293)**5.26) #atmospheric pressure (kPa)
    gamma=0.000665*P #psycromatic constant

    #a= 0.23 #albedo for grass

    (precipHourly,temperatureC,solarradiation,netradiation,relativehumidity, \
        winddirectiondegree,windspeed,snowdepthcm)= \
        numpy.loadtxt(filename,delimiter=",", \
        usecols=[1,2,3,4,5,6,7,8],skiprows=20,unpack=True)

    (precipHourly,temperatureC,solarradiation,netradiation,relativehumidity, \
        winddirectiondegree,windspeed,snowdepthcm)= \
        cleanData_(precipHourly,temperatureC,solarradiation,netradiation, \
        relativehumidity,winddirectiondegree,windspeed,snowdepthcm)

#    for i,elem in enumerate(netradiation): #removes negative net radiation values
#        if netradiation[i]<0:
#            netradiation[i]=numpy.nan

    missingData= checkMissingData_(precipHourly,temperatureC,solarradiation, \
        netradiation,relativehumidity, winddirectiondegree,windspeed,snowdepthcm)
    if missingData == True:
        ETo=[numpy.nan]*365
        return ETo

    #average daily temp
    tempTmean=numpy.nanmean(temperatureC.reshape(-1, 24), axis=1)
    #max daily temp
    tempTmax=numpy.nanmax(temperatureC.reshape(-1, 24), axis=1)
    #min daily temp
    tempTmin=numpy.nanmin(temperatureC.reshape(-1, 24), axis=1)
    #daily net radiation in MJ/m2/dayF
    tempRs=(numpy.nanmean(netradiation.reshape(-1, 24), axis=1))*0.0864
    #average daily windspeed m/s
#    tempU2=numpy.nanmean(windspeed.reshape(-1,24),axis=1)
#    tempU2[:]=numpy.nanmedian(tempU2)
    ''' altered this to troubleshoot'''
#    tempU2=numpy.full((365),numpy.nanmean(windspeed)) # mean hourly unstead of daily
#    tempU2[tempU2>3]=0#numpy.NaN
    tempU2 = pandas.rolling_median(windspeed,(14*24))
    tempU2 = numpy.nanmean(tempU2.reshape(-1, 24), axis=1)
#    tempU2 = scipy.signal.butter(1,(0.1,0.5),'bandpass')
#    tempU2 = smoothed


    #slope of saturation vapor pressure curve
    tempIhat=(4098*(0.6108**((17.21*tempTmean)/(tempTmean+237.3))))/((tempTmean+237.3)**2)
     #delta term (aux calc for radiation term)
    tempDT=tempIhat/(tempIhat+gamma*(1+0.34*tempU2))
    #psi term (aux calc for wind term)
    tempPT=gamma/(tempIhat+gamma*(1+0.34*tempU2))
    #temperature term (aux calc for wind term)
    tempTT=(900/(tempTmean+273))**tempU2
    #saturation air pressure from air temp
    #tempeTmean=0.6108**((17.27+tempTmean)/(tempTmean+237.3)) #unused
    tempeTmax=0.6108**(17.27*tempTmax/(tempTmax+237.3))
    tempeTmin=0.6108**(17.27*tempTmin/(tempTmin+237.3))
    #mean saturation vopor pressure
    tempes=(tempeTmax+tempeTmin)/2
    #relative humidity
    tempRHmax=numpy.nanmax(relativehumidity.reshape(-1,24),axis=1)
    tempRHmin=numpy.nanmin(relativehumidity.reshape(-1,24),axis=1)
    #acutal vapor pressure from relative humidity
    tempea= (tempeTmin*tempRHmax/100+tempeTmax*tempRHmin/100)/2
    #inverse relative distance earth-sun
    tempdr=[1+0.033*numpy.cos((2*numpy.pi/365)*(i+1)) for i,elem in enumerate(tempea)]
    #solar declination
    tempSdec=[0.409*numpy.sin(((2*numpy.pi/365)*(i+1))-1.39) for i,elem in enumerate(tempea)]
    #sunset hour angle
    tempOmegas=numpy.arccos(-numpy.tan(stationstats['latitude'])*numpy.tan(tempSdec))
     #extraterrestrial radiation
    tempRa=([24*60/numpy.pi*0.0820*x for x in tempdr])* \
        ((tempOmegas*numpy.sin(stationstats['latitude'])*numpy.sin(tempSdec)) \
        +(numpy.cos(stationstats['latitude'])*numpy.cos(tempSdec)*numpy.sin(tempOmegas)))
    #clear sky solar radiation
    tempRso=(0.75+2*numpy.exp(-5) *stationstats['z'])*tempRa
    #net soloar or net shortwave radiation
    tempRns=(1-a)* tempRs
    #net outgoinglongwave solar radiation (sigma is stefan-boltzman constant)
    tempRnl=4903.10**-9 *((tempTmax+273.16)**4+(tempTmin+273.16)**4)/2 \
        *(0.34-0.14*numpy.sqrt(tempea)) *(1.35*tempRs/tempRso-0.35)
    #net radiation in MJ m-2 day-1
    tempRn=tempRns-tempRnl
    #net radiation in mm
    tempRng=0.408*tempRn
    #radiation term
    tempETrad=tempDT*tempRng
    #wind term
    tempETwind=tempPT*tempTT*(tempes-tempea)
    #FINAL evaportranspiration value
    ETo=tempETwind+tempETrad
    ETo=ETo[0:365]
    ETo[ETo<0]=numpy.NaN

    return ETo

def cleanData_(*argv):
    for arg in argv:
        for i,elem in enumerate(arg):
            if arg[i]==-6999:
                arg[i]=numpy.NAN
    return argv
'''for some reason this bit below doesn't work'''
#        if len(arg)>8760: #remove Dec 31st on leap years so arrays are the same size
#            arg=arg[0:8760]
#    return argv #why does adding/deleting this not change anything?

def checkMissingData_(*argv):
    temp=False
    for i,arg in enumerate(argv):
        if numpy.all(numpy.isnan(arg)): #if all values of one variable are missing (NaNs)
            temp=True
    return temp

def seasonalPET_(PET):
    #this will break PET into wet and dry seasons, get averages
    begSummer=171 # initially based on stormstatsgenerator precip graph from
    endSummer=266 # DCEW stations,but adjusted slightly to start of summer&fall

    #concatonates spring and fall/winter values (why doesn't Jim use water years???)
    tempwetPET=PET[0:begSummer:1]
    tempwetPET=numpy.append(tempwetPET,PET[endSummer:365:1],axis=0)

    PETwet=numpy.nanmean(tempwetPET,axis=0)
    PETdry=numpy.nanmean(PET[begSummer:endSummer:1],axis=0)
    return PETwet,PETdry

def plotPET_(pft,dataArray,stationstats):
    # you need yearlabels so you can have a legend when you plot yearly pet
    yearlabels=range(stationstats['startyear'],stationstats['endyear']+1) # +1 exclusive

    plt.figure()
    for i in range(len(dataArray[0])):
        plt.plot(dataArray[:,i], label = yearlabels[i])
    plt.xlim(0,365)
    plt.xlabel('Julian day')
    plt.ylabel('PET (mm/day)')
    plt.legend(loc = 1)
    plt.title('daily {} PET at {}'.format(pft,stationstats['weatherstation']))
    plt.savefig(os.path.join(stationstats['weatherstation'],('PET_{}_{}.svg'.format \
        (stationstats['weatherstation'],pft))),bbox_inches="tight",format='svg')

if __name__ == '__main__':

#    warnings.simplefilter("error")

    BRW={'weatherstation':'BRWtemp','startyear':2012,'endyear':2014,'z':2114,'latitude':43.75876,'longitude':-116.090404} #z in m
    LDP={'weatherstation':'LDP','startyear':2007,'endyear':2013,'z':1850,'latitude':43.737078,'longitude':-116.1221131}
    Treeline={'weatherstation':'Treeline','startyear':2012,'endyear':2012,'z':1610,'latitude': 43.73019,'longitude':-116.140143}
    SCR={'weatherstation':'SCR','startyear':2011,'endyear':2014,'z':1720,'latitude':43.71105,'longitude':-116.09912}
    LowerWeather={'weatherstation':'LowerWeather','startyear':2007,'endyear':2012,'z':1120,'latitude':43.6892464,'longitude':-116.1696892}

    #something wrong with scr data

    stationstats=Treeline
    plotyearlyPET=True
    saveyearlyPET=False

    #albedo values are for summer, snow-off, tree=conifer, shrub=sagebrush
    pftAlbedo={'bare':0.17,'grass':0.23,'shrub':0.14,'tree':0.08}
#    pftAlbedo={'grass':0.23} #this is for troubleshooting so you don't have 4 different plots crowding things up
    numyears = stationstats['endyear']-stationstats['startyear']+1 # +1 exclusinve
    PET=numpy.empty((365,numyears,))
    PET[:]=numpy.NaN

    #finds PET for all pft albedo values (4)
    for k,v in pftAlbedo.items():
        pftPET_(k,v)

