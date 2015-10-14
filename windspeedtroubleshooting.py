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
z=[[i,v] for i,v in enumerate(PET) if v>10]
y=[[i,v] for i,v in enumerate(u2) if v>5]

PET = pd.rolling_median(PET,3)

#PET[PET>10]=0

#PET[PET>10]=numpy.NaN
#u2[u2<0]=numpy.NaN

plt.plot(u2)
plt.hold()
#plt.plot(PET)

#troubleshoot=[numpy.NaN]*len(z)
#troubleshoot=[x for x in PET if x>5]