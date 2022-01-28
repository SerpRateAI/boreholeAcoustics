"""
this file plots data for every day from teh raw seismic waveforms
"""
import obspy
from multiprocessing import Pool
from datetime import datetime
import sys
from hydrophone_data_processing import load, preprocessing


starttime = datetime.now()

args = sys.argv
# print(args)
hole = str(args[1]).upper()
# print(hole)

# sys.exit()

def do(paths):
    stream = load.get_raw_stream(paths)
    streamday = str(stream[0].stats.starttime).split('T')[0]
    print('loaded data for day:', streamday)
    if hole == 'A':
        outfile = '/media/sda/data/robdata/rawplots/A/{}.png'.format(streamday)
    elif hole == 'B':
        outfile = '/media/sda/data/robdata/rawplots/B/{}.png'.format(streamday)
        stream = preprocessing.correct_hydrophone_B_wiring_problem(stream)
    else:
        raise ValueError('whatever you put in was not a hole designation')
        
    stream = preprocessing.convert_stream_to_pascals(stream)
    
    stream.plot(outfile=outfile)
    del stream
    print('plotted data for day:', streamday)
    print('elapsed time:', str(datetime.now()-starttime))
    
if __name__=='__main__':
    
    print('process started:', str(starttime))
    
    filelocs = load.create_datafiles()
    print('filelocs created:',str(datetime.now()-starttime))
    
    pool = Pool(15)
    pool.map(do, filelocs)
    pool.close()