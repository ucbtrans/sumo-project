#!/usr/bin/env python

#@file runner.py

import os
import sys
import optparse
import subprocess
import random
import pdb
import settings
# import glob

# glob.platoons = []
# glob.platoonedvehicles=[]
# glob.platoonleaderspeed=[]

settings.init()

from platoon_functions import *


# import python modules from $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))
    from sumolib import checkBinary
except ImportError:
    sys.exit("please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
PORT = 8873 # the port used for communicating with your sumo instance


# Runs the simulation, and allows you to change traffic phase
def run(platoon_flag):
    ## execute the TraCI control loop
    traci.init(PORT)
    programPointer = 0 # initiates at start # len(PROGRAM) - 1 # initiates at end
    step = 0

    platooning = platoon_flag
    
    ## Platoons Settings - platoon_comm should be a divisor of platoon_create so that theres no misalignment (ie, forming
    # platoons without already adjusting the current platoons - if platoon_comm = 20, then possible to create platoon without
    # first updating the ones that exist that can have changed lanes)

    platoon_create = 50; # how often platoons update and are checked, every X ticks
    platoon_comm = 10; # how often platoons communicate, every X ticks
    numplatoons = 0;
    
    while traci.simulation.getMinExpectedNumber() > 0 and step <= 60*60*3*settings.step_frac: #60*60*1.5: # 1.5 hours
        traci.simulationStep() # advance a simulation step
        
        if step % settings.step_frac == 0:
            programPointer = (programPointer + 1) % 120
       		
        ################################# PLATOONING #################################
        
        ## PLATOON CREATION
        # Creates platoons if active, one line for each intersection and road segment.
        start_range = 1; end_range = 120;
        targetTau = 0.8; targetMinGap = 3;
        accTau = 1.1; accMinGap = 3;

        ## PLATOON CONTROL
        if platooning and (step % platoon_comm == 0):
            #step >= 88*settings.step_frac
            platoon_control(accTau, accMinGap, targetTau, targetMinGap, platoon_comm, step/settings.step_frac) #step%150 == 0 and step >= 1000)

        if platooning and (step % platoon_create == 0):

            ## top left intersection
            create_platoons("116069075#0", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#0", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#0", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("116069075#0.376", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#0.376", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#0.376", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#0.376", "_3", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("5982169#1", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("5982169#1", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("5982169#1", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("116069075#1", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#1", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#1", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("5982169#0.394", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("5982169#0.394", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("5982169#0.394", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("5982169#0.394", "_3", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            ## right of top left intersection

            create_platoons("116069075#1.264", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#1.264", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#1.264", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#1.264", "_3", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("116069075#1.338", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#1.338", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#1.338", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#1.338", "_3", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069075#1.338", "_4", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("5982169#0", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("5982169#0", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("5982169#0", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("26467810", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("26467810", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("26467810", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("116069186#1.128", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069186#1.128", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069186#1.128", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069186#1.128", "_3", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069186#1.128", "_4", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("116069186#1.112", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069186#1.112", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069186#1.112", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            ## to the right of above intersection
            create_platoons("26467810.54", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("26467810.54", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("26467810.54", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("26467810.54", "_3", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("26467810.54", "_4", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("116069186#1", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069186#1", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069186#1", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("116069261", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("116069261", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("50846753.54", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("50846753.54", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("50846753.54", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("-50846769", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("-50846769", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("-50846769", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            ## finish main route
            create_platoons("50846755#0", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("50846755#0", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("50846755#0.517", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("50846755#0.517", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("50846755#0.517", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("50846755#0.671", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("50846755#0.671", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("50846755#0.671", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("50846755#0.671", "_3", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)


            create_platoons("50846755#2.0", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("50846755#2.0", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)

            create_platoons("50846755#2.0.590", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("50846755#2.0.590", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("50846755#2.0.590", "_2", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)





        
	    ## Final Simulation Step Actions
        # sets traffic light at intersection 13 at the phase indicated
        sys.stdout.flush()
        step += 1

    traci.close()
    sys.stdout.flush()

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')


    sumoProcess = subprocess.Popen([sumoBinary, "-c", "network/testmap.sumocfg", "--step-length", str(settings.step_length), "--tripinfo-output",
                                    "tripinfo.xml", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
    run(False)
    sumoProcess.wait()
