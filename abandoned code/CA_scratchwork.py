# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 21:07:49 2015

@author: Lucy
"""
import multiprocessing
import time, sys, os
import numpy as np
from landlab.io import read_esri_ascii, write_esri_ascii
from landlab import RasterModelGrid as rmg
from Ecohyd_functions_DEM import txt_data_dict, Initialize_, \
                    Empty_arrays, Create_PET_lookup, Save_, Plot_, \
                    SinglePlot_, TimeToStabilizeVeg_, overallVegStats_, \
                    aspectVegStats_, PFTbyAspect_, EstimateStormsPerYear_


if __name__ == '__main__':
    # tells it to make a pool the size of available cores-1
    # this keeps the computer from "locking up" when you are running something
    # by leaving you one core to do other stuff with. If only one core is
    # available it uses that one core.
    replicates = 2
    n_years = 2    # Approx number of years for model to run
    asp = 'NS'

    # modify weather 'up','down','avg'
    # runs average weather
#    wStations = ['BRW', 'LDP', 'Treeline', 'SCR', 'LW']
#    for w in wStations:
#        mpiGO_(weatherstation=w, T='avg', P='avg')

    weatherstation = 'Treeline'
    Temp = 'avg'
    Precip = 'avg'
    iteration = 1
    # Read the DEM
    (grid, elevation) = read_esri_ascii('topoDEM_{}_d100x.asc'.format(asp))
    # Representative grid    
    grid1 = rmg(5,4,5)

    # reads in the inputs
    InputFile = 'CA_veginputs_{}_{}T_{}P.txt'.format(weatherstation, Temp, Precip)
    data = txt_data_dict(InputFile)  # Create dictionary that holds the inputs

    PD_D, PD_W, Rad, Rad_PET, PET_Tree_W, PET_Shrub_W, PET_Grass_W, \
                        PET_Tree_D, PET_Shrub_D, PET_Grass_D, SM, VEG, \
                        vegca = Initialize_(data, grid, grid1, elevation)

    storms = EstimateStormsPerYear_(data)
    n = n_years * storms   # Number of storms the model will be run for

    # creates empty arrays to store data
    P, Tb, Tr, Time, CumWaterStress, VegType, VegTypeN, VegTypeE, VegTypeS, \
                        VegTypeW, PET_, Rad_Factor, EP30, PET_threshold = \
                        Empty_arrays(n, grid, grid1)
    # seasonally different PET lookup table
    # creates an array with values for each PFT for every day of the year
    for i in range(0, 364):
        # Dry Season (about 4000-6500 hrs)
        # Jun 20 to Sept 23 (first day of summer to begning of fall)
        if i < 171 or i > 270:

            Create_PET_lookup(Rad, PET_Tree_D, PET_Shrub_D, PET_Grass_D,
                        PET_, Rad_Factor, EP30, Rad_PET, grid)
        # Wet season
        else:
            Create_PET_lookup(Rad, PET_Tree_W, PET_Shrub_W, PET_Grass_W,
                        PET_, Rad_Factor, EP30, Rad_PET, grid)

    ## Represent current time in years
    current_time = 0            # Start from first day of Jan
    # Keep track of run time for simulation - optional
    Start_time = time.clock()     # Recording time taken for simulation
    # declaring few buffers used in storm loop
    time_check = 0.     # Buffer to store current_time at previous storm
    yrs = 0             # Keep track of number of years passed
    WS = 0.             # Buffer for Water Stress
    Tg = 365            # Growing season in days

    ## Run storm Loop
    for i in range(0, n):  # run from 0 - number of storms
        # Update objects
        # np.floor rounds *down* to an integer, so this figures out what Julian
        # day we're on based on how many days the code has run already
        # it needs to round down, because storms might leave it partly through a day
        # *365 is to change the fraction of a year to a day unit
        Julian = np.floor((current_time - np.floor(current_time)) * 365.)
        # Dry Season (about 4000-6500 hrs)
        if Julian < 166 or Julian > 270:
            PD_D.update()  # dry season rainfall (precipitation distribution)
            P[i] = PD_D.storm_depth
            Tr[i] = PD_D.storm_duration
            Tb[i] = PD_D.interstorm_duration
        else:  # Wet Season - Jul to Sep - NA Monsoon
            PD_W.update()  # wet season rainfall (precipitation distribution)
            P[i] = PD_W.storm_depth
            Tr[i] = PD_W.storm_duration
            Tb[i] = PD_W.interstorm_duration

        grid['cell']['PotentialEvapotranspiration'] =  \
                        (np.choose(grid['cell']['VegetationType'],
                        PET_[Julian])) * Rad_Factor[Julian]
        grid['cell']['PotentialEvapotranspiration30'] =  \
                        (np.choose(grid['cell']['VegetationType'],
                        EP30[Julian])) * Rad_Factor[Julian]
        # soil moisture
        current_time = SM.update(current_time, P=P[i], Tr=Tr[i], Tb=Tb[i])

        if Julian != 364:
            if EP30[Julian + 1, 0] > EP30[Julian, 0]:
                PET_threshold = 1  # 1 corresponds to ETThresholdup
            else:
                PET_threshold = 0  # 0 corresponds to ETThresholddown
        VEG.update(PotentialEvapotranspirationThreshold=PET_threshold)

        WS += (grid['cell']['WaterStress'])*Tb[i]/24.
        Time[i] = current_time

        # Cellular Automata, if it's time to move to the next year
        # if it's been a year since we last entered this loop
        if (current_time - time_check) >= 1.:
            VegType[yrs] = grid['cell']['VegetationType']
            CumWaterStress[yrs] = WS/Tg
            grid['cell']['CumulativeWaterStress'] = CumWaterStress[yrs]
            vegca.update()
            SM.initialize(data, VEGTYPE=grid['cell']['VegetationType'])
            VEG.initialize(data, VEGTYPE=grid['cell']['VegetationType'])
            time_check = current_time
            WS = 0
            # i_check = i
            t = (time.clock()-Start_time)/60
#            print 't = {.2f} minutes, year = {}, storms = '.format(t, yrs), i
            sys.stdout.flush()
            yrs += 1

    # finds what pft is for each aspect (N and S)
    VegType, VegTypeN, VegTypeE, VegTypeS, VegTypeW = PFTbyAspect_(grid, yrs,
                        VegType, VegTypeN, VegTypeE, VegTypeS, VegTypeW)

    # find the year it starts to stabilize
    if yrs < 100:
        yrs_to_stabilize = "too short of a run (<100 yrs)"
    else:
        yrs_to_stabilize = TimeToStabilizeVeg_(VegType, yrs)

    # finds % pft of each veg type
    grass_cov,  shrub_cov,  tree_cov = overallVegStats_(VegType,  yrs)
    grass_covN, shrub_covN, tree_covN = aspectVegStats_(VegTypeN, yrs)
    grass_covE, shrub_covE, tree_covE = aspectVegStats_(VegTypeE, yrs)
    grass_covS, shrub_covS, tree_covS = aspectVegStats_(VegTypeS, yrs)
    grass_covW, shrub_covW, tree_covW = aspectVegStats_(VegTypeW, yrs)

    ## set up saving pathways)
    savepath = os.path.join('saved_data', 'CA_{}_{}r_{}_{}T_{}P_withaspects'
                        .format(asp, replicates, weatherstation, Temp, Precip))

    if not os.path.exists(savepath):
        os.makedirs(savepath)

    Final_time = time.clock()
    Time_Consumed = (Final_time - Start_time)/60.  # in minutes
    # saves this replicate's stats to at txt file
    with open(os.path.join(savepath, 'PFT_statistics.txt'), 'a') as file:
        file.write('{:.2f},{},{},'.format(Time_Consumed, yrs, yrs_to_stabilize))
        file.write('{:.2f},{:.2f},{:.2f},'.format(grass_cov,  shrub_cov,  tree_cov))
        file.write('{:.2f},{:.2f},{:.2f},'.format(grass_covN, shrub_covN, tree_covN))
        file.write('{:.2f},{:.2f},{:.2f},'.format(grass_covE, shrub_covE, tree_covE))
        file.write('{:.2f},{:.2f},{:.2f},'.format(grass_covS, shrub_covS, tree_covS))
        file.write('{:.2f},{:.2f},{:.2f}\n'.format(grass_covW, shrub_covW, tree_covW))

    # saves pft numpy array for the last year
#    np.save(os.path.join(savepath,'VegType_replicate{}'.format(iteration)),VegType[yrs])
#    np.save(os.path.join(savepath,'VegTypeN_replicate{}'.format(iteration)),VegTypeN[yrs])
#    np.save(os.path.join(savepath,'VegTypeS_replicate{}'.format(iteration)),VegTypeS[yrs])

    # use Plot_ to have it draw every yr_step years, SinglePlot_ just gives you the last year
#    SinglePlot_(savepath, grid, VegType, yrs)

#    print 'total time = {}, first stable year = {}, time = {} \n'.format(
#                        Time_Consumed, yrs_to_stabilize, timedatestart)

    timestamp = '{}'.format(time.strftime('%d%b%Y_%H.%M', time.localtime()))
    print('{}, replicate {}, ran for {} years and {:.02f} min, at {}\n'.format(
          weatherstation, iteration, yrs, Time_Consumed, timestamp))
    sys.stdout.flush()
