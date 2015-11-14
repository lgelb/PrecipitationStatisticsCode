# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 17:54:09 2015

@author: lucyB570
"""

import matplotlib.pyplot as plt

plt.figure()
plt.plot(PET_BRW2012_tree, color='k', label='tree')
plt.plot(PET_BRW2012_shrub, color='r', label='shrub')
plt.plot(PET_BRW2012_grass,color='g', label='grass')
plt.xlabel('Julian day')
plt.ylabel('PET (mm/day)')
plt.title('daily PET at BRW')
plt.legend()