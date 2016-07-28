#!/usr/bin/env python

#@file runner.py

import os
import sys
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '..\..\Python_functions'))
#sys.path.insert(0,'C:\Users\ArminAskari\Desktop\Berkeley 2013-2017\Research\CVT\ArminModify\Python_functions')

#from getTrajectory import *

import optparse
import subprocess
import random
import pdb
import math
import matplotlib.pyplot as plt
import numpy as np
import settings

settings.init()

from platoon_functions import *


# import python modules from $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(
       __file__)), '..', "tools"))
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(os.path.realpath(
       __file__)), "..")), "tools"))
    from sumolib import checkBinary
except ImportError:
    sys.exit("please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
PORT = 8873 # the port used for communicating with your sumo instance

# designates the phases definitions, one letter for each direction and turn type, this is for intersection 13
NSGREEN = "GGGgrrrrGGGgrrrr"
WEGREEN = "rrrrGGGgrrrrGGGg"
ALLRED = "rrrrrrrrrrrrrrrr"

cycle_length = 2*60
redClearTime = 0
PROGRAM = [WEGREEN]*(cycle_length/2-redClearTime)
PROGRAM.extend([ALLRED]*redClearTime)
PROGRAM.extend([NSGREEN]*(cycle_length/2-redClearTime))
PROGRAM.extend([ALLRED]*redClearTime)

PROGRAM2 = PROGRAM[::-1]

#PROGRAM.reverse()

step_length = 0.05
light_delay = 2*60/step_length
run_time = 0.5*60*60# seconds*minutes
leaving_times = [[]]
flow_array = []
flow_array_ss = []
ssValue = lambda x: 1/2.5*(x-light_delay*step_length)
flowTime_array = []
tau_cars = []
time_cars = []

binRate = 1/step_length

## Platoons Settings
platoon_check = 50; # how often platoons update and are checked, every X ticks
platoon_comm = 20; # how often platoons communicate, every X ticks
numplatoons = 0;

start_range = 1; end_range = 120;
targetTau = 0.1; targetMinGap = 2.0;
accTau = 0.1; accMinGap = 2.0;



def flowCount(sensor_data,sensor_str,prev_veh_id):
    carCount = 0
    car_ids = []
    for idx in range(len(sensor_data)):
        if len(sensor_data[idx]) != 0:
            veh_id = sensor_data[idx][0][0]
            car_ids.append(veh_id)
            last_id = prev_veh_id[idx]
            if veh_id != last_id:
                carCount += 1
            if sensor_data[idx][0][3] != -1: #if the vehicle is leaving the sensor, record the time it left
                leaving_times[idx].extend([sensor_data[idx][0][2]])

    return carCount, car_ids

# Runs the simulation, and allows you to change traffic phase
def run(run_time):
    ## execute the TraCI control loop
    traci.init(PORT)
    programPointer = 0 # initiates at start # len(PROGRAM) - 1 # initiates at end
    step = 0
    flow_count = 0
    first_car = True
    prev_veh_id = ' '
    prev_veh_id2 = ' '
    pointer_offset = 0
    car_speeds = []

    

    while traci.simulation.getMinExpectedNumber() > 0 and step <= run_time*(1/step_length): 
        traci.simulationStep() # advance a simulation step

        programPointer = int(math.floor(step/(int(1/step_length))))%len(PROGRAM) - pointer_offset 

        sensor_data = traci.inductionloop.getVehicleData("sensor")

        if len(sensor_data) != 0:
            flow_increment,prev_veh_id = flowCount([sensor_data],["sensor"],prev_veh_id)
            car_speeds.append(traci.vehicle.getSpeed(sensor_data[0][0]))
            flow_count += flow_increment
            #print (step*step_length,flow_count)
            if first_car: #if its the first car, record the time that it comes in
                first_time = sensor_data[0][2]
                first_car = False

        if step < light_delay: #24960, let queue accumulate
           traci.trafficlights.setRedYellowGreenState("0", ALLRED)
        else:
           traci.trafficlights.setRedYellowGreenState("0",PROGRAM[programPointer])
           traci.trafficlights.setRedYellowGreenState("2",PROGRAM2[programPointer])
           if step % binRate == 0:
               flow_array.append(flow_count)
               flowTime_array.append(step*step_length)
               flow_array_ss.append(ssValue(step*step_length))

        if (step % platoon_check == 0):
            create_platoons("1i", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

        #print flow_count


        
        step  += 1
        #print str(step)
   
    print "\n \n"
    print "-------------------------------------------------------- \n"
    print "Total number of cars that have passed: " + str(flow_count)

    tau = np.diff(leaving_times)
    tau_cars.extend(tau)
    time_cars.extend(leaving_times[0][1:])


    extrap_flow = flow_count*(3600/(run_time-first_time))
    print "Total throughput extrapolated to 1hr: " + str(extrap_flow)
    print "Average car speed: " + str(np.mean(car_speeds))



    print "Max Theoretical throughput: " + str(3600/min(min(tau)))
    print "Min Theoretical throughput: " + str(3600/max(max(tau)))
    

    print tau
    print "Mean tau: " + str(np.mean(tau)) + "\n"
    print "Var tau: " + str(np.var(tau)) + "\n"
    print "Standard Dev tau: " + str(np.std(tau)) +"\n"
    print "Min Tau:" + str(np.min(tau))
    print "Max Tau:" + str(np.max(tau))

    traci.close()
    sys.stdout.flush()
    return extrap_flow #[np.mean(tau),np.var(tau),np.std(tau)]

#get_options function for SUMO
def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=True, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    sumoBinary = checkBinary('sumo-gui')

    #run_times = [i * 60 for i in range(20+light_delay*step_length/60)] #np.multiply([20+light_delay*step_length/60],60) #corresponds to 60 min of actual signal, 4 minutes for queue build up
    output = []
    file_name = "cross2ltl"+"_"+str(10)+".sumocfg"
    path = "cross2ltl/"+file_name

    print path
    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    sumoProcess = subprocess.Popen([sumoBinary, "-c", path,"--step-length", str(step_length), "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)

    run(run_time*1.2)
        #output.append(run(run_times[0]))
    print output

    filestr = '2min'+str(redClearTime)+'RCT_taus'
    filestrTime = filestr+'_time'
    #np.savetxt(filestr,np.divide(3600,tau_cars[0]),fmt='%d')
    #np.savetxt(filestrTime,time_cars,fmt='%d')

    ##########################################
    ##
    ## Plot instantenous flow
    ##
    ###########################################
    plt.figure(1)
    m1, = plt.plot(time_cars,np.divide(3600,tau_cars[0]),label='Measured Throughput')
    plt.legend(handles=[m1],loc='upper left')
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput per hr")
    plt.title("Total throughput vs time for 2 min cycle")
    plt.axes([240,580,400,2000])
    plt.show()



    # ###########################################
    # ##
    # ## Plot flow count
    # ##
    # ###########################################
    # plt.figure(2)
    # m1, = plt.plot(flowTime_array,flow_array,label='Measured Throughput')
    # m2, = plt.plot(flowTime_array,flow_array_ss,label='Steady State Throughput - No signal')
    # plt.legend(handles=[m1,m2],loc='upper left')
    # plt.xlabel("Time (s)")
    # plt.ylabel("No. of Veh")
    # plt.title("Total throughput vs time for 2 min cycle")
    # plt.show()




