'''
Macro-simulation...

'''

import sys
import numpy as np
import matplotlib.pyplot as plt
from Link import Link
import plot_routines as pr
import pickle


def initialize():
    '''
    Returns array of links, simulation step length in seconds and total simulation time.
    '''
    
    dt = 0.05 # seconds
    total_time = 60 # seconds
    total_links = 200
    dx = 5 # link length in meters
    l = 5 # car length in meters
    g_min = 4 # meters
    v_max = 20 # m/s
    a_max = 1.5 # acceleration in m/s^2
    b_max = 2 # deceleration in m/s^2
    
    stop_location = 100 # link number
    
    tau = 2.05 # seconds
    
    links = []
    
    for i in range(total_links):
        rho = 0
        if i < 50:
            rho = float(1.0/(g_min + l))
        
        v = 0
        if i > 49:
            v = 0
        
        is_stop = False
        if stop_location == i:
            is_stop = True
        link = Link(i, dx, l, g_min, v_max=v_max, rho_init=rho, v_init=v, a_max=a_max, b_max=b_max, tau=tau, is_stop=is_stop)        
        
        links.append(link)
    
    for i in range(total_links):
        if i == 0:
            ulink = None
        else:
            ulink = links[i-1]
        if i == total_links - 1:
            dlink = None
        else:
            dlink = links[i+1]
        
        links[i].update_acceleration(dt, ulink, dlink)
    
    return links, dt, total_time





def simulation_step(links, dt):
    '''
    Advance one simulation step.
    
    links - array of links
    dt - length of simulation step in seconds
    '''
    
    sz = len(links)
    
    for i in range(sz):
        if i == 0:
            ulink = None
        else:
            ulink = links[i-1]
        if i == sz - 1:
            dlink = None
        else:
            dlink = links[i+1]
        
        links[i].update_state(dt, ulink, dlink)
            
    for i in range(sz):
        if i == 0:
            ulink = None
        else:
            ulink = links[i-1]
        if i == sz - 1:
            dlink = None
        else:
            dlink = links[i+1]
        
        links[i].update_acceleration(dt, ulink, dlink)

    return





def run_simulation(links, dt, total_time):
    '''
    Run simulation.
    
    links - array of links
    dt - length of simulation step in seconds
    total_time - time limit of the simulation
    '''
    
    sz = len(links)
    step = 0
    
    while step*dt < total_time:
        step += 1
        simulation_step(links, dt)
    

    i = 90
    
    plt.figure()
    plt.plot(links[i].time, links[i].acceleration, 'b')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Acceleration (m/s^2)")

    plt.figure()
    plt.plot(links[i].time, links[i].speed, 'b')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Speed (m/s)")
        
    plt.figure()
    plt.plot(links[i].time, links[i].density, 'b')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Density (vpm)")

    plt.figure()
    plt.plot(links[i].time, links[i].flow, 'b')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Flow (vph)")
    
    plt.show()
    
    
    if True:
        pr.contour2(links, dtype='a', dflt=0, title='Acceleration (m/s^2)')
        pr.contour2(links, dtype='v', dflt=0, title='Speed (m/s)')
        pr.contour2(links, dtype='g', dflt=0, title='Desired Gap (meters)')
        pr.contour2(links, dtype='d', dflt=0, title='Density (veh. per mile)')
        pr.contour2(links, dtype='f', dflt=0, title='Flow (veh. per hour)')

    return

    











#==============================================================================
# Main function.
#==============================================================================
def main(argv):
    print(__doc__)
    
    links, dt, total_time = initialize()
    run_simulation(links, dt, total_time)
    



if __name__ == "__main__":
    main(sys.argv)

