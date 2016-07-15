'''
Plotting routines...

'''

import sys
import numpy as np
import matplotlib.pyplot as plt
#from Vehicle import Vehicle




def contour(vehicles, dtype='v', dflt=0, title=None):
    '''
    Create a contour plot.
    
    vehicles - array of Vehicle objects
    dtype - type of data to be plotted:
        'v' - speed
        'a' - aceleration
        'h' - headway
        'd' - distance headway
    dflt - default value forcontour parts where data are not available
    title - (optional) title for the figure
    '''
    
    xlabel = 'Time (seconds)'
    ylabel = 'Position (meters)'
    
    sz = len(vehicles)
    
    x_min = int(np.round(vehicles[sz-1].get_history(dtype='x')[0]))
    x_max = int(np.round(vehicles[0].get_history(dtype='x')[-1]))
    xx = np.array(range(x_min, x_max, 5))
    tt = np.array(vehicles[0].get_history(dtype='t'))
    m, n = len(xx), len(tt)
    
    zz = dflt*np.ones((m, n))
    
    
    for i in range(0, m):
        x = xx[i]
        for j in range(0, n-1):
            veh = vehicles[sz-1]
            #print(n, len(veh.get_history(dtype='x')), j)
            if (veh.get_history(dtype='x')[j] - veh.l) > x:
                continue
            if vehicles[0].get_history(dtype='x')[j] < x:
                continue
            k = sz - 1
            while (vehicles[k].get_history(dtype='x')[j] < x):
                k -= 1
                if k == 0:
                    break;
            
            zz[i][j] = vehicles[k].get_history(dtype=dtype)[j]
    
    
    #plt.pcolor(tt, xx, zz, cmap='gray')
    plt.pcolor(tt, xx, zz)
    plt.colorbar()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if title != None:
        plt.title(title)
    plt.axis([tt[0], tt[-1], x_min, x_max])
    plt.show()
    
    
    return
    
    











#==============================================================================
# Main function.
#==============================================================================
def main(argv):
    print(__doc__)

    



if __name__ == "__main__":
    main(sys.argv)