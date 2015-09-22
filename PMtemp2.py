# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 12:17:47 2015

@author: lucyB570
"""

import numpy, os

z= 2114 #elevation above sea level (m)
P=101.3*(((293-0.0065*z)/293)**5.26) #atmospheric pressure (kPa)
gamma=0.000665*P #psycromatic constant
latitude=43.75876
a= 0.23 #albedo for grass

filename = os.path.join('BRWtemp','BRWtemp_HrlySummary_2013.csv')

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
#daily net radiation in MJ/m2/day
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
tempeT=0.6108**((17.27+tempTmean)/(tempTmean+237.3))
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
tempOmegas=numpy.arccos(-numpy.tan(latitude)*numpy.tan(tempSdec))
 #extraterrestrial radiation
tempRa=([24*60/numpy.pi*0.0820*x for x in tempdr])* \
    ((tempOmegas*numpy.sin(latitude)*numpy.sin(tempSdec)) \
    +(numpy.cos(latitude)*numpy.cos(tempSdec)*numpy.sin(tempOmegas)))
#clear sky solar radiation
tempRso=(0.75+2*numpy.exp(-5) *z)*tempRa
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