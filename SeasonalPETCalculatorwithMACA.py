# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 12:17:47 2015
This code takes in cleaned DCEW weather data and returns the PET value in
mm/day for that area based on 4 different pfts (bare,grass,shrub,tree)
thanks to: http://edis.ifas.ufl.edu/pdffiles/ae/ae45900.pdf
and: http://www.luiw.ethz.ch/labor2/experimente/exp4/Presentation/Net_Longwave_Radiation
and: http://edis.ifas.ufl.edu/ae459
if you get list index out of range errors when using loadtxt, open the
offending file and replace all cells that are '#VALUE!' with '-6999'

You will get 'RuntimeWarning: Mean of empty slice warnings.warn("Mean of empty
slice", RuntimeWarning)' once for each year with missing data, *3 for each PFT

Irregular windspeed causes lots of data irregularities, mostly PET spikes. To
deal with this I've held windspeed (U2) constant over a year as its mean. The
code below also includes a roling mean and FFT function, but those are not as
reliable.

@author: lucyB570
"""
import numpy
import os
import matplotlib.pyplot as plt


def pftPET_(pft, albedo, usecolumns):

    # gets daily PET for all years
    for n in range(numyears):  # +1 exclusive
        # creates filename
        filename = os.path.join(stationstats['weatherstation'],
                                "{}_HrlySummary_{}.csv".format(
                                stationstats['weatherstation'],
                                (n+stationstats['startyear'])))
        # calculates yearly PET
        PET[:, (n)] = calcPET_(filename, stationstats, n, albedo, usecolumns)

    ''' the below code allows for troubleshooting with just one year'''
#    filename = os.path.join(stationstats['weatherstation'],
#                        "{}_HrlySummary_{}.csv".format(
#                        stationstats['weatherstation'],
#                        (2013)))
#    PET[:, (1)] = calcPET_(filename, stationstats, 1, albedo)

    if plotyearlyPET:
        plotPET_(pft, PET, stationstats)

    # finds wet and dry season PET for each year
    (PETwet, PETdry) = seasonalPET_(PET)

    output = range(stationstats['startyear'], stationstats['endyear']+1)
    output = numpy.vstack((output, PETwet, PETdry))
    output = output.transpose()
    totmeans = numpy.nanmean(output, axis=0)

    # saves calculated PET values in the weather station's folder as
    # '<station>_PET_values.csv'
    if saveyearlyPET:
        with open(os.path.join(stationstats['weatherstation'],
                               '{}.txt.'.format(runname)), 'a') as text_file:
            text_file.write('PFT: {}\n'.format(pft))
            text_file.write('wet season average= {:.3f}, '.format(totmeans[1]))
            text_file.write('dry season average= {:.3f}\n'.format(totmeans[2]))


def calcPET_(filename, stationstats, n, a, usecolumns):

    # atmospheric pressure (kPa)
    P = 101.3*(((293-0.0065*stationstats['z'])/293)**5.26)
    gamma = 0.000665*P  # psycromatic constant

    # read in and unpack data
    (precipHourly, temperatureC, solarradiation, netradiation,
     relativehumidity, winddirectiondegree, windspeed, snowdepthcm) = \
     numpy.loadtxt(filename, delimiter=",", usecols=[1, 2, 3, 4, 5, 6, 7, 8],
                   skiprows=20, unpack=True)

    (precipHourly, temperatureC, solarradiation, netradiation,
     relativehumidity, winddirectiondegree, windspeed, snowdepthcm) = \
        cleanData_(precipHourly, temperatureC, solarradiation, netradiation,
                   relativehumidity, winddirectiondegree, windspeed,
                   snowdepthcm)
#    #removes negative net radiation values
#    for i,elem in enumerate(netradiation):
#        if netradiation[i]<0:
#            netradiation[i]=numpy.nan

    missingData = checkMissingData_(precipHourly, temperatureC, solarradiation,
                                    netradiation, relativehumidity,
                                    winddirectiondegree, windspeed,
                                    snowdepthcm)

    # if any of the variables are missing all data, terminates this function
    # and returns ETo (PET vector) as nans
    if missingData:
        ETo = [numpy.nan]*365
        return ETo

    ''' To get windspeed: either use FFT, rolling mean, or constant median.
        Comment out the unused options.'''
    # constant median (reshape before)
    tempU2 = numpy.nanmean(windspeed.reshape(-1, 24), axis=1)
    # finds median value for whole year
    tempU2[:] = numpy.nanmean(tempU2)
    '''option changes end here'''
#    # FFT (reshape before FFT function_)
#    tempU2 = numpy.nanmean(windspeed.reshape(-1, 24), axis=1)
#    # fast fourier transform, cutoffFrequency = 5 seems best
#    tempU2 = FFT_(tempU2, 5) #only doing 1 year. WTF?

#    # rolling mean (needs no reshape)
#    # still get spikes, might be better if switch median for mean
#    tempU2 = rollingMedian_(windspeed, 24)

    # no need to worry about precip data, since it's not a used variable

    startday = 365*n
    # reads in all average daily temp values
    csv = numpy.genfromtxt('MACAdata\\MOD85TreelineDCEW.csv', delimiter=",")
    tempTmin = csv[:, usecolumns[0]]
    tempTmax = csv[:, usecolumns[1]]
    tempTmean = csv[:, usecolumns[2]]
    # cuts it down to the needed years
    tempTmin = tempTmin[startday:startday+len(tempU2)]
    tempTmax = tempTmax[startday:startday+len(tempU2)]
    tempTmean = tempTmean[startday:startday+len(tempU2)]

    # daily net radiation in MJ/m2/dayF
    tempRs = (numpy.nanmean(netradiation.reshape(-1, 24), axis=1))*0.0864

    # slope of saturation vapor pressure curve
    tempIhat = (4098*(0.6108**((17.21*tempTmean)/(
                tempTmean+237.3))))/((tempTmean+237.3)**2)
    # delta term (aux calc for radiation term)
    tempDT = tempIhat/(tempIhat+gamma*(1+0.34*tempU2))
    # psi term (aux calc for wind term)
    tempPT = gamma/(tempIhat+gamma*(1+0.34*tempU2))
    # temperature term (aux calc for wind term)
    tempTT = (900/(tempTmean+273))**tempU2
    # saturation air pressure from air temp
#    tempeTmean=0.6108**((17.27+tempTmean)/(tempTmean+237.3)) #unused
    tempeTmax = 0.6108**(17.27*tempTmax/(tempTmax+237.3))
    tempeTmin = 0.6108**(17.27*tempTmin/(tempTmin+237.3))
    # mean saturation vopor pressure
    tempes = (tempeTmax+tempeTmin)/2
    # relative humidity
    tempRHmax = numpy.nanmax(relativehumidity.reshape(-1, 24), axis=1)
    tempRHmin = numpy.nanmin(relativehumidity.reshape(-1, 24), axis=1)
    # acutal vapor pressure from relative humidity
    tempea = (tempeTmin*tempRHmax/100+tempeTmax*tempRHmin/100)/2
    # inverse relative distance earth-sun
    tempdr = [1+0.033*numpy.cos((2*numpy.pi/365) *
                                (i+1)) for i, elem in enumerate(tempea)]
    # solar declination
    tempSdec = [0.409*numpy.sin(((2*numpy.pi/365) *
                                (i+1))-1.39) for i, elem in enumerate(tempea)]
    # sunset hour angle
    tempOmegas = numpy.arccos(-numpy.tan(stationstats['latitude']) *
                              numpy.tan(tempSdec))
    # extraterrestrial radiation
    tempRa = ([24*60/numpy.pi*0.0820*x for x in tempdr]) * \
        ((tempOmegas*numpy.sin(stationstats['latitude']) *
         numpy.sin(tempSdec))+(numpy.cos(stationstats['latitude']) *
         numpy.cos(tempSdec)*numpy.sin(tempOmegas)))
    # clear sky solar radiation
    tempRso = (0.75+2*numpy.exp(-5)*stationstats['z'])*tempRa
    # net soloar or net shortwave radiation
    tempRns = (1-a)*tempRs
    # net outgoinglongwave solar radiation (sigma is stefan-boltzman constant)
    tempRnl = 4903.10**-9*((tempTmax+273.16)**4+(tempTmin+273.16)**4)/2 \
        * (0.34-0.14*numpy.sqrt(tempea))*(1.35*tempRs/tempRso-0.35)
    # net radiation in MJ m-2 day-1
    tempRn = tempRns-tempRnl
    # net radiation in mm
    tempRng = 0.408*tempRn
    # radiation term
    tempETrad = tempDT*tempRng
    # wind term
    tempETwind = tempPT*tempTT*(tempes-tempea)
    # FINAL evaportranspiration value
    ETo = tempETwind+tempETrad
    ETo = ETo[0:365]
    ETo[ETo < 0] = numpy.NaN

    return ETo


def cleanData_(*argv):
    '''this removes all missing data'''
    for arg in argv:
        for i, elem in enumerate(arg):
            if arg[i] == -6999:
                arg[i] = numpy.NAN
    return argv
'''for some reason this bit below doesn't work, but isn't needed?'''
#        # remove Dec 31st on leap years so arrays are the same size
#        if len(arg)>8760:
#            arg=arg[0:8760]
#    return argv #why does adding/deleting this not change anything?


def checkMissingData_(*argv):
    '''if the input for a whole year is missing, return True'''
    temp = False
    for i, arg in enumerate(argv):
        # if all values of one variable are missing (NaNs)
        if numpy.all(numpy.isnan(arg)):
            temp = True
    return temp


def FFT_(data, cutoffFrequency):

    tm = [i for i in range(len(data))]  # time vector
    npts = len(tm)
    dt = 0.001
    frq = numpy.zeros(npts+1)  # +1 because 0 indexing

    # this loop creates a frequency vector for plotting in the frequency domain
    for j in range(npts+1):
        frq[j] = (j-1)/(npts*dt)
    frq = frq[1:]  # gets rid of the +1 for 0 indexing

    hk = numpy.fft.fft(data)
    df = 1/(npts*dt)
    Jc = numpy.int((cutoffFrequency/df)+1)  # define cutoff frequency
    W = numpy.zeros(npts)  # weighting vector
    W[0] = 1

    # positive bits of the complex circle
    W[2:Jc] = 1
    # negative bits of the complex circle
    W[npts+1-Jc:npts+1] = 1

    # multiply weight by original signal
    windowed_signal = hk*W
    # inverse fft to go back to time domain
    wind_sig_tm = abs(numpy.fft.ifft(windowed_signal))

#    plt.figure(4)
#    plt.plot(tm, wind_sig_tm)
#    plt.xlim(min(tm), max(tm))
#    plt.xlabel('time (s)')
#    plt.ylabel('amplitude')
#    plt.title('Windowed signal, time domain')

    return wind_sig_tm


def rollingMedian_(data, window):

    # rolling mean
    y = numpy.zeros((len(data),))
    for ctr in range(len(data)):
        y[ctr] = numpy.sum(data[ctr:(ctr+window)])
    final = y/window

    final = numpy.nanmedian(final.reshape(-1, 24), axis=1)

#    plt.figure()
#    plt.plot(final)
#    plt.xlim(0,365)
#    plt.xlabel('Julian Day')
#    plt.ylabel('windspeed')
#    plt.title('{} {} (window = {}) frequency in time domain'.format(
#              stationstats['weatherstation'], n+stationstats['startyear'],
#              window))

    return final


def plotPET_(pft, dataArray, stationstats):
    '''what it says in the name, only plots if plotyearlyPET == True'''

    # you need yearlabels so you can have a legend when you plot yearly pet
    # +1 exclusive indexing
    yearlabels = range(stationstats['startyear'], stationstats['endyear']+1)

    plt.figure()
    for i in range(len(dataArray[0])):
        plt.plot(dataArray[:, i], label=yearlabels[i])
    plt.xlim(0, 365)
    plt.xlabel('Julian day')
    plt.ylabel('PET (mm/day)')
    plt.legend(loc=1)
    plt.title('daily {} PET at {}'.format(pft, stationstats['weatherstation']))
    plt.savefig(os.path.join(stationstats['weatherstation'],
                '{}_{}.svg'.format(runname, pft)), bbox_inches="tight",
                format='svg')


def seasonalPET_(PET):
    '''this will break PET into wet and dry seasons, get averages'''

    # initially based on stormstatsgenerator precip graph from
    begSummer = 171
    # DCEW stations,but adjusted slightly to start of summer&fall
    endSummer = 266

    # concatonates spring and fall/winter values
    tempwetPET = PET[0:begSummer:1]
    tempwetPET = numpy.append(tempwetPET, PET[endSummer:365:1], axis=0)

    PETwet = numpy.nanmean(tempwetPET, axis=0)
    PETdry = numpy.nanmean(PET[begSummer:endSummer:1], axis=0)
    return PETwet, PETdry

if __name__ == '__main__':

    BRW = {'weatherstation': 'BRW', 'startyear': 2011, 'endyear': 2014,
           'z': 2114, 'latitude': 43.75876, 'longitude': -116.090404}  # z in m
    # 2014 LDP is off
    LDP = {'weatherstation': 'LDP', 'startyear': 2007, 'endyear': 2013,
           'z': 1850, 'latitude': 43.737078, 'longitude': -116.1221131}
    Treeline = {'weatherstation': 'Treeline', 'startyear': 1999,
                'endyear': 2014, 'z': 1610, 'latitude': 43.73019,
                'longitude': -116.140143}
    # 2010 of SCR is empty,
    SCR = {'weatherstation': 'SCR', 'startyear': 2010, 'endyear': 2013,
           'z': 1720, 'latitude': 43.71105, 'longitude': -116.09912}
    # 2013 and 2014 of Lower Weather are off
    LowerWeather = {'weatherstation': 'LowerWeather', 'startyear': 1999,
                    'endyear': 2012, 'z': 1120, 'latitude': 43.6892464,
                    'longitude': -116.1696892}

    '''something funny with scr data'''

    stationstats = Treeline
    plotyearlyPET = True
    saveyearlyPET = True
    useMACAdata = True

    # albedo values are for summer, snow-off, tree=conifer, shrub=sagebrush
    pftAlbedo = {'grass': 0.23, 'shrub': 0.14, 'tree': 0.08}  # 'bare':0.17
    # this is for troubleshooting so you don't have 4 different plots
    # crowding things up
#    pftAlbedo={'grass':0.23}

    # # +1 exclusinve indexing
    numyears = stationstats['endyear']-stationstats['startyear']+1
    PET = numpy.empty((365, numyears,))
    PET[:] = numpy.NaN
    columnsavg = [3, 4, 5]
    columnsinc = [6, 7, 8]
    columnsdec = [9, 10, 11]
    
    '''change the following 'runname' name, and check line 120 is correct'''
    if useMACAdata:
        runname = 'PET_{}_mod85'.format(stationstats['weatherstation'])
        # finds PET for all pft albedo values (4)
        with open(os.path.join(stationstats['weatherstation'],
                  '{}.txt.'.format(runname)), 'a') as text_file:
            text_file.write('\nDCEW values increased by MACA\n')
        for k, v in pftAlbedo.items():
            pftPET_(k, v, columnsinc)
        # finds PET for all pft albedo values (4)
        with open(os.path.join(stationstats['weatherstation'],
                  '{}.txt.'.format(runname)), 'a') as text_file:
            text_file.write('\nDCEW values decreased by MACA\n')
        for k, v in pftAlbedo.items():
            pftPET_(k, v, columnsdec)
    else:  # THIS DOESN'T WORK?
        runname = 'PET_{}_obs'.format(stationstats['weatherstation'])
        # finds PET for all pft albedo values (4)
        for k, v in pftAlbedo.items():
            pftPET_(k, v, columnsavg)
