"""
This file creates an altered dataset of hydrophone data
to isoloate the tremor signals
"""
import obspy
import helpers
import pandas as pd
from datetime import datetime
from multiprocessing import Pool

start = datetime.now()
writing_path = '/media/sda/data/robdata/tremors/{d}.mseed'

def square_stream(stream):
    for s in stream:
        s.data = s.data**2

def apply_function_to_single_day(paths):
    day = helpers.get_stream(paths)
    day.decimate(factor=10)
    day.detrend('demean')
    square_stream(day)
    day.filter(type='lowpass', freq=0.01)
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
    
    pool = Pool(10)
    pool.map(do, datafiles)
    pool.close()
    
#     for d in datafiles:
#         daydata = apply_function_to_single_day(paths=d)
#         day = d[0].split('.')[-1]
        
#         daydata.write(writing_path.format(d=day), type='MSEED')
#         del daydata
#         print('day {d} written, time elapsed: {t}'.format(d=day, t=str(datetime.now()-start)))
    
    print('task completed. you can find data at: {p}'.format(p=writing_path))