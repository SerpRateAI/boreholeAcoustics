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
    day = datadir.split('.')[-1]
    print('finding template for day', day)
    data = tm.digest_data(datadir)

    height = 0.8
    distance = 1.1
    
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