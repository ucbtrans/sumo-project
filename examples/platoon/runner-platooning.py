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

platooning = True

# designates the phases definitions, one letter for each direction and turn type, this is for intersection 13
NSGREEN = "GGGgrrrrGGGrrrr"
NSYELLOW = "yyygrrrryyyrrrr"
TURN1 = "rrrGrrrrrrrrrrr" # the phase for cars turning
CLEAR1 = "rrryrrrrrrrrrrr"
WEGREEN = "rrrrGGGgrrrGGGg"
WEYELLOW = "rrrryyygrrryyyg"
TURN2 = "rrrrrrrGrrrrrrG" # the second phase for cars turning
CLEAR2 = "rrrrrrryrrrrrry"

# An example of a potential cycle for the traffic signal, 1 second each step
# NS pass goes during i=0-9 and WE pass goes during i=16-33

NS_END = 28; NS_START = 23; WE_END=101; WE_START=95; len_p = 120;
PROGRAM = [NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, #9
	NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, #19
	NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, #29
	NSYELLOW, NSYELLOW, NSYELLOW, NSYELLOW, TURN1, TURN1, TURN1, TURN1, TURN1, #38
	TURN1, TURN1, TURN1, TURN1, TURN1, TURN1, TURN1, CLEAR1, CLEAR1, CLEAR1, #48
	WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN,  #58
	WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, #66
	WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, # 76
	WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, # 84
	WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, #93  
	WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, WEGREEN, #101
	WEYELLOW, WEYELLOW, WEYELLOW, WEYELLOW, TURN2, TURN2, TURN2, TURN2, TURN2, #110
	TURN2, TURN2, TURN2, TURN2, TURN2, TURN2, TURN2, CLEAR2, CLEAR2, CLEAR2] #120
	
# Global list of all cars in platoons
# platoonedvehicles = []
# platoons = []
# platoonleaderspeed = []

# Runs the simulation, and allows you to change traffic phase
def run():
    ## execute the TraCI control loop
    traci.init(PORT)
    programPointer = 0 # initiates at start # len(PROGRAM) - 1 # initiates at end
    step = 0
    
    # Keeps track of current queue length in each direction
    queue_east = 0;queue_north = 0;queue_west = 0;queue_south = 0;
    # Flow counters, currently double counts cars
    flow_east = 0;flow_north = 0;flow_west = 0;flow_south = 0;
    flow_east_back = 0;flow_north_back = 0;flow_west_back = 0;flow_south_back = 0; # separate counter for back sensor
    # Counters for soft reset at 30 minutes
    flow_east_be = 0;flow_north_be = 0;flow_west_be = 0;flow_south_be = 0;
    # Keeps track of the last car through each sensor
    last_east1 = "";last_north1 = "";last_west1 = "";last_south1 = "";
    last_east2 = "";last_north2 = "";last_west2 = "";last_south2 = "";
    last_east3 = "";
    last_east_t1 = "";last_north_t1 = "";last_west_t1 = "";last_south_t1 = "";
    last_east_t2 = "";last_north_t2 = "";last_west_t2 = "";last_south_t2 = "";
    acc_count = 0; manual_count = 0;
    
    ## Platoons Settings
    platoon_check = 50; # how often platoons update and are checked, every X ticks
    platoon_comm = 20; # how often platoons communicate, every X ticks
    numplatoons = 0;
    
    while traci.simulation.getMinExpectedNumber() > 0 and step <= 60*60*0.15*settings.step_frac: #60*60*1.5: # 1.5 hours
        traci.simulationStep() # advance a simulation step
        
        # sets next phase in the program cycle
        if step % settings.step_frac == 0:
        	programPointer = (programPointer + 1) % len_p
        #print programPointer
        
       		
        ################################# PLATOONING #################################
        
        ## PLATOON CREATION
        # Creates platoons if active, one line for each intersection and road segment.
        start_range = 1; end_range = 120;
        targetTau = 0.1; targetMinGap = 2.0;
        accTau = 0.1; accMinGap = 2.0;
        
        if platooning and (step % platoon_check == 0):
            create_platoons("G5", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("G5", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("G3b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("G3b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("G6b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            create_platoons("G6b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #screate_platoons("N3b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("N3b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("N1", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("N1", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F18b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F18b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            
            #create_platoons("G7b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G7b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G3", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G3", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G1", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G1", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G6", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G6", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G7", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G7", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G8", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G8", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G8b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G8b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H1b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H1b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H1", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H1", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H2b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H2b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F16", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F16", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            
            #create_platoons("F15b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F15b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H3", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H3", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H3b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H3b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F13b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F13b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F14b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F14b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H4b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H4b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F11b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F11b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F12b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F12b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H5b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H5b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F9b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F9b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F10b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F10b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H6b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H6b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F7b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F7b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F8b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F8b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H7b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F7b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F5b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F4b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F4b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H8b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H8b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H7b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            
            #create_platoons("F3", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F3", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F4", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F4", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H9b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H9b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H10b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H10b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H11b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("H11b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F1b", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("F1b", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G5", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
       
        ## PLATOON CONTROL
        if platooning and (step % platoon_comm == 0):
            platoon_control(accTau, accMinGap, targetTau, targetMinGap, platoon_comm)
        
	    ## Final Simulation Step Actions
        # sets traffic light at intersection 13 at the phase indicated
        sys.stdout.flush()
		#programPointer -= 1
        #traci.trafficlights.setRedYellowGreenState("13", PROGRAM[programPointer])
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

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    sumoProcess = subprocess.Popen([sumoBinary, "-c", "network/huntcol.sumocfg", "--step-length", str(settings.step_length), "--tripinfo-output",
                                    "tripinfo.xml", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
    run()
    sumoProcess.wait()
