"""
This module has functions for template matching
"""

from hydrophone_data_processing import load
from obspy.signal.cross_correlation import correlation_detector
import obspy

def digest_data(stream):
    """
    custom digest_data for tempmatch
    """

    stream.merge(fill_value='latest')
    stream.detrend('demean')
    # stream.normalize()
    stream.filter('highpass', freq=40, corners=4, zerophase=True)
    return stream

def _make_template_A():
    paths = [
     '/media/sda/data/robdata/Hydrophones/DAYS/A00/A00.7F.01.GDH.2019.141'
    ,'/media/sda/data/robdata/Hydrophones/DAYS/A00/A00.7F.02.GDH.2019.141'
    ,'/media/sda/data/robdata/Hydrophones/DAYS/A00/A00.7F.03.GDH.2019.141'
    ,'/media/sda/data/robdata/Hydrophones/DAYS/A00/A00.7F.04.GDH.2019.141'
    ,'/media/sda/data/robdata/Hydrophones/DAYS/A00/A00.7F.05.GDH.2019.141'
    ,'/media/sda/data/robdata/Hydrophones/DAYS/A00/A00.7F.06.GDH.2019.141'
    ]
    stream = load.import_corrected_data_for_single_day(paths=paths)
    stream = digest_data(stream)
    
    templates = stream.select(id='7F.A00.03.GDH').slice(obspy.UTCDateTime('2019-05-21T07:04:18.85'), obspy.UTCDateTime('2019-05-21T07:04:19.025'))
    templates += stream.select(id='7F.A00.04.GDH').slice(obspy.UTCDateTime('2019-05-21T07:04:18.85'), obspy.UTCDateTime('2019-05-21T07:04:19.05'))
    templates += stream.select(id='7F.A00.05.GDH').slice(obspy.UTCDateTime('2019-05-21T07:04:18.93'), obspy.UTCDateTime('2019-05-21T07:04:19.00'))
    templates += stream.select(id='7F.A00.06.GDH').slice(obspy.UTCDateTime('2019-05-21T07:04:18.97'), obspy.UTCDateTime('2019-05-21T07:04:19.05'))
    
    del stream
    return templates

def _make_template_B(raw):
    paths = [
        '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.01.GDH.2019.138'
    ,'/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.02.GDH.2019.138'
    ,'/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.03.GDH.2019.138'
    ,'/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.04.GDH.2019.138'
    ,'/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.05.GDH.2019.138'
    ,'/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.06.GDH.2019.138'
    ]
    data = load.import_corrected_data_for_single_day(paths=paths)
    # data = digest_data(data)
    if raw == False:
        data = digest_data(data)
    
    templates = data.select(id='7F.B00.01.GDH').slice(obspy.UTCDateTime('2019-05-18T14:36:16.178Z'), obspy.UTCDateTime('2019-05-18T14:36:16.304Z'))
    templates += data.select(id='7F.B00.02.GDH').slice(obspy.UTCDateTime('2019-05-18T14:36:16.22Z'), obspy.UTCDateTime('2019-05-18T14:36:16.35Z'))
    templates += data.select(id='7F.B00.03.GDH').slice(obspy.UTCDateTime('2019-05-18T14:36:16.26Z'), obspy.UTCDateTime('2019-05-18T14:36:16.4Z'))
    templates += data.select(id='7F.B00.04.GDH').slice(obspy.UTCDateTime('2019-05-18T14:36:16.3Z'), obspy.UTCDateTime('2019-05-18T14:36:16.45Z'))
    templates += data.select(id='7F.B00.05.GDH').slice(obspy.UTCDateTime('2019-05-18T14:36:16.35Z'), obspy.UTCDateTime('2019-05-18T14:36:16.50Z'))
    templates += data.select(id='7F.B00.06.GDH').slice(obspy.UTCDateTime('2019-05-18T14:36:16.40Z'), obspy.UTCDateTime('2019-05-18T14:36:16.60Z'))
    
    del data
    return templates

# def make_template(hole):
def make_template(hole, raw=False):
    """
    wrapper function for making bubble template for hole A or B
    """
    if hole == 'A':
        # return _make_template_A()
        return _make_template_A(raw=raw)
    elif hole == 'B':
        # return _make_template_B()
        return _make_template_B(raw=raw)
    else:
        raise ValueError('These are not the holes you are looking for:', hole)
        

if __name__=='__main__':
    print('dont do this')