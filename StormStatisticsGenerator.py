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
    and 'endSummer' variables. I've used 171 (4104) and 270 (6480) below
    as they are very close to observed and are the official JD end of
    spring`and beginng of fall. You may also have to omit a year if precip
    data is not included for the calender year (common if a datalogger
    was installed in the spring)
    4)change txtfile.write to have correct notes in the output file

flaws:
    -this code does not deal with storms overlapping seasons
    -some files have 24 rows of ",,,,,,,,,,,,,," at the end (1 day). Not sure why,
    but I manually deleted these rows. If you don't, you get: "ValueError: could
    not convert string to float:"

@author: lucyB570
"""

#from numpy import loadtxt
import numpy,pylab,os
from tabulate import tabulate
import matplotlib.pyplot as plt

LowerWeather={'weatherstation':'LowerWeather','startyear':1999,'endyear':2014,'z':1120,'latitude':43.6892464,'longitude':-116.1696892}
Treeline={'weatherstation':'Treeline','startyear':1999,'endyear':2014,'z':1610,'latitude': 43.73019,'longitude':-116.140143}
SCR={'weatherstation':'SCR','startyear':2010,'endyear':2013,'z':1720,'latitude':43.71105,'longitude':-116.09912}
LDP={'weatherstation':'LDP','startyear':2007,'endyear':2014,'z':1850,'latitude':43.737078,'longitude':-116.1221131}
BRW={'weatherstation':'BRW','startyear':2012,'endyear':2014,'z':2114,'latitude':43.75876,'longitude':-116.090404} #z in m

'''-----------------------------'''
'''---adjust these as needed----'''
weatherstation=Treeline
# adjust these manually based your needs
begSummer=4104
endSummer=6480
# precip to count as a storm: precim is in mm
stormthreshold=1 # (0.5 was used as the daily threshold)
'''-----------------------------'''

startyear=weatherstation['startyear']
endyear=weatherstation['endyear']
#initialize empty arrays, w=wet season, d=dry season
#units are hours and mm
w_stormlength=[];w_stormdepth=[];w_interstorm=[];w_stormcount=0
d_stormlength=[];d_stormdepth=[];d_interstorm=[];d_stormcount=0
numyears=endyear-startyear #finds the number of years the simulation is run

#initialized precip figure
cm = plt.get_cmap('winter')
plt.figure()
plt.xlabel("hour in year")
plt.ylabel("precip in mm")
ax = plt.subplot(111)
ax.set_color_cycle([cm(1.*i/numyears) for i in range(numyears)]) #color of lines changes non-randomly

for n in range(startyear,(endyear+1)): #+1 exclusive
    #precipHourly=loadtxt(filename, comments="#", delimiter="    ", unpack=False) #loads in the hourly precip data
    filename = os.path.join(weatherstation['weatherstation'], \
                        "{}_HrlySummary_{}.csv".format(weatherstation['weatherstation'],n))
    print "Calculating {}...".format(n)
    #reads in one year's precip data, skipping 20 header rows,\
    precipHourly= numpy.loadtxt(filename,delimiter=",", \
        usecols=[1],skiprows=20,unpack=True)

    for i,elem in enumerate(precipHourly):
        if precipHourly[i]==-6999:
            precipHourly[i]=numpy.NAN

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
pylab.title('hourly {} precipitation'.format(weatherstation['weatherstation']))
pylab.savefig(os.path.join(weatherstation['weatherstation'],'Precip_{}.svg'.format(\
                    weatherstation['weatherstation'])), bbox_inches="tight",format='svg')

#wetseason statistics
w_mustormlength = numpy.nanmean(w_stormlength)
w_mustormdepth = numpy.nanmean(w_stormdepth)
w_muinterstorm = numpy.nanmean(w_interstorm)
w_mustormcount = w_stormcount/numyears

#dry season statistics
d_mustormlength = numpy.nanmean(d_stormlength)
d_mustormdepth = numpy.nanmean(d_stormdepth)
d_muinterstorm = numpy.nanmean(d_interstorm)
d_mustormcount = d_stormcount/numyears

#yearly average statistics
y_mustormlength = numpy.nanmean(w_stormlength+d_stormlength)
y_mustormdepth = numpy.nanmean(w_stormdepth+d_stormdepth)
y_muinterstorm = numpy.nanmean(w_interstorm+d_interstorm)
y_mustormcount = (w_stormcount+d_stormcount)/numyears

#create a table for easy formatting of output
t=[["wet season","{0:.2f}".format(w_mustormlength),"{0:.2f}/{1:.2f}".format( \
                    w_muinterstorm,w_muinterstorm/24),"{0:.2f}".format( \
                    w_mustormdepth),"{0:.2f}".format(w_mustormcount)], \
                    ["dry season","{0:.2f}".format(d_mustormlength), \
                    "{0:.2f}/{1:.2f}".format(d_muinterstorm,d_muinterstorm/24),\
                    "{0:.2f}".format(d_mustormdepth),"{0:.2f}".format( \
                    d_mustormcount)],["year average","{0:.2f}".format( \
                    y_mustormlength),"{0:.2f}/{1:.2f}".format(y_muinterstorm, \
                    y_muinterstorm/24),"{0:.2f}".format(y_mustormdepth), \
                    "{0:.2f}".format(y_mustormcount)]]
h=[" ","S (hrs)","IS (hrs/days)","D (mm)",'num S']
out= tabulate(t,h)

#write findings to a file
with open(os.path.join(weatherstation['weatherstation'],"Precip_{}.txt".format( \
                    weatherstation['weatherstation'])), "w") as text_file:
    text_file.write("Calculated {} averages using years {} to {} \n".format( \
                    weatherstation['weatherstation'],startyear,endyear))
    text_file.write(out)
print out