# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 12:17:47 2015
This code takes in cleaned DCEW weather data and returns the PET value for that
area based on 4 different pfts (bare,grass,shrub,tree)
thanks to: http://edis.ifas.ufl.edu/pdffiles/ae/ae45900.pdf
and: http://www.luiw.ethz.ch/labor2/experimente/exp4/Presentation/Net_Longwave_Radiation
and: http://edis.ifas.ufl.edu/ae459
@author: lucyB570
"""

import numpy, os
import matplotlib.pyplot as plt

def calcPET_(filename,stationstats):

    P=101.3*(((293-0.0065*stationstats['z'])/293)**5.26) #atmospheric pressure (kPa)
    gamma=0.000665*P #psycromatic constant

    a= 0.23 #albedo for grass

    (precipHourly,temperatureC,solarradiation,netradiation,relativehumidity, \
        winddirectiondegree,windspeed,snowdepthcm)= \
        numpy.loadtxt(filename,delimiter=",", \
        usecols=[1,2,3,4,5,6,7,8],skiprows=20,unpack=True)

    #average daily temp
    tempTmean=numpy.mean(temperatureC.reshape(-1, 24), axis=1)
    #max daily temp
    tempTmax=numpy.max(temperatureC.reshape(-1, 24), axis=1)
    #min daily temp
    tempTmin=numpy.min(temperatureC.reshape(-1, 24), axis=1)
    #daily net radiation in MJ/m2/dayF
    tempRs=(numpy.mean(netradiation.reshape(-1, 24), axis=1))*0.0864
     #average daily windspeed m/s
    tempU2=numpy.mean(windspeed.reshape(-1,24),axis=1)
    #slope of saturation vapor pressure curve
    tempIhat=(4098*(0.6108**((17.21*tempTmean)/(tempTmean+237.3))))/((tempTmean+237.3)**2)
     #delta term (aux calc for radiation term)
    tempDT=tempIhat/(tempIhat+gamma*(1+0.34*tempU2))
    #psi term (aux calc for wind term)
    tempPT=gamma/(tempIhat+gamma*(1+0.34*tempU2))
    #temperature term (aux calc for wind term)
    tempTT=(900/(tempTmean+273))**tempU2
    #saturation air pressure from air temp
    tempeTmean=0.6108**((17.27+tempTmean)/(tempTmean+237.3))
    tempeTmax=0.6108**(17.27*tempTmax/(tempTmax+237.3))
    tempeTmin= 0.6108**(17.27*tempTmin/(tempTmin+237.3))
    #mean saturation vopor pressure
    tempes=(tempTmax+tempeTmin)/2
    #relative humidity
    tempRHmax=numpy.max(relativehumidity.reshape(-1,24),axis=1)
    tempRHmin=numpy.min(relativehumidity.reshape(-1,24),axis=1)
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
    return ETo

def plotMinMeanMax_(dataArray,yearlabels):
    plt.figure()
    for i in range(len(dataArray[0])):
        plt.plot(dataArray[:,i], label = yearlabels[i])
    plt.xlabel('Julian day')
    plt.ylabel('PET (mm/day)')
    plt.legend(loc = 1)

def seasonalPET_(PET):
    #this will break PET into wet and dry seasons, get averages
    begSummer=171 # initially based on stormstatsgenerator precip graph from
    endSummer=266 # DCEW stations,but adjusted slightly to start of summer&fall

    #concatonates spring and fall/winter values (why doesn't Jim use water years???)
    tempwetPET=PET[0:begSummer:1]
    tempwetPET=numpy.append(tempwetPET,PET[endSummer:365:1],axis=0)

    PETwet=numpy.mean(tempwetPET,axis=0)
    PETdry=numpy.mean(PET[begSummer:endSummer:1],axis=0)
    return PETwet,PETdry

def saveData_():
    x=5

def plotData_(PET):
    #plots that PET data for each year, saves that fig
    yearlabels=range(stationstats['startyear'],stationstats['endyear']+1) # +1 exclusive
    plotMinMeanMax_(PET,yearlabels)

if __name__ == '__main__':

    weatherstation='BRWtemp'
    stationstats={'startyear':2013,'endyear':2014,'z':2114,'latitude':43.75876} #z in m
    #albedo values are for summer, snow-off, tree=conifer, shrub=sagebrush
    albedo={'bare':0.17,'grass':0.23,'shrub':0.14,'tree':0.08}
    numyears = stationstats['endyear']-stationstats['startyear']+1 # +1 exclusinve
    PET=numpy.empty((365,numyears,))
    PET[:]=numpy.NaN

    #gets daily PET for all years
    for n in range(numyears): # +1 exclusive
        filename = os.path.join(weatherstation, \
            "{}_HrlySummary_{}.csv".format(weatherstation, \
            (n+stationstats['startyear'])))
        PET[:,(n)]= calcPET_(filename,stationstats)

    plotData_(PET)

    #finds wet and dry season PET for each year
    (PETwet,PETdry)=seasonalPET_(PET)






