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

cycle_length = 2*60
redClearTime = 0

PROGRAM = [WEGREEN]*(cycle_length/2-redClearTime)
PROGRAM.extend([ALLRED]*redClearTime)
PROGRAM.extend([NSGREEN]*(cycle_length/2-redClearTime))
PROGRAM.extend([ALLRED]*redClearTime)

#PROGRAM.reverse()

gmin = 4.0
b = 4.5
tau_sumo = 2.05
a = 1.0
step_length = 0.05
light_delay = 4*60/step_length
run_time = 60*60# seconds*minutes
tau_effective = lambda x: 1.0 + (5.0 + 1.0)/x #effective tau is sumo_tau + (lengthOfCar + minGap)/avgSpeed, on this lane, avgSpeed is 30m/s and from rou.xml, lengthOfCar = 5, minGap = 0.5, sumo_tau = 1
leaving_times = [[]]
v1 = []
v2 = []
v3 = []
sumopos1 = []
sumopos2 = []
sumopos3 = []
gt = []
gt2 = []
gt3 = []
times = []



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
            #print (step*step_length,flow_count)
            if first_car: #if its the first car, record the time that it comes in
                first_time = sensor_data[0][2]
                print first_time
                first_car = False

        if step < light_delay: #24960, let queue accumulate
            traci.trafficlights.setRedYellowGreenState("0", ALLRED)
        else:
            traci.trafficlights.setRedYellowGreenState("0",WEGREEN)#PROGRAM[programPointer])
            v1.append(traci.vehicle.getSpeed("2.0"))
            v2.append(traci.vehicle.getSpeed("2.1"))
            v3.append(traci.vehicle.getSpeed("2.2"))

            sumopos1.append(traci.vehicle.getPosition("2.0")[0])
            sumopos2.append(traci.vehicle.getPosition("2.1")[0])
            sumopos3.append(traci.vehicle.getPosition("2.2")[0])

            gt.append(traci.vehicle.getPosition("2.0")[0]-traci.vehicle.getPosition("2.1")[0]-5)
            gt2.append(traci.vehicle.getPosition("2.1")[0]-traci.vehicle.getPosition("2.2")[0]-5)
            gt3.append(traci.vehicle.getPosition("2.2")[0]-traci.vehicle.getPosition("2.3")[0]-5)

            times.append(step*step_length)


        
        step  += 1
        #print str(step)
   
    print "\n \n"
    print "-------------------------------------------------------- \n"
    print "Total number of cars that have passed: " + str(flow_count)
    tau = np.diff(leaving_times)
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

def vsafe(vl,v,gt):
    gd = np.add(np.multiply(vl,tau_sumo),gmin)
    vbar = np.divide(np.add(vl,v),2)
    numerator = np.subtract(gt,gd)
    denominator = np.add(np.divide(vbar,b),tau_sumo)
    return np.add(vl,np.divide(numerator,denominator))

def vCalc(vl,v,gt):
    vs = vsafe(vl,v,gt)
    vmax = 20
    vnext = v + a*step_length
    return max(0,min([vmax,vnext,vs]))


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
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    run_times = np.multiply([0.4+light_delay*step_length/60],60) #corresponds to 60 min of actual signal, 4 minutes for queue build up
    output = []
    for x in range(1):
        file_name = "cross1ltl"+"_"+str(x)+".sumocfg"
        path = "cross1ltl/"+file_name

        print path
    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
        sumoProcess = subprocess.Popen([sumoBinary, "-c", path,"--step-length", str(step_length), "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)


        output.append(run(run_times[0]))

        sumoProcess.wait()

    print output

    


    # gd = np.add(np.multiply(v1,step_length/2),gmin)
    # vbar = np.divide(np.add(v1,v2),2)
    # numerator = np.subtract(gt,gd)
    # denominator = np.add(np.divide(vbar,b),tau_sumo)

    # vs = np.add(v1, np.divide(numerator,denominator))
    vs2 = vsafe(v1,v2,gt)
    vs3 = vsafe(v2,v3,gt2)
    vmax = np.multiply(np.ones(len(vs2)),20)
    va = np.add(v2,a*step_length)
    va1 = [n*a*step_length for n in range(len(vs2))]
    va2 = [(n-10*step_length)*a*step_length for n in range(len(vs2))]
    va3 = [(n-20*step_length)*a*step_length for n in range(len(vs2))]

    vthry = [0]
    for i in range(len(vs2)):
        vthry.append(vCalc(v1[i],vthry[i],gt[i]))

    theta = np.divide(np.add(gt[:-1],5),v2[1:])
    thetaMin = np.multiply(np.ones(len(theta)),2.5)
    theta2 = np.multiply(np.ones(len(theta)),2)
    #pdb.set_trace()



    ###########################################
    ##
    ## Plot instantaneous tau
    ##
    ###########################################

    plt.figure(4)
    #pdb.set_trace()
    print len(times[51:])
    print len(theta[50:])
    m1, = plt.plot(times[51:],theta[50:],label='Measured')
    m2, = plt.plot(times[51:],thetaMin[50:],label='Theoretical Tau at s.s = 2.5s')
    m3, = plt.plot(times[51:],theta2[50:],label='Tau = 2s')
    plt.legend(handles=[m1,m2,m3],loc='upper right')
    #plt.plot(times[100:],thetaMin[100:])
    plt.xlabel("Time (s)")
    plt.ylabel("Tau (s)")
    plt.title("Evolution of tau in time - Accel = 2.6 m/s^2")
    plt.show()

    ###########################################
    ##
    ## Plot v(t+dt) of cars 
    ##
    ###########################################

    plt.figure(3)
    m1, = plt.plot(times,vmax,label='vmax')
    m2, = plt.plot(times,vs2,label='vs')
    m3, = plt.plot(times,va1,label='v+a*dt')
    m4, = plt.plot(times,v2,label='veh2 measured')
    #m5, = plt.plot(times,gt,label='Gap (m)')

    plt.legend(handles=[m1,m2,m3,m4],loc='upper left')
    plt.xlabel("Time (s)")
    plt.ylabel("Velocity")
    plt.title("Theoretical calculations")
    plt.show()

    # plt.figure(2)
    # m1, = plt.plot(times,vthry[0:-1],label="theoretical vehicle2")
    # m2, = plt.plot(times,v2,label="veh2 measured")

    # plt.legend(handles=[m1,m2],loc='upper left')
    # plt.show()

    #pdb.set_trace()

    ###########################################
    ##
    ## Plot velocity of cars 
    ##
    ###########################################

    plt.figure(1)
    #m1, = plt.plot(times,vmax,label="vmax")
    m6, = plt.plot(times,v1,label="veh1")
    m7, = plt.plot(times,v2,label="veh2")
    m8, = plt.plot(times,v3,label="veh3")
    m9, = plt.plot(times,gt,label='Gap btwn veh1 & veh2 (m)')

    plt.legend(handles=[m6,m7,m8,m9],loc='upper left')
    plt.xlabel("Time (s)")
    plt.ylabel("Velocity (m/s)")
    plt.title("Measured Velocities - Accel=1.0 m/s^2")
    plt.show()

    ###########################################
    ##
    ## Plot trajectory of cars 
    ##
    ###########################################

    # plt.figure(2)
    # x1 = [sumopos1[0]]
    # x2 = [sumopos2[0]]
    # x3 = [sumopos3[0]]
    # for i in range(len(v1)-1):
    #     x1.append(x1[i]+(v1[i]+v1[i+1])*step_length/2)
    #     x2.append(x2[i]+(v2[i]+v2[i+1])*step_length/2)
    #     x3.append(x3[i]+(v3[i]+v3[i+1])*step_length/2)

    # print (sumopos1[0:5],x1[0:5])

    # q1, = plt.plot(times,x1,label=" x1")
    # q2, = plt.plot(times,x2,label=" x2")
    # q3, = plt.plot(times,x3,label=" x3")

    # plt.legend(handles=[q1,q2,q3],loc='upper left')
    # plt.title('x(t+dt) = x(t) + (v(t) + v(t+dt))*dt/2 trajectory')
    # plt.show()




