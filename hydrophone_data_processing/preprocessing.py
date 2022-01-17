"""
This module has functions that apply preprocessing to data
collected from oman drilling project site BA1
"""

import obspy
import io
import pandas as pd
import glob
import numpy as np

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

def square_stream(stream):
    """
    Returns the square of the traces contained in the stream
    """
    for s in stream:
        s.data = s.data**2
        
if __name__=='__main__':
    print('Nothing to see here. We may go about our business.')