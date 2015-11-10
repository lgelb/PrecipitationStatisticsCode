# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:11:00 2015

@author: lucyB570
"""

import numpy
import matplotlib.pyplot as plt
import pandas as pd

u2=numpy.load('tempU2.npy')

PET=numpy.load('pet.npy')

#find where PET > 10
#z=[[i,v] for i,v in enumerate(PET) if v>10]
#y=[[i,v] for i,v in enumerate(u2) if v>5]

#PET = pd.rolling_median(PET,10)
#PET[PET>10]=0
PET[PET>10]=numpy.NaN
#u2[u2<0]=numpy.NaN
#troubleshoot=[numpy.NaN]*len(z)
#troubleshoot=[x for x in PET if x>5]

def smooth(x,window_len=11,window='hanning'):
        if x.ndim != 1:
                raise ValueError, "smooth only accepts 1 dimension arrays."
        if x.size < window_len:
                raise ValueError, "Input vector needs to be bigger than window size."
        if window_len<3:
                return x
        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
                raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
        s=numpy.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
        if window == 'flat': #moving average
                w=numpy.ones(window_len,'d')
        else:
                w=eval('numpy.'+window+'(window_len)')
        y=numpy.convolve(w/w.sum(),s,mode='same')
        return y[window_len:-window_len+1]

results=[]
#if form_results['smooth']:
a = u2#[:,0]
smoothed = smooth(a,window_len=10)

#plt.plot(u2)
#plt.hold()
plt.plot(smoothed)