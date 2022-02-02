"""
This module has functions that apply preprocessing to data
collected from oman drilling project site BA1
"""

import obspy
import io
import pandas as pd
import glob
import numpy as np
from hydrophone_data_processing import load

def correct_hydrophone_B_wiring_problem(stream):
    """
    Hole B has a reversed wiring issue where hydrophone 4 (index 3)
    has the wires installed backwards which flips the signal. THis
    function corrects that.
    """
    stream[3].data = -1 * stream[3].data
    return stream

def convert_trace_to_pascals(trace):
    """
    converts hydrophone data to pascals
    % convert digital counts to Pa
    % Q330S+ has 419430 counts/volt
    % hydrophone sensitivity is -165 dB, re: 1V/uPa
    % or p in uPa = V/10^-16.5
    """
    trace.data = trace.data/419430 # converts to volts
    trace.data = trace.data/(10**(-165/20.)) # converts to microPascals
    trace.data = trace.data/1e6 # converts to pascals
    # return trace
    return trace.data

def convert_stream_to_pascals(stream):
    """
    wrapper function to convert an entire stream to pascals
    """
    for n, tr in enumerate(stream):
        # print(type(tr))
        stream[n].data = convert_trace_to_pascals(tr)
        
    return stream

# def convert_stream_to_pascals(stream):
#     """
#     converts hydrophone data to pascals
#     % convert digital counts to Pa
#     % Q330S+ has 419430 counts/volt
#     % hydrophone sensitivity is -165 dB, re: 1V/uPa
#     % or p in uPa = V/10^-16.5
#     """
#     for n, tr in enumerate(stream):
#         stream[n].data = tr.data/419430. # converts to volts
#         stream[n].data = tr.data/(10**(-165/20.)) # converts to microPascals
#         stream[n].data = tr.data/1e6 # converts to Pascals
        
#     return stream

def square_stream(stream):
    """
    Returns the square of the traces contained in the stream
    """
    for s in stream:
        s.data = s.data**2
        
        
def abs_stream(stream):
    for s in stream:
        s.data = np.abs(s.data)
        
def calculate_quiet_noise():
    """
    This function returns the standard deviations ordered by station that can be used to calculate the amount of noise contributed by the station
    
    It uses data from year 2019 day 285 which was identified via spectrogram as a "very quiet day". The data uses a quiet period of 2 hours between 19h and 21h
    
    all units are in Pascals
    """
    day285 = load.import_corrected_data_for_single_day(julian_day=285, year=2019, borehole='b')
    quiet_time = day285.slice(starttime=obspy.UTCDateTime('2019-10-12T19:00:00')
               ,endtime=obspy.UTCDateTime('2019-10-12T21:00:00'))
    # the data is demeaned because there is an offset from zero
    quiet_time.decimate(factor=10)
    quiet_time.detrend('demean')
    quiet_time.filter(type='bandpass', freqmin=5, freqmax=10, zerophase=True)
    square_stream(quiet_time)
    quiet_time.filter(type='lowpass', freq=0.1)
    
    del day285
    return quiet_time.std()
        
if __name__=='__main__':
    print('Nothing to see here. We may go about our business.')
