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
    stream.detrend('demean')
    stream.normalize()
    stream[0].data = filter.highpass(stream[0].data, freq=40, df=1000)
    stream[0].data = filter.lowpass(stream[0].data, freq=5, df=1000)
    return stream

def make_template():
    template_dir = '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.138'
    template = digest_data(template_dir)
    pick = UTC('2019-05-18T11:57:41.532000Z')
    template = template.trim(pick-0.025, pick+0.25)
    return template

def make_template_1():
    template_dir = '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.274'
    template = digest_data(template_dir)
    pick1 = UTC('2019-10-01T12:32:11.92Z')
    pick2 = UTC('2019-10-01T12:32:12.13Z')
    template = template.trim(pick1, pick2)
    return template

def make_template_02():
    template_dir = '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.02.GDH.2019.138'
    template = digest_data(template_dir)
    pick = UTC('2019-05-18T11:57:41.532000Z')
    template = template.trim(pick-0.015, pick+0.25)
    return template

def make_template_1_02():
    template_dir = '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.02.GDH.2019.274'
    template = digest_data(template_dir)
    pick1 = UTC('2019-10-01T12:32:11.95Z')
    pick2 = UTC('2019-10-01T12:32:12.13Z')
    template = template.trim(pick1, pick2)
    return template

# def find_template_in_data(datadir):
# def find_template_in_data(datadir, phone):
def find_template_in_data(datadir, templates, phone):
    day = datadir.split('.')[-1]
    print('finding template for day', day)
    data = digest_data(datadir)
#     height = 0.875
    height = [0.875, 0.925]
    distance = 3
#     template = make_template()
#     template2 = make_template_1()
#     templates = [template, template2]
    detections, sims = correlation_detector(stream=data
                                        , templates=templates
                                        , heights=height
                                        , distance=distance
                                        , plot=None)
    data_writing_location = '/media/sda/data/borehole/detections/' + phone + day
    try:
        sims[0].write(data_writing_location + phone + '_similarity.mseed', format='MSEED')
    except AttributeError:
        # TODO : what is this error handling? Is it because it finds nothing and so
        #        there is nothing to write?
        print('there is an error writing similarity for day', str(day))
    df = pd.DataFrame(detections)
    df.to_csv(data_writing_location + phone + '_detections.csv', index=False)
    del detections, sims, df, data

if __name__=='__main__':
    start = datetime.now()
    print('process started at', str(start))
    
    # get data file locations for importing
    datafiles2019_01 = glob.glob('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.*')
    datafiles2020_01 = glob.glob('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2020.*')
    datafiles_01 = datafiles2019_01 + datafiles2020_01
    
    datafiles2019_02 = glob.glob('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.02.GDH.2019.*')
    datafiles2020_02 = glob.glob('/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.02.GDH.2020.*')
    datafiles_02 = datafiles2019_02 + datafiles2020_02    
    # create template
#     template = make_template()
    templates_01 = [make_template(), make_template_1()]
    templates_02 = [make_template_02(), make_template_1_02()]
    
    def find_temp_01(datafiles):
        return find_template_in_data(datafiles, templates=templates_01, phone='01')
    
    def find_temp_02(datafiles):
        return find_template_in_data(datafiles, templates=templates_02, phone='02')
    
    # create a processor pool to ingest the data, by default uses all processors
    pool = Pool()
#     pool.map(find_template_in_data, datafiles_01)
    pool.map(find_temp_01, datafiles_01)
    pool.map(find_temp_02, datafiles_02)
    pool.close()
    
    print('process finished at', datetime.now()-start)
    print('detection tables and similiarity scores can be found at',  '/media/sda/data/borehole/detections/')
    