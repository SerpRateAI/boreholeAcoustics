"""
This file calculates the standard deviations of the noise levels for data from hole b1
"""
import pandas as pd
import numpy as np
import obspy
import glob
from datetime import datetime
from multiprocessing import Pool
import helpers
from hydrophone_data_processing import load, preprocessing

start = datetime.now()

# def get_stream(paths):
#     """
#     opens the data as an obspy stream from the given list of paths
#     """
#     stream = obspy.read(paths[0])
#     for p in paths[1:]:
#         stream = stream + obspy.read(p)  
    
#     # some days there is multiple files for one day these need to be combined
#     stream.merge(fill_value='latest')
#     stream[3].data = -1 * stream[3].data
#     return stream

def get_std(stream, length_step):
    """
    creates a pandas dataframe with the standard deviations calculated for each hydrophone
    for 60s non-overlapping windows.
    """
    stream_copy = stream.copy()
    # dfstd = pd.DataFrame()
    dfstd = pd.DataFrame(columns=['h0','h1','h2','h3','h4','h5'])
    for window in stream_copy.slide(window_length=length_step, step=length_step):
        dfwindow = pd.DataFrame(window.std()).transpose()
        dfwindow.columns = ['h0','h1','h2','h3','h4','h5']
        dfwindow.index = (window[0].stats['starttime'],)
        dfstd = pd.concat([dfstd, dfwindow])
    # dfstd.columns = ['h0', 'h1', 'h2', 'h3', 'h4', 'h5']
    return dfstd

def get_std_for_one_day(dataloc):
    """
    wrapper function for get_stream and get_std that writes to file the standard deviation
    calculated curves for a single day.
    """
    day = dataloc[0].split('.')[-1]
    year = dataloc[0].split('.')[-2]
    # stream = get_stream(paths=dataloc)
    stream = load.import_corrected_data_for_single_day(julian_day=day, year=year, borehole='b')
    stream.decimate(factor=10)
    stream.detrend('demean')
    # stream.filter(freqmin=6.0, freqmax=8.0, type='bandpass')
    stream.filter(freqmin=5.0, freqmax=10.0, type='bandpass', corners=4, zerophase=True)
    preprocessing.square_stream(stream=stream)
    stream.filter(type='lowpass', freq=0.1, zerophase=True)
    
    std = get_std(stream, length_step=60.0)
    std['day'] = day
    std['year'] = year   
    # test to make sure that the dataframe is the right size otherwise throw an error
    assert std.shape[1] == 8, 'There should be 8 columns but there are {c}, see file {d} for more details'.format(c=std.shape[1], d=dataloc)
    
    csv_loc = '/media/sda/data/robdata/stds/std_{year}_{day}.csv'.format(year=year, day=day)
    std.to_csv(csv_loc, index=True)
    print('writing', csv_loc, 'to file')
    print('elapsed time:', str(datetime.now() - start))
    del day, year, stream, std, csv_loc


if __name__=='__main__':
    print('process started at', str(start))
    
    datafiles = helpers.create_datafiles()
    # create a processor pool to ingest the data, by default uses all processors, we use 10 here
    pool = Pool(15)
    pool.map(get_std_for_one_day, datafiles)
    pool.close()
    print('process finished at', datetime.now()-start)
    print('detection tables and similiarity scores can be found at',  '/media/sda/data/borehole/detections/')