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

from numpy import loadtxt
import numpy
#import csv

stormlength=[]
stormdepth=[]
interstorm=[]


preciptocountasastorm=0.5 #precim is in mm
alltimeprecip=[]
stormcount=0 #this is to count total number of storms, to get num storms/yr

for n in range(1999,2013): #years 1999-2013, because exclusive
    print "Calculating %i..." % (n)
    filename = "%i.txt" % (n)
    precipHourly = loadtxt(filename, comments="#", delimiter="    ", unpack=False) #loads in the hourly precip data

    
    days=len(precipHourly)/24 #finds number of days/year (leap years)
    
    precipDaily = [0 for x in range(days)] #declare an empty array of the correct number of days
    
    precipDaily = precipHourly[0::24] #pick out daily precip
        
    raining = [0 for x in range(days)]
    stormprecip = [0 for x in range(days)]
    
    todayprecip=[]
    dailytotprecip=[]
    #this is a first pass to find all the days it rains, could probably combine it with below for loop
    for n in range(days):
        if n==0:
            pass
        else:
            todayprecip=precipDaily[n]-precipDaily[(n-1)]#vestigal lazyness
            dailytotprecip.append(todayprecip)
            if (precipDaily[n]-precipDaily[(n-1)])>preciptocountasastorm: 
                raining[n]=1
            else:
                pass
    
    alltimeprecip.append(dailytotprecip) #really this could be used from now on but I'm lazy and don't feel like fixing it now -Lucy, 3:26 AM 
            
    templength =0
    tempdepth=0
    tempinterstorm=0
    index=days-1
    
    #actual counting of storm descriptors here
    for n in range(index):
        if raining[n]==0:
            tempinterstorm+=1
        else: #adds to storm length
            templength+=1
            tempdepth+=(precipDaily[n]-precipDaily[(n-1)])
            if raining[(n-1)]==0: #if a storm is begining
                interstorm.append(tempinterstorm)
                tempinterstorm=0
            if raining[(n+1)]==0: #if a storm is ending
                stormdepth.append(tempdepth)
                stormlength.append(templength)
                templength=0
                tempdepth=0
                stormcount+=1

mustormlength = numpy.mean(stormlength)
mustormdepth = numpy.mean(stormdepth)
muinterstorm = numpy.mean(interstorm)
mustormsperyear = stormcount/14.0 #total number of storms divided by years

#have to strip the [] from the first and last value
#I'm not sure why I wrote this in here, just saves values of storms, but all 
#I want are means, so why bother saving this stuff? 
#fo = open("stormlength.csv", "wb")
#line = fo.writelines( str(stormlength) )
#fo.close()
#fo = open("stormdepth.csv", "wb")
#line = fo.writelines( str(stormdepth) )
#fo.close()
#fo = open("interstorm.csv", "wb")
#line = fo.writelines( str(interstorm) )
#fo.close()

out = "Done! mustormlength = %.2f days (%.2f hours), mustormdepth = %.2f mm, muinterstorm = %.2f days (%.2f hours), mustormsperyear = %.2f" % (mustormlength, (mustormlength*24),mustormdepth,muinterstorm, (mustormlength*24),mustormsperyear)

with open("Output.txt", "w") as text_file:
    text_file.write(out)

print out