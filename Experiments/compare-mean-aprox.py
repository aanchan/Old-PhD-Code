'''
Created on Mon Jul 11 10:50:07 2011

@author: -
'''
from ControlCharts import Tseries
from CUSUM import cusum 
import numpy as np
import matplotlib.pyplot as plt
from Frahst_v3_1 import FRAHST_V3_1
from SPIRIT import SPIRIT
from utils import QRsolveA, pltSummary, pltSummary2, GetInHMS, writeRes
from AnomalyMetrics import analysis, fmeasure, aveMetrics
from plot_utils import plot_4x1
import scipy
import time
from PedrosFrahst import frahst_pedro
import pickle as pk
import os

def MA_over_window(data, window_length):
    """ Incremental Average of last N data points 
    This is the fastest implimentation and has been tested to be equivilant to the above 
    """
    window = np.zeros((data.shape[1], window_length))
    Av = np.zeros(data.shape[1])
    Aved_data = np.zeros_like(data)
    
    for i in range(data.shape[0]):
        new_data_vec = data[i]
        dropped_data_vec = window[:,0].copy()
        window[:,:-1] = window[:,1:] # Shift Window
        window[:,-1] = new_data_vec
        # update average incrementally
        Av = Av + ((new_data_vec - dropped_data_vec)/ float(window_length))  
        
        Aved_data[i] = Av
        
    return Aved_data

def EWMA(data, N):
    """ Exponetially Weighted Moving Average """    
    alpha = 2.0 / (N + 1) 
    aved_data = np.zeros_like(data)
    u = np.zeros(data.shape[1])
    for i in range(data.shape[0]):
        new_data_vec = data[i]
        u = u * (1-alpha) + new_data_vec * alpha
        aved_data[i] = u
    return aved_data

def weighted_MA(data, N):
    """ MA fractionally wighted of last N time steps """
    window = np.zeros((data.shape[1], N))
    wma = np.zeros(data.shape[1])    
    Aved_data = np.zeros_like(data)
    SumX = np.zeros(data.shape[1])
    denominator = N * (N+1) / float(2.0)
    
    for i in range(data.shape[0]):
        new_data_vec = data[i]

        dropped_data_vec = window[:,0].copy()
        window[:,:-1] = window[:,1:] # Shift Window
        window[:,-1] = new_data_vec
        
        wma = wma + (((N * new_data_vec) - SumX) / denominator)
        SumX = SumX + new_data_vec - dropped_data_vec        
        
        # update average incrementally
        Aved_data[i] = wma
        
    return Aved_data
    

def CMA(data):
    """ Simple Cummulative Moving Average
    Looks at entire history of data
    """
    # Update CMA
    cma = np.zeros(data.shape[1])
    aved_data = np.zeros_like(data)
    for i in range(data.shape[0]):
        t = i + 1 
        new_data_vec = data[i]
        cma = cma + ((new_data_vec - cma)/ float(t + 1))
        aved_data[i] = cma
    return aved_data

def fractional_MA(data):
    """ MA based on incremetal time fractions """
    aved_data = np.zeros_like(data)
    u = np.zeros(data.shape[1])
    for i in range(data.shape[0]):
        t = i + 1
        new_data_vec = data[i]
        u = ((t - 1)/float(t)) * u + (1/float(t)) * new_data_vec
        aved_data[i] = u
    return aved_data

def fractional_decay_MA(data, alpha):
    """ MA based on incremetal time fractions """
    aved_data = np.zeros_like(data)
    u = np.zeros(data.shape[1])
    for i in range(data.shape[0]):
        t = i + 1
        new_data_vec = data[i]
        u = ((t - 1)/float(t)) * alpha * u + (1/float(t)) * new_data_vec
        aved_data[i] = u
    return aved_data
    
if __name__ == '__main__':
    # Create Series 
    s0 = Tseries(0)
    s1 = Tseries(0)
    s2 = Tseries(0)
    
    s0.makeSeries([1,3,1], [100,10,190], base = [0, 0, 2], gradient = 0.2, noise = 0.5)
    s1.makeSeries([1,4,1], [200,10,90], base = [0, 0, -2], gradient = 0.2, noise = 0.5)
    s2.makeSeries([1], [300], noise = 0.5)
    
    streams = scipy.c_[s0, s1, s2]
    
    N = 25
    
    # Test Moving Averages
    MA1 = MA_over_window1(streams, N)
    MA2 = MA_over_window2(streams, N)
    MA3 = MA_over_window3(streams, N)
    cma = CMA(streams)
    ewma = EWMA(streams, N)
    fracMA = fractional_MA(streams)
    frac_decMA = fractional_decay_MA(streams, 0.9)
    
    wma = weighted_MA(streams, N)