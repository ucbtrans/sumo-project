'''
Simulation...

'''

import sys
import matplotlib.pyplot as plt
from Vehicle import Vehicle


def initialize():
    '''
    Returns array of vehicles; simulation step length in seconds.
    '''
    
    a = 2.6 # m/s^2
    dt = 0.01 # seconds
    total_time = 60 # seconds
    total_vehicles = 50
    
    l = 5 # meters
    v_max = 20 # m/s
    b = 4.5 # m/s^2
    g_min = 4 # meters
    tau = 2.05 # seconds
    
    vehicles = []
    
    for i in range(0, total_vehicles):
        pos = -i * (l + g_min)
        veh = Vehicle(pos, l=l, a=a, b=b, v_max=v_max, g_min=g_min, tau=tau)
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
    
    step = 0
    i = 0
    t_prev = 0
    position = []
    dx = []
    dv = []
    flow = []
    flow1 = []
    speed = []
    max_speed = []
    time = []
    time2 = []
    ss_throughput = []
    
    while step*dt < total_time:
        step += 1

        if i == 0 and i < sz and vehicles[i].get_position() >= 0.1 and vehicles[i+1].get_speed() > 0:
            theta0 = vehicles[i+1].tau + float(vehicles[i+1].g_min+vehicles[i+1].l)/vehicles[i].get_max_speed()
            theta = vehicles[i+1].get_distance_headway()/vehicles[i+1].get_speed()
            #theta = vehicles[i+1].get_distance_headway()/vehicles[i+1].get_safe_speed(vehicles[i].get_position(), vehicles[i].get_speed())
            dx.append(vehicles[i+1].get_distance_headway())
            dv.append(vehicles[i].get_speed() - vehicles[i+1].get_speed())
            position.append(vehicles[i].get_position())            
            max_speed.append(vehicles[i].get_max_speed())            
            speed.append(vehicles[i].get_speed())            
            time.append(step*dt)
            ss_throughput.append(3600/theta0)
            flow.append(3600/theta)
            i += 1
            
        if i > 0 and i < sz-1 and vehicles[i].get_position() >= 0.1:
            theta0 = vehicles[i+1].tau + float(vehicles[i].g_min+vehicles[i+1].l)/vehicles[i+1].get_max_speed()
            theta = vehicles[i+1].get_distance_headway()/vehicles[i+1].get_speed()
            #theta = vehicles[i+1].get_distance_headway()/vehicles[i+1].get_safe_speed(vehicles[i].get_position(), vehicles[i].get_speed())
            theta1 = step*dt - t_prev
            t_prev = step*dt
            position.append(vehicles[i].get_position())
            dx.append(vehicles[i+1].get_distance_headway())
            dv.append(vehicles[i].get_speed() - vehicles[i+1].get_speed())
            max_speed.append(vehicles[i].get_max_speed())            
            speed.append(vehicles[i].get_speed())
            time.append(step*dt)
            time2.append(step*dt)
            ss_throughput.append(3600/theta0)
            flow.append(3600/theta)
            flow1.append(3600/theta1)
            i += 1
            
        simulation_step(vehicles, dt)
    

    plt.figure()
    plt.plot(time, position)
    plt.plot(time, position, 'o')
    plt.xlabel('Time')
    plt.ylabel('Position')
    plt.show()
    
    plt.figure()
    plt.plot(time, dx)
    plt.plot(time, dx, 'o')
    plt.xlabel('Time')
    plt.ylabel('Distance to Leader')
    plt.show()
    
    plt.figure()
    plt.plot(time, max_speed, 'r')
    plt.plot(time, speed)
    plt.plot(time, speed, 'o')
    plt.xlabel('Time')
    plt.ylabel('Speed')
    plt.show()
    
    plt.figure()
    plt.plot(time, dv)
    plt.plot(time, dv, 'o')
    plt.xlabel('Time')
    plt.ylabel('Speed Difference')
    plt.show()
    
    plt.figure()
    plt.plot(time, ss_throughput, 'r')
    plt.plot(time2, flow1, 'k')
    plt.plot(time2, flow1, 'o')
    plt.plot(time, flow)
    plt.plot(time, flow, 'o')
    plt.xlabel('Time')
    plt.ylabel('Flow')
    plt.show()
    
    print("Count =", len(flow)+1, "Theta_0 =", theta0, "Theta =", theta)
    











#==============================================================================
# Main function.
#==============================================================================
def main(argv):
    print(__doc__)
    
    vehicles, dt, total_time = initialize()
    run_simulation(vehicles, dt, total_time)
    



if __name__ == "__main__":
    main(sys.argv)

