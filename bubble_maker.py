"""
This module generates the bubble catalogs for the boreholes
"""
from hydrophone_data_processing import load, preprocessing, useful_variables, tempmatch
import obspy
from obspy.signal.cross_correlation import correlation_detector
import pandas as pd
import numpy as np
import sys
# from datetime import datetime
from multiprocessing import Pool

# start = datetime.now()

args = sys.argv
system = args[0]
hole = load.control_for_bad_hole_labels(args[1])
temp = tempmatch.make_template(hole=hole)
# print('template created for hole {}, elapsed time:'.format(hole), datetime.now()-start)
print('template created for hole {}, elapsed time:'.format(hole), useful_variables.elapsed_time())


def find_bubbles_in_single_day(paths):
    """
    Wrapper function to create a single day worth of bubble
    detections
    """
    # set correlation parameters based on what hole you are
    # detecting in
    if hole == 'A':
        height = 0.8
        distance = 1.1
    elif hole == 'B':
        height = 0.8
        distance = 1.1
    
    year, day = paths[0].split('.')[-2:]
    stream = load.import_corrected_data_for_single_day(paths)
    stream = tempmatch.digest_data(stream)
    detections, sims = correlation_detector(
                                      stream=stream
                                    , templates=temp
                                    , heights=height
                                    , distance=distance
                                    , plot=None
                                           )
    data_writing_location = '/media/sda/data/borehole/detections/'+hole+day
    df = pd.DataFrame(detections)
    print('detected {n} events on day {y}.{d}'.format(n=df.shape[0], d=day, y=year))
    # print('elapsed time:', datetime.now()-start)
    print('elapsed time:',useful_variables.elapsed_time())
    df.to_csv(data_writing_location + '.csv', index=False)
    del detections, sims, df, stream   

if __name__=='__main__':
    
    print('catalog creation process started for hole {}:'.format(hole), useful_variables.start)

    # TODO: cross correlation per day for template to identify templates
    datafiles = load.create_datafiles(hole=hole)
    pool = Pool(10)
    pool.map(find_bubbles_in_single_day, datafiles)
    pool.close()

    # TODO: calculate FFT to get max freq
    
    # TODO: calculate radius from Minneart relationship
    
    # TODO: calculate volume
    
    # TODO: calculate mass
    
    print('catalog generation for hole {} has completed. elapsed time:'.format(hole), useful_variables.elapsed_time())