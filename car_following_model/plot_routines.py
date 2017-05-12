'''
Plotting routines...

'''

import sys
import numpy as np
import matplotlib.pyplot as plt




def contour(vehicles, dtype='v', dflt=0, title=None):
    '''
    Create a contour plot.
    
    vehicles - array of Vehicle objects
    dtype - type of data to be plotted:
        'v' - speed
        'a' - aceleration
        'h' - headway
        'd' - distance headway
        'f' - flow
    dflt - default value forcontour parts where data are not available
    title - (optional) title for the figure
    '''
    
    xlabel = 'Time (seconds)'
    ylabel = 'Position (meters)'
    
    sz = len(vehicles)
    
    x_min = int(np.round(vehicles[sz-1].get_history(dtype='x')[0]))
    x_max = int(np.round(vehicles[0].get_history(dtype='x')[-1]))
    #x_max = 1049
    #print(x_min, x_max)
    xx = np.array(range(x_min, x_max, 5))
    tt = np.array(vehicles[0].get_history(dtype='t'))
    m, n = len(xx), len(tt)
    
    zz = dflt*np.ones((m, n))
    
    
    for i in range(0, m):
        x = xx[i]
        for j in range(0, n-1):
            veh = vehicles[sz-1]
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
    
    plt.pcolor(tt, xx, zz, cmap='jet')
    #plt.contourf(tt, xx, zz, cmap='jet')
    plt.colorbar()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if title != None:
        plt.title(title)
    plt.axis([tt[0], tt[-1], x_min, x_max])
    plt.show()
    
    
    return





def contour2(links, dtype='v', dflt=0, title=None, vmin=None, vmax=None):
    '''
    Create a contour plot.
    
    links - array of Link objects
    dtype - type of data to be plotted:
        'v' - speed
        'a' - aceleration
        'f' - flow
        'd' - density
    dflt - default value forcontour parts where data are not available
    title - (optional) title for the figure
    '''
    
    xlabel = 'Time (seconds)'
    ylabel = 'Position (meters)'
    
    sz = len(links)
    offset = 50
    
    dx = links[0].dx
    
    x_min = -offset*dx
    x_max = (sz - offset) * dx
    xx = np.array(range(x_min, x_max, dx))
    tt = np.array(links[0].get_history(dtype='t'))
    m, n = len(xx), len(tt)
    
    zz = dflt*np.ones((m, n))
    
    
    for i in range(0, m):
        k = i
        if i == 0:
            k = 1
        for j in range(0, n-1):
            if links[k].get_history(dtype='d')[j] > 0 or dtype=='d' or dtype=='f':
                zz[i][j] = links[k].get_history(dtype=dtype)[j]
            
    if vmin == None:
        vmin = np.min(np.min(zz))
    
    if vmax == None:
        vmax = np.max(np.max(zz))
    
    print(np.max(np.max(zz)))
    plt.figure()
    plt.pcolor(tt, xx, zz, cmap='jet', vmin=vmin, vmax=vmax)
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