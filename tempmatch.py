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
    # stream = obspy.read(filedir[0])
    stream = obspy.read(filedir)
    # some traces have overlapping data, we remove this and fill it with most recent
    # data
    stream.merge(fill_value='latest')
    stream.detrend('demean')
    stream.normalize()
    stream.filter('highpass', freq=40)
    return stream

def make_template(templatedir, starttime, endtime):
    template = digest_data(templatedir)
    pick1 = UTC(starttime)
    pick2 = UTC(endtime)
    template = template.trim(pick1, pick2)
    return template

def similarity_component_thres(ccs, thres, num_components):
    """Return Trace with mean of ccs
    and set values to zero if number of components above threshold is not reached"""
    ccmatrix = np.array([tr.data for tr in ccs])
    header = dict(sampling_rate=ccs[0].stats.sampling_rate,
                  starttime=ccs[0].stats.starttime)
    comp_thres = np.sum(ccmatrix > thres, axis=0) >= num_components
    data = np.mean(ccmatrix, axis=0) * comp_thres
    
    if ccs[1].stats.starttime - ccs[0].stats.starttime < 0.1:
        return None
    else:
        return Trace(data=data, header=header)

def simf(ccs):
    return similarity_component_thres(ccs, 0.5, 6)


if __name__=='__main__':
    print('dont do this')