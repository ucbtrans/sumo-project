#!/usr/bin/env python

#@file runner.py

import os
import sys
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '..\..\Python_functions'))
#sys.path.insert(0,'C:\Users\ArminAskari\Desktop\Berkeley 2013-2017\Research\CVT\ArminModify\Python_functions')

from getTrajectory import *

import optparse
import subprocess
import random
import pdb
import matplotlib.pyplot as plt
import math
import numpy as np
import scipy.io


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

PROGRAM = [WEGREEN]*60
PROGRAM.extend([NSGREEN]*60)
#PROGRAM.reverse()


step_length = 0.05
run_time = 60*60# seconds*minutes
tau_effective = lambda x: 1.0 + (5.0 + 1.0)/x #effective tau is sumo_tau + (lengthOfCar + minGap)/avgSpeed, on this lane, avgSpeed is 30m/s and from rou.xml, lengthOfCar = 5, minGap = 0.5, sumo_tau = 1
leaving_times = [[]]


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
            if first_car: #if its the first car, record the time that it comes in
                first_time = sensor_data[0][2]
                print first_time
                first_car = False

        if step*step_length < 60: #24960, let queue accumulate
            traci.trafficlights.setRedYellowGreenState("0", ALLRED)
        else:
            traci.trafficlights.setRedYellowGreenState("0",PROGRAM[programPointer])


        
        step  += 1
        #print str(step)
   
    print "\n \n"
    print "-------------------------------------------------------- \n"
    print "Total number of cars that have passed: " + str(flow_count)
    tau = np.diff(leaving_times)
    print "Total throughput extrapolated to 1hr: " + str(flow_count*(3600/(run_time-first_time)))
    print "Average car speed: " + str(np.mean(car_speeds))



    print "Max Theoretical throughput: " + str(3600/min(min(tau)))
    print "Min Theoretical throughput: " + str(3600/max(max(tau)))
    

    # print tau
    # print "Mean tau: " + str(np.mean(tau)) + "\n"
    # print "Var tau: " + str(np.var(tau)) + "\n"
    # print "Standard Dev tau: " + str(np.std(tau)) +"\n"

    traci.close()
    sys.stdout.flush()
    return [np.mean(tau),np.var(tau),np.std(tau)]



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

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if (options.nogui):
        sumoBinary = checkBinary('sumo-gui')
    else:
        sumoBinary = checkBinary('sumo-gui')

    run_times = np.multiply([9],60) #corresponds to 30 min of actual signal, 6 minutes for queue build up
    output = []
    for x in run_times:

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
        sumoProcess = subprocess.Popen([sumoBinary, "-c", "cross1ltl/cross1ltl.sumocfg","--step-length", str(step_length), 
            "--fcd-output", "fcd.xml", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)


        output.append(run(x))

        sumoProcess.wait()

    print output

    file_name = 'fcd.xml'
    #veh_id = inputnumber() #do vehicles 22,31 for 100% automated, vehicles 2,8 for all manual
    veh_id = str([1.0,2.0,2.1,2.2,1.1,1.2,2.3,2.4,1.3,1.4])
    t,dist = trajectoryData(file_name,veh_id)


    for i in range(len(dist)):
        time_array = np.asarray(t[i][:len(t[i])-1])
        time_array = time_array.astype('float')
        plt.plot(np.subtract(time_array,0),np.subtract(dist[i],0))

    # plt.xlabel('Time (s)')
    # plt.ylabel('Distance Travelled')
    # plt.title('Trajectory')
    #plt.axis([0,50, 60, 400])
    #plt.legend(['Veh ' + str for str in veh_id])
    plt.show()


