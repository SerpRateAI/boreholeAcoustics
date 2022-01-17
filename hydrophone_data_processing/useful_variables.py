"""
This module has random useful variables that dont need to be
recalcuated and generating bugs and stuff
"""
import itertools

def get_hydrophone_pairs():
    hydrophones = [0, 1, 2, 3, 4, 5]
    hydrophone_pairs = [h for h in itertools.combinations(hydrophones, 2)]
    return hydrophone_pairs

if __name__=='__main__':
    print('Nothing to see here. You may go about our business.')