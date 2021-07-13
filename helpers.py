
import obspy
import io

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