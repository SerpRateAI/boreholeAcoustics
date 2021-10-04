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

def digest_data(filedir):
    stream = obspy.read(filedir)
    stream.merge()
    stream.detrend('demean')
    stream.normalize()
    stream[0].data = filter.highpass(stream[0].data, freq=40, df=1000)
#     stream[0].data = filter.lowpass(stream[0].data, freq=5, df=1000)
#     stream[0].data = filter.lowpass(stream[0].data, freq=40, df=1000)
#     stream[0].data = filter.highpass(stream[0].data, freq=5, df=1000)
    return stream

def make_template(templatedir, starttime, endtime):
    template = digest_data(templatedir)
    pick1 = UTC(starttime)
    pick2 = UTC(endtime)
    template = template.trim(pick1, pick2)
    return template

def find_templates_in_data():
    pass

# def make_template():
#     template_dir = '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.138'
#     template = digest_data(template_dir)
#     pick = UTC('2019-05-18T11:57:41.532000Z')
#     template = template.trim(pick-0.025, pick+0.25)
#     return template

# def make_template_1():
#     template_dir = '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.274'
#     template = digest_data(template_dir)
#     pick1 = UTC('2019-10-01T12:32:11.92Z')
#     pick2 = UTC('2019-10-01T12:32:12.13Z')
#     template = template.trim(pick1, pick2)
#     return template

# def make_template_2():
#     template_dir = '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.274'
#     template = digest_data(template_dir)
#     pick1 = UTC('2019-05-18T12:03:10.30Z')
#     pick2 = UTC('2019-05-18T12:03:10.50Z')
#     template = template.trim(pick1, pick2)
#     return template

# def make_template_3():
#     template_dir = '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.274'
#     template = digest_data(template_dir)
#     pick1 = UTC('2019-05-18T12:06:05.055Z')
#     pick2 = UTC('2019-05-18T12:06:05.20Z')
#     template = template.trim(pick1, pick2)
#     return template

def find_template_in_data(datadir):
    day = datadir.split('.')[-1]
#     print('finding template for day', datadir.split('.')[-1])
    print('finding template for day', day)
    data = digest_data(datadir)
    height = 0.875
    distance = 3
#     template = make_template()
#     template2 = make_template_1()
#     templates = [template, template2]\
    templates = [make_template()
                ,make_template_1()
                ,make_template_2()
                ,make_template_3()]
    detections, sims = correlation_detector(stream=data
#                                         , templates=template
                                        , templates=templates
                                        , heights=height
                                        , distance=distance
                                        , plot=None)
#     data_writing_location = '/media/sda/data/borehole/detections/' + datadir.split('.')[-1]
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
    
    # get data file locations for importing
    datafiles2019 = glob.glob('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.*')
    datafiles2020 = glob.glob('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2020.*')
    datafiles = datafiles2019 + datafiles2020
    
    # create template
#     template = make_template()
    
    # create a processor pool to ingest the data, by default uses all processors
    pool = Pool()
    pool.map(find_template_in_data, datafiles)
    pool.close()
    
    print('process finished at', datetime.now()-start)
    print('detection tables and similiarity scores can be found at',  '/media/sda/data/borehole/detections/')
    