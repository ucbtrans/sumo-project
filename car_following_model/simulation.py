'''
Simulation...

'''

import sys
import numpy as np
import matplotlib.pyplot as plt
from Vehicle import Vehicle
import plot_routines as pr
import pickle


def initialize():
    '''
    Returns array of vehicles; simulation step length in seconds.
    '''
    
    dt = 0.05 # seconds
    total_time = 60 # seconds
    total_vehicles = 50
    
    l = 5 # meters
    v_init = 0
    v_max = 20 # m/s
    v_max_lead = 20
    
    a = 1.5 # acceleration in m/s^2
    b = 2 # deceleration in m/s^2
    
    g_min = 4 # meters
    acc_g_min = 3 # meters
    platoon_g_min = 2 # meters
    
    stop_location = 8300 # meters
    
    tau = 2.05 # seconds
    acc_tau = 1.1 # seconds
    platoon_tau = 0.75 # seconds
    
    acc_penetration = 0
    enable_platoons = False
    
    #model = 'krauss' # Krauss
    #model = 'idm' # IDM
    model = 'iidm' # Improved IDM
    #model = 'gipps' # Gipps
    #model = 'helly' # Helly
    #model = 'platoon' # Platoon
    
    vehicles = []
    is_acc = False
    global acc_veh
    acc_veh = [True, False, True, False, False, True, False, False, True, True, False, False, False, False, False, False, False, True, True, True, False, False, True, True, False, True, False, False, False, True, True, False, True, True, False, False, True, True, False, True, True, True, True, True, True, False, True, True, False, False, False, False, True, False, False, False, True, True, False, False]
    
    for i in range(0, total_vehicles):
        my_g_min = g_min
        my_tau = tau
        my_model = model
        
        #if acc_veh[i]:        
        if np.random.rand() <= acc_penetration:
            #acc_veh.append(True)
            my_g_min = acc_g_min
            my_tau = acc_tau
            if is_acc:
                if enable_platoons:
                    my_model = 'platoon'
                    my_g_min = platoon_g_min
                    my_tau = platoon_tau
            else:
                is_acc = True
        else:
            #acc_veh.append(False)
            is_acc = False
            
        
        if i == 0:
            pos = 0
        else:
            pos -= (l + my_g_min)
            
        if i == 0:
            veh = Vehicle(i+1, pos, l=l, v=v_init, a=a, b=b, v_max=v_max_lead, g_min=my_g_min, tau=my_tau, stop_x=stop_location, model=my_model)
        else:
            veh = Vehicle(i+1, pos, l=l, v=v_init, a=a, b=b, v_max=v_max, g_min=my_g_min, tau=my_tau, stop_x=stop_location, model=my_model)
        
        vehicles.append(veh)
    
    return vehicles, dt, total_time





def simulation_step(vehicles, dt):
    '''
    Advance one simulation step.
    
    vehicles - array of vehicles
    dt - length of simulation step in seconds
    '''
    
    sz = len(vehicles)
    
    for i in range(1, sz+1):
        if i == sz:
            vehicles[-i].step(1000000, vehicles[-i].get_max_speed(), dt=dt)
        else:
            vehicles[-i].step(vehicles[-i-1].get_position(), vehicles[-i-1].get_speed(), dt)
                    
    return





def run_simulation(vehicles, dt, total_time):
    '''
    Run simulation.
    
    vehicles - array of vehicles
    dt - length of simulation step in seconds
    total_time - time limit of the simulation
    '''
    
    sz = len(vehicles)
    sensor_loc = 0.1
    
    step = 0
    i = 0
    t_prev = 0
    position = []
    dx = []
    dv = []
    flow = []
    flow1 = []
    speed = []
    safe_speed = []
    leader_speed = []
    accel = []
    max_speed = []
    time = []
    time2 = []
    ss_throughput = []
    
    while step*dt < total_time:
        step += 1

        if i == 0 and i < sz and vehicles[i].get_position() >= sensor_loc and vehicles[i+1].get_speed() > 0:
            theta0 = vehicles[i+1].tau + float(vehicles[i+1].g_min+vehicles[i+1].l)/vehicles[i].get_max_speed()
            theta = vehicles[i+1].get_headway()
            dx.append(vehicles[i+1].get_distance_headway())
            dv.append(vehicles[i].get_speed() - vehicles[i+1].get_speed())
            position.append(vehicles[i].get_position())            
            max_speed.append(vehicles[i].get_max_speed())            
            speed.append(vehicles[i].get_speed())
            accel.append(vehicles[i].get_acceleration())            
            time.append(step*dt)
            ss_throughput.append(3600/theta0)
            flow.append(3600/theta)
            i += 1
            
        if i > 0 and i < sz-1 and vehicles[i].get_position() >= sensor_loc:
            theta0 = vehicles[i+1].tau + float(vehicles[i].g_min+vehicles[i+1].l)/vehicles[i+1].get_max_speed()
            theta = vehicles[i+1].get_headway()
            theta1 = step*dt - t_prev
            t_prev = step*dt
            position.append(vehicles[i].get_position())
            dx.append(vehicles[i+1].get_distance_headway())
            dv.append(vehicles[i].get_speed() - vehicles[i+1].get_speed())
            max_speed.append(vehicles[i].get_max_speed())            
            speed.append(vehicles[i].get_speed())
            safe_speed.append(vehicles[i].get_safe_speed(vehicles[i-1].get_position(), vehicles[i-1].get_speed()))
            leader_speed.append(vehicles[i-1].get_speed())
            accel.append(vehicles[i].get_acceleration())
            time.append(step*dt)
            time2.append(step*dt)
            ss_throughput.append(3600/theta0)
            flow.append(3600/theta)
            flow1.append(3600/theta1)
            i += 1
            
        simulation_step(vehicles, dt)
    
    if True:
        with open('a_15.pickle', 'wb') as f:
            pickle.dump(time, f)
            pickle.dump(time2, f)
            pickle.dump(dx, f)
            pickle.dump(dv, f)
            pickle.dump(speed, f)
            pickle.dump(accel, f)
            pickle.dump(flow1, f)
    

    if False:
        plt.figure()
        plt.plot(time, position)
        plt.plot(time, position, 'o')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Position (meters)')
        #plt.show()
    
    plt.figure()
    plt.plot(time, dx)
    plt.plot(time, dx, 'o')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Distance to Leader (meters)')
    #plt.show()
    
    plt.figure()
    plt.plot(time, max_speed, 'r')
    plt.plot(time, speed)
    plt.plot(time, speed, 'o')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Speed (m/s)')
    #plt.show()
        
    if False:
        plt.figure()
        plt.plot(time, max_speed, 'r')
        plt.plot(time2, safe_speed)
        plt.plot(time2, safe_speed, 'o')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Safe Speed (m/s)')
        #plt.show()
    
    if False:
        plt.figure()
        plt.plot(time, max_speed, 'r')
        plt.plot(time2, leader_speed)
        plt.plot(time2, leader_speed, 'o')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Leader Speed (m/s)')
        #plt.show()
    
    plt.figure()
    plt.plot(time, accel)
    plt.plot(time, accel, 'o')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Acceleration (m/s^2)')
    #plt.show()
    
    plt.figure()
    plt.plot(time, dv)
    plt.plot(time, dv, 'o')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Speed Difference (m/s)')
    #plt.show()
    
    plt.figure()
    plt.plot(time, ss_throughput, 'r')
    plt.plot(time2, flow1, 'k')
    plt.plot(time2, flow1, 'o')
    #plt.plot(time, flow)
    #plt.plot(time, flow, 'o')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Flow (vph)')
    plt.show()
    
    if False:
        return
        
    i = 0
    total = 10
    vehicles_to_plot = range(i, i+total)
    #vehicles_to_plot = [0, 5, 10, 15, 20, 25]
    
    plt.figure()
    plt.plot([vehicles[i].time[0], vehicles[i].time[-1]], [sensor_loc, sensor_loc], 'k')
    for j in vehicles_to_plot:
        plt.plot(vehicles[j].time, vehicles[j].trajectory)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Position (meters)')
    
    plt.figure()
    plt.plot([vehicles[i].time[0], vehicles[i].time[-1]], [vehicles[i].get_max_speed(), vehicles[i].get_max_speed()], 'r')
    for j in vehicles_to_plot:
        plt.plot(vehicles[j].time, vehicles[j].speed)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Speed (m/s)')
    
    plt.figure()
    for j in vehicles_to_plot:
        plt.plot(vehicles[j].time, vehicles[j].acceleration)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Acceleration (m/s^2)')
    plt.show()
    
    if True:
        plt.figure()
        for j in vehicles_to_plot:
            plt.plot(vehicles[j].time, vehicles[j].distance_headway)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Distance Headway (meters)')
        plt.show()
    
    #if False:
        plt.figure()
        for j in vehicles_to_plot:
            plt.plot(vehicles[j].time, vehicles[j].headway)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Headway (seconds)')
        plt.show()
    
    if True:
        pr.contour(vehicles, dtype='v', dflt=0, title='Speed (m/s)')
        pr.contour(vehicles, dtype='a', dflt=0, title='Acceleration (m/s^2)')
        pr.contour(vehicles, dtype='h', dflt=0, title='Headway (seconds)')
        pr.contour(vehicles, dtype='d', dflt=0, title='Distance Headway (meters)')
        pr.contour(vehicles, dtype='f', dflt=0, title='Flow (vph)')
    
    print("Count =", len(flow), "Theta_0 =", theta0, "Theta =", theta)

    











#==============================================================================
# Main function.
#==============================================================================
def main(argv):
    print(__doc__)
    
    vehicles, dt, total_time = initialize()
    run_simulation(vehicles, dt, total_time)
    



if __name__ == "__main__":
    main(sys.argv)

