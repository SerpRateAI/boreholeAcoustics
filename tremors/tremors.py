"""
This file creates an altered dataset of hydrophone data
to isoloate the tremor signals
"""
import obspy
import helpers
import pandas as pd
from datetime import datetime
from multiprocessing import Pool
from hydrophone_data_processing import load, preprocessing

start = datetime.now()
writing_path = '/media/sda/data/robdata/tremors/{d}.mseed'

def square_stream(stream):
    for s in stream:
        s.data = s.data**2
        
def convert_paths_to_day_year_borehole(path):
    """
    some functions need paths, some functions just want the raw informations
    
    This converts from paths to raw information
    """
    path = path[0]
    path = path.split('.')
    julian_day = path[-1]
    year = path[-2]
    borehole = path[-6][0]
    return julian_day, year, borehole

def apply_function_to_single_day(paths):
    # day = helpers.get_stream(paths)
    julian_day, year, borehole = convert_paths_to_day_year_borehole(path=paths)
    day = load.import_corrected_data_for_single_day(julian_day, year, borehole='b')
    day.decimate(factor=10)
    day.detrend('demean')
    square_stream(day)
    # day.filter(type='lowpass', freq=0.01)
    day.filter(type='lowpass', freq=0.1, zerophase=True, corners=4)
    return day

def do(paths):
    daydata = apply_function_to_single_day(paths=paths)
    day = paths[0].split('.')[-1]
    daydata.decimate(factor=10)
    daydata.write(writing_path.format(d=day), type='MSEED')
    del daydata
    print('day {d} written, time elapsed: {t}'.format(d=day, t=str(datetime.now()-start)))
        
if __name__=='__main__':
    
    print('started at {t}'.format(t=str(start)))
    
    datafiles = helpers.create_datafiles()
    print('data file locations created ...')
    
    pool = Pool(15)
    pool.map(do, datafiles)
    pool.close()
    
    print('task completed. you can find data at: {p}'.format(p=writing_path))