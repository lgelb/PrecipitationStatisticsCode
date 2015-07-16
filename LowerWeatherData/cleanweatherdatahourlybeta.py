# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 16:01:38 2015
this is an adaptation of the clean weather data code that should
calculate storm statistics on an hourly and seasonal basis
@author: lucyB570
"""

from numpy import loadtxt

w_stormlength=[];w_stormdepth=[];w_interstorm=[]

preciptocountasastorm=0.01 #precim is in mm (0.5 was used as the daily threshold)

for n in range(1999,2000): #years 1999-2013, because exclusive
    print "Calculating %i..." % (n)
    filename = "%i.txt" % (n)
    #loads in the hourly precip data
    precipHourly = loadtxt(filename, comments="#", delimiter="    ", unpack=False) 
    
    numdays= (len(precipHourly))/24 #finds number of days/year
    if numdays > 365: #(leap years)
        leapyear=True
    else:
        leapyear=False
    numdays= (len(precipHourly))/24
    
    #initialize temporary variables
    templength=0
    tempdepth=0
    tempinterstorm=0