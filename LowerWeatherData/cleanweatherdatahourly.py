# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 16:01:38 2015
this is an adaptation of the clean weather data code that should
calculate storm statistics on an hourly and seasonal basis

major flaw: this code does not deal with storms overlapping seasons
@author: lucyB570
"""

from numpy import loadtxt
import numpy

stormlength=[];stormdepth=[];interstorm=[];stormcount=0

preciptocountasastorm=0.01 #precim is in mm (0.5 was used as the daily threshold)
startyear=1999
endyear=2013

for n in range(startyear,endyear): #years 1999-2013, because exclusive
    print "Calculating %i..." % (n)
    filename = "%i.txt" % (n)
    #loads in the hourly precip data
    precipHourly = loadtxt(filename, comments="#", delimiter="    ", unpack=False) 
    
    #defines wet and dry seson
    quarteryear = precipHourly/4    

    #initialize temporary variables
    templength=0
    tempdepth=0
    tempinterstorm=0
    
    #actual counting of storm descriptors here
    for i in range(len(precipHourly)): #len = 8760, range is 0-8759

                
        #if it's not raining, add to interstorm
        if (precipHourly[i]-precipHourly[(i-1)])==0 or i==0: #preciptocountasastorm or i==0:
            tempinterstorm+=1
        
        #if it is raining, it is a storm. What kind?
        else:
            templength+=1 #add one hour to the storm length
            tempdepth+=(precipHourly[i]-precipHourly[(i-1)]) #top up rain depth/storm
            
            #if it wasn't raining last hour, a storm is begining
            if precipHourly[(i-1)] -precipHourly[(i-2)]<=0: 
                interstorm.append(tempinterstorm)
                tempinterstorm=0 #ends the interstorm duration, and clears it for next time
                stormcount+=1
            
            #at the end of a year, end storm
            if (i+1)==len(precipHourly):
                stormdepth.append(tempdepth)
                stormlength.append(templength)
                templength=0
                tempdepth=0  
                
            #if it isn't raining next hour, a storm is ending
            elif precipHourly[(i+1)] -precipHourly[(i)]==0:
                stormdepth.append(tempdepth)
                stormlength.append(templength)
                templength=0
                tempdepth=0     
                    
mustormlength = numpy.mean(stormlength)
mustormdepth = numpy.mean(stormdepth)
muinterstorm = numpy.mean(interstorm)
mustormsperyear = stormcount/(endyear-startyear) #total number of storms divided by years
        
    
        
out = "Done! mustormlength = %.2f hours, mustormdepth = %.2f mm, muinterstorm = %.2f hours, mustormsperyear = %.2f" % (mustormlength,mustormdepth,muinterstorm,mustormsperyear)

with open("Output.txt", "w") as text_file:
    text_file.write(out)
#
print out        
