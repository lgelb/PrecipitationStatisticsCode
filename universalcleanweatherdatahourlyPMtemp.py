# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 15:56:35 2015

@author: lucyB570
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 16:01:38 2015
this is an adaptation of the clean weather data code that should
calculate storm statistics on an hourly and seasonal basis

to use:
    1)change weather station name to correspond with correct site
    2)run once to see the plot that shows when precip is occuring, then
    3)adjust dry/wet seasons to correspond with correct 'begSummer'
    and 'endSummer' variables. You may also have to omit a year if precip
    data is not included for the calender year (common if a datalogger
    was installed in the spring)
    4)change txtfile.write to have correct notes in the output file

flaws:
    -this code does not deal with storms overlapping seasons
    -cannot currently deal with missing data (-6999), manually ignore those years
    -some files have 24 rows of ",,,,,,,,,,,,,," at the end (1 day). Not sure why,
    but I manually deleted these rows. If you don't, you get: "ValueError: could
    not convert string to float:"

@author: lucyB570
"""

#from numpy import loadtxt
import numpy,pandas,pylab,os
from tabulate import tabulate
import matplotlib.pyplot as plt

#initialize empty arrays, w=wet season, d=dry season
#units are hours and mm
w_stormlength=[];w_stormdepth=[];w_interstorm=[];w_stormcount=0
d_stormlength=[];d_stormdepth=[];d_interstorm=[];d_stormcount=0
PMpet=[]

#these must be adjust manually
weatherstation="BRWtemp"
startyear=2013
endyear=2014
z= 2114 #elevation above sea level (m)
P=101.3*(((293-0.0065*z)/293)**5.26) #atmospheric pressure (kPa)
gamma=0.000665*P #psycromatic constant
latitude=43.75876

numyears=endyear-startyear #finds the number of years the simulation is run
begSummer=4000 #adjust these manually based on precip graph
endSummer=6500
stormthreshold=1 #precip to count as a storm: precim is in mm (0.5 was used as the daily threshold)

#initialized precip figure
cm = plt.get_cmap('winter')
plt.figure()
plt.xlabel("day in year")
plt.ylabel("precip in mm")
ax = plt.subplot(111)
ax.set_color_cycle([cm(1.*i/numyears) for i in range(numyears)]) #color of lines changes non-randomly

for n in range(startyear,(endyear+1)): #+1 exclusive
    #precipHourly=loadtxt(filename, comments="#", delimiter="    ", unpack=False) #loads in the hourly precip data
    filename = os.path.join(weatherstation,"{}_HrlySummary_{}.csv".format(weatherstation,n))
    print "Calculating {}...".format(n)
    #reads in one year's weather data, skipping 20 header rows,\
    #for this code I'm only using precip, but there are much more data
    date_time = pandas.read_csv(filename, parse_dates=[0], \
        header=None, usecols=[0],skiprows=20)
    (precipHourly,temperatureC,solarradiation,netradiation,relativehumidity, \
        winddirectiondegree,windspeed,snowdepthcm)= \
        numpy.loadtxt(filename,delimiter=",", \
        usecols=[1,2,3,4,5,6,7,8],skiprows=20,unpack=True)

    tempTinC=numpy.mean(temperatureC.reshape(-1, 24), axis=1) #average daily temp
    tempRs=(numpy.mean(netradiation.reshape(-1, 24), axis=1))*0.0864 #daily net radiation in MJ/m2/day
    tempU2=numpy.mean(windspeed.reshape(-1,24),axis=1) #average daily windspeed m/s
    tempIhat=(4098*(0.6108**((17.21*tempTinC)/(tempTinC+237.3))))/((tempTinC+237.3)**2) #slope of saturation vapor pressure curve
    tempDT=tempIhat/(tempIhat+gamma*(1+0.34*tempU2)) #delta term (aux calc for radiation term)
    tempPT=gamma/(tempIhat+gamma*(1+0.34*tempU2)) #psi term (aux calc for wind term)
    tempTT=(900/(tempTinC+273))**tempU2 #temperature term (aux calc for wind term)
    tempeT=0.6108**((17.27+tempTinC)/(tempTinC+237.3)) #mean saturation air pressure from air temp
    tempea= tempeT*(numpy.mean(relativehumidity.reshape(-1,24),axis=1)/100)#acutal vapor pressure from relative humidity
    tempdr=[1+0.033*numpy.cos((2*numpy.pi/365)*(i+1)) for i,elem in enumerate(tempea)]#inverse relative distance earth-sun
    tempSdec=[0.409*numpy.sin(((2*numpy.pi/365)*(i+1))-1.39) for i,elem in enumerate(tempea)] #solar declination
    tempOmegas=numpy.arccos(-numpy.tan(latitude)*numpy.tan(tempSdec)) #sunset hour angle
    tempRa=24*60/numpy.pi*0.0820*tempdr* \
        ((tempOmegas*numpy.sin(latitude)*numpy.sin(tempSdec)) \
        +(numpy.cos(latitude)*numpy.cos(tempSdec)*numpy.sin(tempOmegas))) #extraterrestrial radiation
    tempRso=(0.75+2*numpy.exp(-5) *z)*tempRa #clear sky solar radiation

    #initialize temporary variables
    templength=0
    tempdepth=0
    tempinterstorm=0

    #plots this year's precip
    ax.plot(precipHourly, label=n)

    #actual counting of storm descriptors here
    for i in range(len(precipHourly)): #len = 8760, range is 0-8759

        if i<begSummer or i>(endSummer): #wetseason
            #if it's not raining, add to interstorm
            if (precipHourly[i]-precipHourly[(i-1)])<stormthreshold or i==0: #preciptocountasastorm or i==0:
                tempinterstorm+=1
            #if it is raining, it is a storm. What kind?
            else:
                templength+=1 #add one hour to the storm length
                tempdepth+=(precipHourly[i]-precipHourly[(i-1)]) #top up rain depth/storm
                #if it wasn't raining last hour, a storm is begining
                if precipHourly[(i-1)] -precipHourly[(i-2)]<stormthreshold:
                    w_interstorm.append(tempinterstorm)
                    tempinterstorm=0 #ends the interstorm duration, and clears it for next time
                    w_stormcount+=1
                #at the end of a year, end storm
                if (i+1)==len(precipHourly):
                    w_stormdepth.append(tempdepth)
                    w_stormlength.append(templength)
                    templength=0
                    tempdepth=0
                #if it isn't raining next hour, a storm is ending
                elif precipHourly[(i+1)] -precipHourly[(i)]<stormthreshold:
                    w_stormdepth.append(tempdepth)
                    w_stormlength.append(templength)
                    templength=0
                    tempdepth=0

        else: #dry season
        #if it's not raining, add to interstorm
            if (precipHourly[i]-precipHourly[(i-1)])<stormthreshold or i==0: #preciptocountasastorm or i==0:
                tempinterstorm+=1
            #if it is raining, it is a storm. What kind?
            else:
                templength+=1 #add one hour to the storm length
                tempdepth+=(precipHourly[i]-precipHourly[(i-1)]) #top up rain depth/storm
                #if it wasn't raining last hour, a storm is begining
                if precipHourly[(i-1)] -precipHourly[(i-2)]<stormthreshold:
                    d_interstorm.append(tempinterstorm)
                    tempinterstorm=0 #ends the interstorm duration, and clears it for next time
                    d_stormcount+=1
                #at the end of a year, end storm
                if (i+1)==len(precipHourly):
                    d_stormdepth.append(tempdepth)
                    d_stormlength.append(templength)
                    templength=0
                    tempdepth=0
                #if it isn't raining next hour, a storm is ending
                elif precipHourly[(i+1)] -precipHourly[(i)]<stormthreshold:
                    d_stormdepth.append(tempdepth)
                    d_stormlength.append(templength)
                    templength=0
                    tempdepth=0
    #clear these arrays for use in future years
    (precipHourly,tempC,solarradiation,totalradiation,relativehumidity, \
        winddirectiondegree,windspeed,snowdepthcm)=([] for i in range(8))

# Shrink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
# Put a legend to the right of the current axis
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
pylab.title('{}'.format(weatherstation))
pylab.savefig('{}YearlyPrecip.pdf'.format(weatherstation), bbox_inches='tight')

#wetseason statistics
w_mustormlength = numpy.mean(w_stormlength)
w_mustormdepth = numpy.mean(w_stormdepth)
w_muinterstorm = numpy.mean(w_interstorm)
w_mustormcount = w_stormcount/numyears

#dry season statistics
d_mustormlength = numpy.mean(d_stormlength)
d_mustormdepth = numpy.mean(d_stormdepth)
d_muinterstorm = numpy.mean(d_interstorm)
d_mustormcount = d_stormcount/numyears

#yearly average statistics
y_mustormlength = numpy.mean(w_stormlength+d_stormlength)
y_mustormdepth = numpy.mean(w_stormdepth+d_stormdepth)
y_muinterstorm = numpy.mean(w_interstorm+d_interstorm)
y_mustormcount = (w_stormcount+d_stormcount)/numyears

#create a table for easy formatting of output
t=[["wet season","{0:.2f}".format(w_mustormlength),"{0:.2f}/{1:.2f}".format(w_muinterstorm,w_muinterstorm/24),"{0:.2f}".format(w_mustormdepth),"{0:.2f}".format(w_mustormcount)],["dry season","{0:.2f}".format(d_mustormlength),"{0:.2f}/{1:.2f}".format(d_muinterstorm,d_muinterstorm/24),"{0:.2f}".format(d_mustormdepth),"{0:.2f}".format(d_mustormcount)],["year average","{0:.2f}".format(y_mustormlength),"{0:.2f}/{1:.2f}".format(y_muinterstorm,y_muinterstorm/24),"{0:.2f}".format(y_mustormdepth),"{0:.2f}".format(y_mustormcount)]]
h=[" ","S (hrs)","IS (hrs/days)","D (mm)",'num S']
out= tabulate(t,h)

#write findings to a file
with open("{}Output.txt".format(weatherstation), "w") as text_file:
    text_file.write("Calculated {} averages using years {} to {} \n".format(weatherstation,startyear,endyear))
    text_file.write("skipped 2010, missing precip data\n \n")
    text_file.write("elevation at BRW is 2114 m")
    text_file.write(out)
print out