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

templates = [
    tm.make_template('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.138' , '2019-05-18T14:36:16.178Z', '2019-05-18T14:36:16.304Z')
        ,
    ]


def find_template_in_data(datadir):
    day = datadir.split('.')[-1]
    print('finding template for day', day)
    data = tm.digest_data(datadir)

#     height = 0.875
    # i have increased the height to 0.92 because below that it picks up tiny signals that we define as possible electrical noise
    # all the events below 0.92 similarity in this run are happening simultaneously on all hydrophones
    height = 0.92
    distance = 1.1
    
#     templates = [
#         tm.make_template('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.138' , '2019-05-18T14:36:16.178Z', '2019-05-18T14:36:16.304Z')
#         ,
#     ]
    detections, sims = correlation_detector(stream=data
                                    , templates=templates
                                    , heights=height
                                    , distance=distance
                                    , plot=None)
    data_writing_location = '/media/sda/data/borehole/detections/' + day
    try:
        sims[0].write(data_writing_location + 'similarity.mseed', format='MSEED')
    except AttributeError:
        print('there is an error writing similarity for day', str(day))
    df = pd.DataFrame(detections)
    df.to_csv(data_writing_location + 'detections.csv', index=False)
    del detections, sims, df, data

if __name__=='__main__':
    start = datetime.now()
    print('process started at', str(start))
    
    datafiles2019 = glob.glob('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.*')
    datafiles2020 = glob.glob('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2020.*')
    datafiles = datafiles2019 + datafiles2020

    # create a processor pool to ingest the data, by default uses all processors
    pool = Pool()
    pool.map(find_template_in_data, datafiles)
    pool.close()
    print('process finished at', datetime.now()-start)
    print('detection tables and similiarity scores can be found at',  '/media/sda/data/borehole/detections/')
    
