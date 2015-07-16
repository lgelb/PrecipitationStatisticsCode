# This code will read in precipitation data and find storms.
#For those storms it will give these outputs:
#    mustormlength (days)
#    mustormdepth (mm)
#    muinterestorm (days)

#for HP could test this threshold by varrying it and calculating some statistics
#currenlty missing 15 (for 1999) days where rain >0 but <preciptocountasstorm
#does not take into account storms that go over the new year
#could add some bash scripting to format precip data.
#currently needs a single column tab-separated .txt of precip in mm

"""
This code doesn't work. Something is wrong with the way it counts things as a storm
"""

from numpy import loadtxt
import numpy
#import csv

#dstormlength=[];dstormdepth=[];dinterstorm=[]
w_stormlength=[];w_stormdepth=[];w_interstorm=[]

preciptocountasastorm=0.01 #precim is in mm 0.5
alltimeprecip=[] #who do I need thid?
stormcount=0 #this is to count total number of storms, to get num storms/yr

for n in range(1999,2000): #years 1999-2013, because exclusive
    print "Calculating %i..." % (n)
    filename = "%i.txt" % (n)
    precipHourly = loadtxt(filename, comments="#", delimiter="    ", unpack=False) #loads in the hourly precip data
    
    if (len(precipHourly)/24 > 365): #finds number of days/year (leap years)
        leapyear=True
    else:
        leapyear=False
    numdays= (len(precipHourly))/24#formerly index
    
    #precipDaily = [0 for x in range(days)] #declare an empty array of the correct number of days
    #precipDaily = precipHourly[0::24] #pick out daily precip  
#    raining = [0 for x in range(precipHourly)]
#    stormprecip = [0 for x in range(precipHourly)]
#    todayprecip=[]
#    for n in range(precipHourly):
#        #if the precip since last hour is greater than the storm threshold
#        #add to storm lenght
#            if (precipHourly[n]-precipHourly[(n-1)])>preciptocountasastorm:
#                templength+=1
#            else:
#                tempinterstorm+=1
    #alltimeprecip.append(dailytotprecip) #really this could be used from now on but I'm lazy and don't feel like fixing it now -Lucy, 3:26 AM 
            
    templength=0
    tempdepth=0
    tempinterstorm=0
    
    #actual counting of storm descriptors here
    for i in range(len(precipHourly)):

        #if it's not raining, add to interstorm
        if (precipHourly[i]-precipHourly[(i-1)])<0 or i==0: #preciptocountasastorm or i==0:
            tempinterstorm+=1
        #if it is raining, query storm duration
        else: #adds to storm length
            templength+=1
            tempdepth+=(precipHourly[i]-precipHourly[(i-1)])
            if precipHourly[(i-1)]<0: #if it wasn't raining last hour, a storm is begining
                w_interstorm.append(tempinterstorm)
                tempinterstorm=0 #ends the interstorm duration, and clears it for next time
                stormcount+=1
                print "new storm", i
            else:
                if i+1==len(precipHourly):
                    #ends storms that are ongoing at new years to avoid indexing problems.
                    #In future should have data run for the length of the water year.
                    w_stormdepth.append(tempdepth)
                    w_stormlength.append(templength)
                    print "end yr", i
                    #wipe temp variables for next storm                
                    templength=0
                    tempdepth=0
                    stormcount=0
                elif precipHourly[(i+1)]==0:
                    #Ends storms if it isn't raining next hour
                    w_stormdepth.append(tempdepth)
                    w_stormlength.append(templength)
                    print "fin storm", i
                    #wipe temp variables for next storm                
                    templength=0
                    tempdepth=0
                    stormcount=0


#wmustormlength = numpy.mean(wstormlength)
#wmustormdepth = numpy.mean(wstormdepth)
#wmuinterstorm = numpy.mean(winterstorm)

#dmustormlength = numpy.mean(dstormlength)
#dmustormdepth = numpy.mean(dstormdepth)
#dmuinterstorm = numpy.mean(dinterstorm)

mustormsperyear = stormcount/14.0 #total number of storms divided by years

#out = "Done! mustormlength = %f, mustormdepth = %f, muinterstorm = %f, mustormsperyear = %f (lengths in days and mm)" % (wmustormlength,wmustormdepth,wmuinterstorm,mustormsperyear)
#
#with open("Output.txt", "w") as text_file:
#    text_file.write(out)
#
#print out