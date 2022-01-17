"""
This module automates the cross correlation data set creation
"""
import os
import sys
sys.path.append(os.getcwd())

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

# import tempmatch as tm
import obspy
from obspy.signal import cross_correlation

# from hydrophone_data_processing import load, preprocessing
import load, preprocessing

import itertools

from datetime import datetime

hydrophones = [0, 1, 2, 3, 4, 5]
hydrophone_pairs = [h for h in itertools.combinations(hydrophones, 2)]

def preprocess_data_for_cc(data):
    data.decimate(factor=10)
    data.filter(freqmin=5, freqmax=10, corners=4, type='bandpass', zerophase=True)
    data.detrend('demean')
    preprocessing.square_stream(data)
    return data

def get_windowed_data(data, window_length=1*60.):
    """
    returns a generator of windowed data. window lengths default to 60 seconds.
    
    the returned window slice is an obspy Stream object
    """
    return data.copy().slide(window_length=window_length, step=window_length)

def calculate_cc_dataframe(windowed_data, shift=100*5):
    """
    Calculates the cross-correlation scores between two windows that slide
    between the start and end times according to shift, which defaults to
    +/- 500 ms.
    
    Returns a dataframe with calculated statistics.
    """
    shift = 100*5
    cc_df = pd.DataFrame()
    n = -1
    for window in windowed_data:
        n += 1
        for pair in hydrophone_pairs:
            h1, h2 = pair
            # cc = obspy.signal.cross_correlation.correlate(a=window[h1]
            cc = cross_correlation.correlate(a=window[h1]
                                            ,b=window[h2]
                                            ,shift=shift
                                            ,demean=True
                                            ,normalize=False)
            # cc_norm = obspy.signal.cross_correlation.correlate(a=window[h1]
            cc_norm = cross_correlation.correlate(a=window[h1]
                                                ,b=window[h2]
                                                ,shift=shift
                                                ,demean=True
                                                ,normalize=True)
            window_df = pd.DataFrame(
                {
                    'window_index':[n,]
                    ,'h1_index':(h1,) # first hydrophone index used for cross correlation
                    , 'h2_index':(h2,) # second hydrophone index used for cross correlation
                    ,'cross_correlation_max':[cc.max(),]
                    ,'cross_correlation_index':[np.argmax(cc),]
                    ,'sample_rate':[window[0].stats.sampling_rate,]
                    ,'window_starttime':[window[0].stats.starttime,]
                    ,'window_endtime':[window[0].stats.endtime]
                    ,'lagtime_seconds':((np.argmax(cc)-500)*1/100.,)
                    ,'cc_estimator':(cc,)
                    ,'cc_estimator_normed':(cc_norm,)
                    ,'cc_normed_max':(cc_norm.max(),)
                    ,'cc_normed_idx':(np.argmax(cc_norm),)
                    ,'normed_lagtime':((np.argmax(cc_norm)-500)/100.,)
                }
            )
            cc_df = pd.concat([cc_df, window_df])
    cc_df.reset_index(inplace=True)
    return cc_df
    


if __name__=='__main__':
    starttime = datetime.now()
    print('process started at', str(starttime))
    
    day138 = load.import_corrected_data_for_single_day(julian_day='138', year='2019', borehole='b')
    day138 = preprocess_data_for_cc(day138)
    
    freqs = [0.1, 0.5]
    for freq in freqs:
        data = day138.copy()
        data.filter('lowpass', freq=freq, corners=4, zerophase=True)
        data = get_windowed_data(data)
        ccdf = calculate_cc_dataframe(data)
        ccdf.to_csv('/media/sda/data/robdata/tremors/xcorr/cc_{f}.csv'.format(f=freq), index=True)
    # day138_01 = day138.copy()
    # day138_01 = get_windowed_data(day138_01)
    # ccdf_01 = calculate_cc_dataframe(day138_01)
    # ccdf_05
    
    print('process finished after', str(datetime.now()-starttime))
    
    
    