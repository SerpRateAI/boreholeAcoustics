"""
This module has functions to import data from the
borehole hydrophones
"""
import os
import sys
sys.path.append(os.getcwd())

import obspy
import io
import pandas as pd
import glob
import numpy as np
# from hydrophone_data_processing import preprocessing
import preprocessing

def create_datafiles():
    """
    creates a list of lists of datafiles, there are 6 files
    per day for each of 6 hydrophones
    """
    datafiles = []
    years_days = [d.split('.')[-2:] for d in glob.glob('/media/sda/data/robdata/Hydrophones/DAYS/B00/*')]
    years_days = np.array([list(x) for x in set(tuple(x) for x in years_days)])
    
    for y, d in years_days:
        day_dirs = []
        for s in [1,2,3,4,5,6]:
            dir = '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.0{s}.GDH.{y}.{d}'.format(s=s, y=y, d=d)
            day_dirs.append(dir)
        datafiles.append(day_dirs)  
    return datafiles

def get_stream_subsample_between_dates(path, startdate, enddate):
    """
    Produces a subsample of a large stream mseed file bounded
    by start and end dates.
    
    Assumes that only one trace exists in the stream file.
    
    This solution is based on this discussion:
    https://discourse.obspy.org/t/large-miniseed-files-read-in-chunks/1109
    
    Parameters:
    path (str): path to mseed file
    startdate (UTC): startdate of return data
    enddate (UTC): enddate of return data
    
    Returns:
    st (obspy.Stream): stream of subselected data
    """
    
    reclen = 512
    chunksize = 100000 * reclen
    with io.open(path, 'rb') as fh:
        i = 0
        while True:
            with io.BytesIO() as buf:
                c = fh.read(chunksize)
                buf.write(c)
                buf.seek(0, 0)
                
                if 'st' not in locals():
                    st = obspy.read(buf)
                    
                    # delete the stream and move on if its trace is not 
                    # before the starttime
                    if st.traces[0].stats.starttime < startdate:
                        del st

                else:
                    st_new = obspy.read(buf)
                    
                    # if the stream traces start after the enddate
                    # delete stop the loop
                    if st_new.traces[0].stats.starttime > enddate:
                        break
                    else:
                        st = st + st_new
    return st

def import_detections(filedir):
    """
    Builds a pandas dataframe out of the files found in the 
    directory provided to the function.
    
    Detections are built from the cross correlation template
    matching function. See template_match_B00.py for example
    
    Returns:
    df : pandas.DataFrame
    """
    import glob
    filepaths = glob.glob(filedir)
    df = pd.DataFrame()
    for f in filepaths:
        # TODO : you can rewrite this as if statement to check
        #        if there is a dataframe with zero rows. 
        #        probably will be less computationally intense
        #        if that ever becomes an issue. Also, it would
        #        be much more explicit in what is happening
        try:
            df = pd.concat([df, pd.read_csv(f)])
        except:
            # this exception handles the case when there is no
            # data in the read in dataframe due to no
            # detections being made
            pass
        
    return df

def get_raw_stream(paths):
    """
    returns raw data with no conversions
    """
    stream = obspy.read(paths[0])
    for p in paths[1:]:
        stream = stream + obspy.read(p)
    stream.merge(fill_value='latest')
    return stream

def import_corrected_data_for_single_day(julian_day, year, borehole='B'):
    """
    Imports data for all 6 hydrophones for specific day
    """
    if borehole.upper() not in ['A', 'B']:
        raise ValueError('borehole should be A or B')
    
    file_locs = []
    for s in [1, 2, 3, 4, 5, 6]:
        dir = '/media/sda/data/robdata/Hydrophones/DAYS/B00/B00.7F.0{s}.GDH.{y}.{d}'.format(s=s, y=year, d=julian_day)
        file_locs.append(dir)
    
    # return get_stream(file_locs)
    stream = get_raw_stream(file_locs)
    stream = preprocessing.correct_hydrophone_B_wiring_problem(stream)
    stream = preprocessing.convert_stream_to_pascals(stream)
    return stream

def read_csvs_convert_to_dataframe(csv_paths):
    """
    reads a list of csv file locations and returns them
    as a pandas dataframe
    """
    df = pd.DataFrame()
    for f in csv_paths:
        try:
            df = pd.concat([df, pd.read_csv(f)])
        except:
            pass
        
    return df

if __name__=='__main__':
    print('Nothing to see here. You may go about our business.')