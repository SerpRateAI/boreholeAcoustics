import obspy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates


from hydrophone_data_processing import load, preprocessing, tempmatch

import matplotlib.ticker as ticker

class PrecisionDateFormatter(ticker.Formatter):
    """
    Extend the `matplotlib.ticker.Formatter` class to allow for millisecond
    precision when formatting a tick (in days since the epoch) with a
    `~datetime.datetime.strftime` format string.

    """

    def __init__(self, fmt, precision=3, tz=None):
        """
        Parameters
        ----------
        fmt : str
            `~datetime.datetime.strftime` format string.
        """
        from matplotlib.dates import num2date
        if tz is None:
            from matplotlib.dates import _get_rc_timezone
            tz = _get_rc_timezone()
        self.num2date = num2date
        self.fmt = fmt
        self.tz = tz
        self.precision = precision

    def __call__(self, x, pos=0):
        if x == 0:
            raise ValueError("DateFormatter found a value of x=0, which is "
                             "an illegal date; this usually occurs because "
                             "you have not informed the axis that it is "
                             "plotting dates, e.g., with ax.xaxis_date()")

        dt = self.num2date(x, self.tz)
        ms = dt.strftime("%f")[:self.precision]

        return dt.strftime(self.fmt).format(ms=ms)

    def set_tzinfo(self, tz):
        self.tz = tz
        

def make_detection_plot(detections, timewindow, stream):
    
    # make detection lines
    dets = detections[detections.time.between(timewindow[0], timewindow[1])].copy()
    x = data.time
    y = np.ones_like(x)*500
    
    h1 = stream[0].slice(starttime=obspy.UTCDateTime(timewindow[0])
                         ,endtime=obspy.UTCDateTime(timewindow[1])
                        )
    
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(x, y, color='limegreen')
    ax.plot(h1.times('matplotlib'), h1.data)
    fig.savefig('detections_check/{}.pdf', bbox_inches='tight')
    plt.close()
    del det, x, y, h1, fig, ax
    
def do_for_one_day(paths):
    stream = load.import_corrected_data_for_single_day(paths=paths)
    startdate = str(stream[0].stats.starttime).split('T')[0]
    
        
if __name__=='__main__':
    detectfiles = '/media/sda/data/borehole/detections/*.csv'
    det = load.import_detections(detectfiles)
    
    streamlocs = load.create_datafiles(hole='b')
    
    