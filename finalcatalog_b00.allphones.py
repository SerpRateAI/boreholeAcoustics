from obspy import read, UTCDateTime as UTC
from obspy.signal.cross_correlation import correlation_detector
import obspy
import io
import matplotlib.pyplot as plt
import helpers
import numpy as np
import pandas as pd

from obspy.signal import trigger
from obspy.signal import filter

from datetime import datetime

from multiprocessing import Pool
import glob

import tempmatch as tm

data = tm.digest_data('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.138')
data += tm.digest_data('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.02.GDH.2019.138')
data += tm.digest_data('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.03.GDH.2019.138')
data += tm.digest_data('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.04.GDH.2019.138')
data += tm.digest_data('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.05.GDH.2019.138')
data += tm.digest_data('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.06.GDH.2019.138')

data[3].data = data[3].data*-1

templates = data.select(id='7F.B00.01.GDH').slice(UTC('2019-05-18T14:36:16.178Z'), UTC('2019-05-18T14:36:16.304Z'))
templates += data.select(id='7F.B00.02.GDH').slice(UTC('2019-05-18T14:36:16.22Z'), UTC('2019-05-18T14:36:16.35Z'))
templates += data.select(id='7F.B00.03.GDH').slice(UTC('2019-05-18T14:36:16.26Z'), UTC('2019-05-18T14:36:16.4Z'))
templates += data.select(id='7F.B00.04.GDH').slice(UTC('2019-05-18T14:36:16.3Z'), UTC('2019-05-18T14:36:16.45Z'))
templates += data.select(id='7F.B00.05.GDH').slice(UTC('2019-05-18T14:36:16.35Z'), UTC('2019-05-18T14:36:16.50Z'))
templates += data.select(id='7F.B00.06.GDH').slice(UTC('2019-05-18T14:36:16.40Z'), UTC('2019-05-18T14:36:16.60Z'))

del data

def find_template_in_data(datadir):
    # control for if there are multiple traces
    # or only a single trace
    if len(datadir)==6:
        # multiple traces (assuming 6 hydrophones)
        data = tm.digest_data(datadir[0])
        for d in datadir[1:]:
            data += tm.digest_data(d)
        
        # flip the signal on hydrophone 4 because the leads were installed incorrectly
        data[3].data = data[3].data * -1
        
        day = datadir[0].split('.')[-1]
        year = datadir[0].split('.')[-2]
        
    else:
        # single trace
        tm.digest_data(datadir)
        day = datadir.split('.')[-1]
        year = datadir[0].split('.')[-2]
        
    print('finding events for {y}.{d}'.format(y=year, d=day))
        
    height = 0.8
    distance = 1.1
    
    detections, sims = correlation_detector(
                                    stream=data
                                    , templates=templates
                                    , heights=height
                                    , distance=distance
                                    , plot=None
                                    # , similarity_func=tm.simf
                                           )
    
    data_writing_location = '/media/sda/data/borehole/detections/' + day
    
    ####
    #### I have removed this because I feel like it takes up a lot of time
    ####
    # try:
    #     sims[0].write(data_writing_location + 'similarity.mseed', format='MSEED')
    # except AttributeError:
    #     print('there is an error writing similarity for day', str(day))
        
    df = pd.DataFrame(detections)
    print('detected {n} events on day {y}.{d}'.format(n=df.shape[0], d=day, y=year))
    df.to_csv(data_writing_location + 'detections.csv', index=False)
    del detections, sims, df, data

if __name__=='__main__':
    start = datetime.now()
    print('process started at', str(start))
    
    datafiles = []
    
    # days = np.unique(
    #             np.array(
    #                 [d.split('.')[-1] for d in glob.glob('/media/sda/data/robdata/Hydrophones/DAYS/B00/*')]
    #                     )
    #                 )
    # years = 
    
    years_days = [d.split('.')[-2:] for d in glob.glob('/media/sda/data/robdata/Hydrophones/DAYS/B00/*')]
    years_days = np.array([list(x) for x in set(tuple(x) for x in years_days)])
    
#     for y in [2019, 2020]:
#         # for d in np.arange(1, 366, 1):
#         for d in days:
#             day_dirs = []
#             for s in [1,2,3,4,5,6]:
#                 dir = '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.0{s}.GDH.{y}.{d}'.format(s=s, y=y, d=d)
#                 day_dirs.append(dir)
                
#             datafiles.append(day_dirs)

    for y, d in years_days:
        day_dirs = []
        for s in [1,2,3,4,5,6]:
            dir = '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.0{s}.GDH.{y}.{d}'.format(s=s, y=y, d=d)
            day_dirs.append(dir)
        datafiles.append(day_dirs)
                

    # create a processor pool to ingest the data, by default uses all processors, we use 10 here
    pool = Pool(10)
    pool.map(find_template_in_data, datafiles)
    pool.close()
    print('process finished at', datetime.now()-start)
    print('detection tables and similiarity scores can be found at',  '/media/sda/data/borehole/detections/')