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

major flaw: this code does not deal with storms overlapping seasons
cannot currently deal with missing data (-6999), manually ignore those years
some files have 24 rows of ",,,,,,,,,,,,,," at the end (1 day)
not sure why, but I manually deleted these rows
if you dont you get: "ValueError: could not convert string to float:"

skip missing data 2007

@author: lucyB570
"""

#from numpy import loadtxt
import numpy, pandas,pylab
from tabulate import tabulate
import matplotlib.pyplot as plt

w_stormlength=[];w_stormdepth=[];w_interstorm=[];w_stormcount=0
d_stormlength=[];d_stormdepth=[];d_interstorm=[];d_stormcount=0
(precipHourly,tempC,solarradiation,totalradiation,relativehumidity, \
        winddirectiondegree,windspeed,snowdepthcm)=([] for i in range(8))

weatherstation='LDP'
startyear=2008
endyear=2015#exclusive

numyears=endyear-startyear
begSummer=4000
endSummer=6500
stormthreshold=1 #precim is in mm (0.5 was used as the daily threshold)

cm = plt.get_cmap('winter')
plt.figure()
plt.xlabel("day in year")
plt.ylabel("precip in mm")
ax = plt.subplot(111)
ax.set_color_cycle([cm(1.*i/numyears) for i in range(numyears)])

for n in range(startyear,endyear): #years 1999-2013, because exclusive    
    #precipHourly=loadtxt(filename, comments="#", delimiter="    ", unpack=False) #loads in the hourly precip data
    filename = "{}_HrlySummary_{}.csv".format(weatherstation,n)    
    print "Calculating {}...".format(n)
    date_time = pandas.read_csv(filename, parse_dates=[0], \
        header=None, usecols=[0],skiprows=20)
    (precipHourly,tempC,solarradiation,totalradiation,relativehumidity, \
        winddirectiondegree,windspeed,snowdepthcm)= \
        numpy.loadtxt(filename,delimiter=",", \
        usecols=[1,2,3,4,5,6,7,8],skiprows=20,unpack=True)
    
    #initialize temporary variables
    templength=0
    tempdepth=0
    tempinterstorm=0
    
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


w_mustormlength = numpy.mean(w_stormlength)
w_mustormdepth = numpy.mean(w_stormdepth)
w_muinterstorm = numpy.mean(w_interstorm)
w_mustormcount = w_stormcount/numyears

d_mustormlength = numpy.mean(d_stormlength)
d_mustormdepth = numpy.mean(d_stormdepth)
d_muinterstorm = numpy.mean(d_interstorm)
d_mustormcount = d_stormcount/numyears


y_mustormlength = numpy.mean(w_stormlength+d_stormlength)
y_mustormdepth = numpy.mean(w_stormdepth+d_stormdepth)
y_muinterstorm = numpy.mean(w_interstorm+d_interstorm)
y_mustormcount = (w_stormcount+d_stormcount)/numyears

t=[["wet season","{0:.2f}".format(w_mustormlength),"{0:.2f}/{1:.2f}".format(w_muinterstorm,w_muinterstorm/24),"{0:.2f}".format(w_mustormdepth),"{0:.2f}".format(w_mustormcount)],["dry season","{0:.2f}".format(d_mustormlength),"{0:.2f}/{1:.2f}".format(d_muinterstorm,d_muinterstorm/24),"{0:.2f}".format(d_mustormdepth),"{0:.2f}".format(d_mustormcount)],["year average","{0:.2f}".format(y_mustormlength),"{0:.2f}/{1:.2f}".format(y_muinterstorm,y_muinterstorm/24),"{0:.2f}".format(y_mustormdepth),"{0:.2f}".format(y_mustormcount)]]
h=[" ","S (hrs)","IS (hrs/days)","D (mm)",'num S']
         
out= tabulate(t,h)

with open("{}Output.txt".format(weatherstation), "w") as text_file:
    text_file.write("(Calculated {} averages using years {} to {}) \n \n".format(weatherstation,startyear,endyear))    
    text_file.write(out)

print out    
        