"""
SUMO route analysis routines.

"""


import sys
import numpy as np
import matplotlib.pyplot as plt
import pickle


def get_q_data(q_file, lnk):
    '''
    
    '''
    
    ql = []
    cnt = 0
    thres = 37
    
    with open(q_file, "r") as qf:
        for line in qf:
            if line.find("<lane id=\"" + lnk) < 0:
                continue
            
            cnt += 1
            if cnt > 3600:
                break
            
            offset = 0
            if cnt > 121:
                offset = 15 * np.random.rand() + 4
            
            q = float(line.split('"')[5])
            q = int(np.round(q / 3.0) + offset)
            q = np.min([q, thres])
            ql.append(q)
            
        qf.close()
        
    return ql






#==============================================================================
# Main function - for standalone execution.
#==============================================================================

def main(argv):
    #print(__doc__)
    
    q_file = "network/queues.xml"
    lnk = "116069075#1.338_2"
    
    ql = get_q_data(q_file, lnk)
    print(np.max(np.array(ql)))
    plt.plot(ql)
    plt.show()
    
    return



if __name__ == "__main__":
    main(sys.argv)

