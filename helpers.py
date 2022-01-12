
import obspy
import io
import pandas as pd
import glob
import numpy as np

def create_datafiles():
    """
    creates a list of lists of datafiles, there are 6 files per day for each of 6 hydrophones
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

def correct_hydrophone_B_wiring_problem(stream):
    """
    Hole B has a reversed wiring issue where hydrophone 4 (index 3)
    has the wires installed backwards which flips the signal. THis
    function corrects that.
    """
    stream[3].data = -1 * stream[3].data
    return stream

def convert_stream_to_pascals(stream):
    """
    converts hydrophone data to pascals
    % convert digital counts to Pa
    % Q330S+ has 419430 counts/volt
    % hydrophone sensitivity is -165 dB, re: 1V/uPa
    % or p in uPa = V/10^-16.5
    """
    for n, tr in enumerate(stream):
        stream[n].data = tr.data/419430. # converts to volts
        stream[n].data = tr.data/(10**(-165/20.)) # converts to microPascals
        stream[n].data = tr.data/1e6 # converts to Pascals
        
    return stream
    

#     p=data/419430; % now in volts
#     p=p/10^(-165/20); % now in uPa
#     p=p/1e06; % now in Pa
    # for n, tr in enumerate(stream):
    #     stream[n].data = tr.data/419430.0 # converts to volts
    #     stream[n].data = tr.data**(-165/20) # converts to microPascal
    #     stream[n].data = tr.data/1e6 # now in pascals
    # return stream

def import_raw_data_for_single_day(julian_day, year, borehole='B'):
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
    stream = correct_hydrophone_B_wiring_problem(stream)
    stream = convert_stream_to_pascals(stream)
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