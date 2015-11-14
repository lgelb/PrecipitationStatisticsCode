# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 16:45:41 2015

@author: Lucy
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy
import matplotlib.pyplot as plt


data = numpy.loadtxt('Treeline_HrlySummary_2012.csv', delimiter=",",
                     usecols=[7], skiprows=20, unpack=True)

tm = [i for i in range(len(data))]  # time vector
s = data
npts = len(tm)
dt = 0.001
frq = numpy.zeros(npts+1)  # +1 because 0 indexing

# this loop creates a frequency vector for plotting in the frequency domain
for j in range(npts+1):
    frq[j] = (j-1)/(npts*dt)
frq = frq[1:]  # gets rid of the +1 for 0 indexing

hk = numpy.fft.fft(s)
df = 1/(npts*dt)
f =5  # cutoff frequency (from inspection())
Jc = numpy.int((f/df)+1)  # define cutoff frequency
W = numpy.zeros(npts)  # weighting vector
W[0] = 1

for j in range(2, Jc):
    W[j] = 1  # positive bits of the coplex circle
    K = npts+1-j
    W[K] = 1  # negative bits of the complex circle

# multiply weight by original signal
windowed_signal = hk*W

# inverse fft to go back to time domain
wind_sig_tm = abs(numpy.fft.ifft(windowed_signal))

plt.figure(4)
plt.plot(tm, wind_sig_tm)
plt.xlim(min(tm), max(tm))
plt.xlabel('time (s)')
plt.ylabel('amplitude')
plt.title('Windowed signal, time domain')
