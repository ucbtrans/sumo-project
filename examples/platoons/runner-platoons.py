#!/usr/bin/env python

#@file runner.py

import os
import sys
import optparse
import subprocess
import random

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
step_frac = 10;
step_length = 1.0/step_frac;
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
platoonedvehicles = []
platoons = []
platoonleaderspeed = []

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
    # Counters for soft reset at 30 minutes
    flow_east_be = 0;flow_north_be = 0;flow_west_be = 0;flow_south_be = 0;
    # Keeps track of the last car through each sensor
    last_east1 = "";last_north1 = "";last_west1 = "";last_south1 = "";
    last_east2 = "";last_north2 = "";last_west2 = "";last_south2 = "";
    last_east3 = "";
    last_east_t1 = "";last_north_t1 = "";last_west_t1 = "";last_south_t1 = "";
    last_east_t2 = "";last_north_t2 = "";last_west_t2 = "";last_south_t2 = "";
    
    ## Platoons Settings
    platooning = True
    platoon_check = 1; # how often platoons communicate and are verified
    numplatoons = 0;
    
    while traci.simulation.getMinExpectedNumber() > 0 and step <= 60*60*1.5*step_frac: #60*60*1.5: # 1.5 hours
        traci.simulationStep() # advance a simulation step
        
        # sets next phase in the program cycle
        if step % step_frac == 0:
        	programPointer = (programPointer + 1) % len_p
        #print programPointer
        
        # gets number of vehicles in the induction area in the last step, this is currently not being used
        # numPriorityVehicles = traci.inductionloop.getLastStepVehicleNumber("south_inner1")
        
        ###################################### SOUTH ######################################
        structure1 = traci.inductionloop.getVehicleData("south_inner1")
        structure2 = traci.inductionloop.getVehicleData("south_inner1")
        structure3 = traci.inductionloop.getVehicleData("south_outer1")
        structure4 = traci.inductionloop.getVehicleData("south_outer1")
        structure5 = traci.inductionloop.getVehicleData("south_check1")
        structure6 = traci.inductionloop.getVehicleData("south_check1")

	    # Detecting a full queue using method 1
        if (structure3 and structure3[0][0] == last_south_t1 and structure3[0][3] == -1) or (structure5 and structure5[0][0] == last_south_t1 and structure5[0][3] == -1): # in case we detect the back is still
	        if (structure4 and structure4[0][0] == last_south_t2 and structure4[0][3] == -1) or (structure6 and structure6[0][0] == last_south_t2 and structure6[0][3] == -1):
		        if structure1 and structure2 and structure1[0][0] == last_south1 and structure2[0][0] == last_south2: # in case we detect the front is still
					# use getLastStepMeanSpeed instead?
					if (structure1[0][3] == -1) and (structure2[0][3] == -1): # all four cars are still
					#if queue_south > 24: # we are already almost full (one car didn't get detected), method 2
						#print "South Queue Full"
						queue_south = 26
						
        for car in (structure1):
	        if structure1 and car[0] != last_south1 and car[0] != last_south2:
	        	last_south1 = car[0]
	        	queue_south -= 1
	        	flow_south += 1
        for car in (structure2):
	        if structure2 and car[0] != last_south1 and car[0] != last_south2:
	        	last_south2 = car[0]
	        	queue_south -= 1
	        	flow_south += 1
        for car in (structure3):
	        if structure3 and car[0] != last_south_t1 and car[0] != last_south_t2:
	        	last_south_t1 = car[0]
	        	queue_south += 1
	        	flow_south += 1
        for car in (structure4):
	        if structure4 and car[0] != last_south_t1 and car[0] != last_south_t2:
	        	last_south_t2 = car[0]
	        	queue_south += 1
	        	flow_south += 1
	        	
        if queue_south < 0:
	        queue_south = 0
	    
        
        ###################################### WEST ######################################
        structure1 = traci.inductionloop.getVehicleData("west_inner1")
        structure2 = traci.inductionloop.getVehicleData("west_inner1")
        structure3 = traci.inductionloop.getVehicleData("west_outer1")
        structure4 = traci.inductionloop.getVehicleData("west_outer1")
        structure5 = traci.inductionloop.getVehicleData("west_check1")
        structure6 = traci.inductionloop.getVehicleData("west_check1")
        
	    # Detecting a full queue using method 1
        if (structure3 and structure3[0][0] == last_west_t1 and structure3[0][3] == -1) or (structure5 and structure5[0][0] == last_west_t1 and structure5[0][3] == -1): # in case we detect the back is still
	        if (structure4 and structure4[0][0] == last_west_t2 and structure4[0][3] == -1) or (structure6 and structure6[0][0] == last_west_t2 and structure6[0][3] == -1):
		        if structure1 and structure2 and structure1[0][0] == last_west1 and structure2[0][0] == last_west2: # in case we detect the front is still
					if (structure1[0][3] == -1) and (structure2[0][3] == -1): # all four cars are still
					#if queue_west > 24: # we are already almost full (one car didn't get detected), method 2
						#print "West Queue Full"
						queue_west = 26
					
        for car in (structure1):
            if structure1 and car[0] != last_west1 and car[0] != last_west2:
        	    last_west1 = car[0]
        	    queue_west -= 1
        	    flow_west += 1
        for car in (structure2):
	        if structure2 and car[0] != last_west1 and car[0] != last_west2:
	        	last_west2 = car[0]
	        	queue_west -= 1
	        	flow_west += 1
        for car in (structure3):
            if structure3 and car[0] != last_west_t1 and car[0] != last_west_t2:
	        	last_west_t1 = car[0]
	        	queue_west += 1
	        	flow_west += 1
        for car in (structure4):
	        if structure4 and car[0] != last_west_t1 and car[0] != last_west_t2:
	        	last_west_t2 = car[0]
	        	queue_west += 1
	        	flow_west += 1
	    
        if queue_west < 0:
	        queue_west = 0
        	
        ###################################### NORTH ######################################
        structure1 = traci.inductionloop.getVehicleData("north_inner1")
        structure2 = traci.inductionloop.getVehicleData("north_inner1")
        structure3 = traci.inductionloop.getVehicleData("north_outer1")
        structure4 = traci.inductionloop.getVehicleData("north_outer1")

        if structure1 and structure1[0][0] != last_north1:
        	last_north1 = structure1[0][0]
        	queue_north -= 1
        	flow_north += 1
        if structure2 and structure2[0][0] != last_north2:
        	last_north2 = structure2[0][0]
        	queue_north -= 1
        	flow_north += 1
        if structure3 and structure3[0][0] != last_north_t1:
        	last_north_t1 = structure3[0][0]
        	queue_north += 1
        	flow_north += 1
        if structure4 and structure4[0][0] != last_north_t2:
        	last_north_t2 = structure4[0][0]
        	queue_north += 1
        	flow_north += 1
        	
        if queue_north < 0:
	        queue_north = 0
        	
        ###################################### EAST ######################################
        structure1 = traci.inductionloop.getVehicleData("east_inner1")
        structure2 = traci.inductionloop.getVehicleData("east_inner1")
        structure3 = traci.inductionloop.getVehicleData("east_outer1")
        structure4 = traci.inductionloop.getVehicleData("east_outer1")
        structure5 = traci.inductionloop.getVehicleData("east_branch")

        for car in (structure1):
            if structure1 and car[0] != last_east1 and car[0] != last_east2:
                last_east1 = car[0]
                queue_east -= 1
                flow_east += 1
        for car in (structure2):
	        if structure2 and car[0] != last_east1 and car[0] != last_east2:
	        	last_east2 = car[0]
	        	queue_east -= 1
	        	flow_east += 1
        for car in (structure3):
	        if structure3 and car[0] != last_east_t1:
	        	last_east_t1 = car[0]
	        	queue_east += 1
	        	flow_east += 1
        for car in (structure4):
	        if structure4 and car[0] != last_east_t2:
	        	last_east_t2 = car[0]
	        	queue_east += 1
	        	flow_east += 1
        for car in (structure5):
	        if structure5 and [0] != last_east3:
	        	last_east3 = structure5[0][0] # branch
	        	queue_east -= 1
	        	flow_east += 1
	        	
        if queue_east < 0:
	        queue_east = 0
        
        ###################################### LIGHT CONTROL ######################################
        light_control = False
        #programPointer = 90 # forces always green WE
        
        if light_control:
	        if (queue_east + queue_west) < (queue_north + queue_south): # if the vertical pressure is higher
	            if programPointer == NS_END:
	            	#print "restarting NS"
	                # NS is currently ending, go back
	                programPointer = NS_START
	            #elif programPointer > WE_START:
	            #    # WE is currently active, skip to end of phase
	            #    programPointer = max(WE_END, programPointer)
	        elif (queue_east + queue_west) > (queue_north + queue_south): # then horizontal pressure is higher
	            if programPointer == WE_END:
	            	#print "restarting WE"
	                # WE is currently ending, restart
	                programPointer = WE_START
	            #elif programPointer < NS_END:
	            #    # NS is currently active, skip to end of phase
	            #    programPointer = NS_END
       	
       	if (step / step_frac) == 60*30: # warm-up time
       		flow_east_be = flow_east
       		flow_west_be = flow_west
       		flow_north_be = flow_north
       		flow_south_be = flow_south
       		
       	if (step % step_frac == 0) and ((step / step_frac) % (60*30) == 0) and (step > 0): #step == 60*60*1.5: 
 	      	print "----"
 	      	#print(str(flow_east) + " " + str(flow_west) + " " + str(flow_north) + " " + str(flow_south))
    	   	#print (flow_east - flow_east_be)
       		print (flow_west - flow_west_be)
       		#print (flow_north - flow_north_be)
       		#print (flow_south - flow_south_be)
 	      	#print "----"
       		
        ################################# PLATOONING #################################
        
        ## PLATOON CREATION
        # Run platoons if active, one line for each intersection and road segment.
        start_range = 47; end_range = 48;
        targetTau = 0.15; targetMinGap = 0.5;
        accTau = 0.45; accMinGap = 2.0;
        
        if platooning:
            create_platoons("G5", "_1", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
            #create_platoons("G5", "_0", start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer)
       
        ## PLATOON CONTROL
        if (step % platoon_check == 0):
            platoon_control(accTau, accMinGap, platoon_check)
        
	    ## Final Simulation Step Actions
        # sets traffic light at intersection 13 at the phase indicated
        sys.stdout.flush()
		#programPointer -= 1
        traci.trafficlights.setRedYellowGreenState("13", PROGRAM[programPointer])
        step += 1
        
    traci.close()
    sys.stdout.flush()

# Control the platoons and performs inter-vehicle communication to prevent crashes
def platoon_control(accTau, accMinGap, platoon_check):
            # go through each platoon at this step and maintain communication/check if still a platoon
            allvehicles = traci.vehicle.getIDList();
            index = -1
            for platoon in platoons:
                index += 1
            	
                if platoon_maintenance(platoon, accTau, accMinGap, allvehicles) == -1:
                    continue
                
                # Communication step
                leader = platoon[2]
                leader_accel = traci.vehicle.getAccel(leader)
                leader_speed = traci.vehicle.getSpeed(leader)
                if len(platoonleaderspeed) > index: # if we are not in the first time step for this platoon
                	leader_accel = (leader_speed - platoonleaderspeed[index]) / (step_length*platoon_check)
                else:
                	leader_accel = 0
                target_speed = traci.lane.getMaxSpeed(traci.vehicle.getLaneID(leader))
                
                if (leader_accel < -0.1) or (leader_speed < target_speed):
                	for car in platoon[3:]: # go through all followers and have them slow down accordingly
                		traci.vehicle.slowDown(car, leader_speed, step_length*platoon_check) # slows down the vehicle for the appropriate period
                
                if (leader_accel < -0.1) and (leader_speed < target_speed * 0.8): # vehicle encountering heavy traffic or stop signal, break up platoon
                	platoonedvehicles.remove(leader)
                	traci.vehicle.setColor(leader, (0,255,0,0))
                	for car in platoon[3:]: # go through all followers and have them slow down accordingly
                		traci.vehicle.slowDown(car, leader_speed, step_length*platoon_check) # slows down the vehicle for the appropriate period
                		traci.vehicle.setTau(car, accTau)
                		traci.vehicle.setMinGap(car, accMinGap)
                		traci.vehicle.setColor(car, (0,255,0,0))
                	platoons.remove(platoon)
                	platoonedvehicles.remove(car)
	    
            del platoonleaderspeed[:] # clears the list
            for platoon in platoons: # records the speed of all platoon leaders to calculate acceleration # records the speed of all platoon leaders to calculate acceleration
            	platoonleaderspeed.append(traci.vehicle.getSpeed(platoon[2]))

# Performes maintenance on platoons by eliminating vehicles for various reasons
def platoon_maintenance(platoon, accTau, accMinGap, allvehicles):
                # First perform maintenance on the platoon
                for car in platoon[2:]:
                    if not (car in allvehicles): # car not in simulation anymore
		                platoon.remove(car)
		                platoonedvehicles.remove(car) 	# this is causing issues and it should not. Only started after I moved code to a function, come back to it
		                continue
	                
	            # Check to see lane divergence
                leader = platoon[2]
                curr_lane = traci.vehicle.getLaneID(leader)
                if (curr_lane != platoon[0]) and (curr_lane != platoon[1]) and (curr_lane[:-1] == platoon[1][:-1]):
                	# the leader switched lanes, so remove it as leader
                	platoon.remove(leader)
                	platoonedvehicles.remove(leader)
                	traci.vehicle.setColor(leader, (0,255,0,0))
                	# Configure the new leader
                	leader = platoon[2]
                	curr_lane = traci.vehicle.getLaneID(leader)
                	traci.vehicle.setMinGap(leader, accMinGap)
                	traci.vehicle.setTau(leader, accTau)
                	traci.vehicle.setColor(leader, (0,255,255,0))
                
                if (curr_lane != platoon[0]) and (curr_lane != platoon[1]) and (":" not in curr_lane):
                	# our leader has moved on to a new lane.
                	platoon[0] = platoon[1];
                	platoon[1] = curr_lane
                
                lane1 = platoon[0]; lane2 = platoon[1];
                
                # Go through follower vehicles
                for car in platoon[3:]: 
                	curr_lane = traci.vehicle.getLaneID(car)
                	if (curr_lane != lane1) and (curr_lane != lane2) and (":" not in curr_lane):
                		# car has switched lanes on reached a new road
                	    platoon.remove(car)
                	    platoonedvehicles.remove(car) # remove car and revert it to regular ACC
                	    traci.vehicle.setMinGap(car, accMinGap)
                	    traci.vehicle.setTau(car, accTau)
                	    traci.vehicle.setColor(car, (0,255,0,0))
                
	        	# If platoon is gone, delete it
                if len(platoon) < 4:
                	traci.vehicle.setColor(leader, (0,255,0,0))
                	platoons.remove(platoon)
                	platoonedvehicles.remove(leader)
                	return -1
                return 0

# Creates platoons in a given road segment and cycle time interval (between 1 and 120)
def create_platoons(road, lane, start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer):
            road_segment = road + lane;
            target_speed = traci.lane.getMaxSpeed(road_segment)
        	# If the signal is about to open, create platoons
            if (programPointer >= start_range and programPointer <= end_range):
                first = True
                cars = traci.lane.getLastStepVehicleIDs(road_segment)
                platoon = [road_segment] # start platoon empty
                # iterate through cars in order of closest to light
                for car in cars[::-1]:
                	#if traci.vehicle.getPosition(car): # potential check to add to see if car is past a certain point; not necessary
                	#print traci.vehicle.getRoute(car)
                	
                	# check if the vehicle is automatic
                    type = traci.vehicle.getTypeID(car)
                    # If the car is ACC, add to platoon here
                    if (type == "CarA"):
                    	# If vehicle is already in a platoon, break platoon creation here
                    	if (car in platoonedvehicles):
                    	    if len(platoon) == 3: # if there was a single ACC vehicles
                    	        platoonedvehicles.remove(platoon[2]) # do not make the platoon
                                traci.vehicle.setColor(car, (0,255,0,0))
                            if len(platoon) > 3: # if there were multiple ACC vehicles
                            	platoons.append(platoon) # add the platoon
                            first = True
                            platoon = [road_segment]
                            continue
                            
                    	if first:
                    		# leading car maintains the same min gap and tau as before
                    		if car == cars[0]: # if we have a lone vehicle which is last in the lane, don't make it into a platoon
                    			continue
                        	traci.vehicle.setColor(car, (0,255,255,0)) 	# set its color to cyan, signifying car leader
                        	traci.vehicle.setSpeed(car, target_speed) 		# set its speed higher to help ease propogation delay	
                        	first = False
                        	leader_route = traci.vehicle.getRoute(car) # gets the route for the leading car
                        	platoon.append(get_next_segment(leader_route, road) + lane) # gets the leading car's next segment
                        	platoon.append(car)
                        	platoonedvehicles.append(car)
                    	else:
                    	    traci.vehicle.setMinGap(car, targetMinGap) 	# temporarily set its minimum gap
                    	    traci.vehicle.setTau(car, targetTau) 		# temporarily set its tau
                    	    traci.vehicle.setColor(car, (0,0,255,0)) 	# set its color to blue, signifying car follower
                    	    traci.vehicle.setSpeed(car, target_speed) 			# set its speed higher to help ease propogation delay
                    	    platoon.append(car)
                    	    platoonedvehicles.append(car)
                    	    if car == cars[0]: # this platoon includes the last car on this segment
                    			platoons.append(platoon) # add the platoon
                    # if it is manual, stop making the platoon, since no cars behind can accelerate anyways
                    else:
                    	if len(platoon) == 3: # if there was a single ACC vehicles
                    	    platoonedvehicles.remove(platoon[2]) # do not make the platoon
                            traci.vehicle.setColor(platoon[2], (0,255,0,0))
                        if len(platoon) > 3: # if there were multiple ACC vehicles
                        	platoons.append(platoon) # add the platoon
                        first = True
                        platoon = [road_segment]


def get_next_segment(leader_route, road_segment): # This method returns the next segment in a vehicle's itinerary
	index = 0
	for segment in leader_route:
		index += 1
		if segment == road_segment:
			break
	return leader_route[index]

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
    sumoProcess = subprocess.Popen([sumoBinary, "-c", "network/huntcol.sumocfg", "--step-length", str(step_length), "--tripinfo-output",
                                    "tripinfo.xml", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
    run()
    sumoProcess.wait()
