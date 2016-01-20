# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 21:07:49 2015

@author: Lucy
"""
import multiprocessing, time, sys


def mpiGO_(weatherstation, T, P):

    pool = multiprocessing.Pool(processes=(multiprocessing.cpu_count()-1 or 1))
    for i in range(numreplicates):  # tells how many replicates to do
        # runs replicate i
        pool.apply_async(worker, args=(i, numreplicates, n_years, asp,
                         weatherstation, T, P))
    pool.close()
    pool.join()


def worker(iteration, replicates, n_years, asp, weatherstation, T, P):

    timestamp = '%s' % (time.strftime('%d%b%Y_%H.%M', time.localtime()))
    print('{}, replicate {}, {}\n'.format(weatherstation, iteration, timestamp))
    sys.stdout.flush()


if __name__ == '__main__':

    # tells it to make a pool the size of available cores-1
    # this keeps the computer from "locking up" when you are running something
    # by leaving you one core to do other stuff with. If only one core is
    # available it uses that one core.
    numreplicates = 5
    n_years = 2    # Approx number of years for model to run
    asp = 'NS'
    # modify weather 'up','down','avg'

    wStations = ['BRW', 'LDP', 'Treeline', 'SCR', 'LW']
    for i in wStations:
        mpiGO_(weatherstation=i, T='avg', P='avg')
