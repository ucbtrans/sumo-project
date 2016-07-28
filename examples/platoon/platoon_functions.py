import os
import sys
import optparse
import subprocess
import random
import traci
import settings
import pdb

########## Global variables used in runner file ################################
# settings.platoonedvehicles = []
# settings.platoons = []
# settings.platoonleaderspeed = []
# Note - whenever trying to modify the global variables, they must be referenced
#	as settings.platoonedvehicles or settings.platoons, etc...
#
# Updated 7/28/16 - Armin
################################################################################



################################################################################
# Platoon Control function
#   This function controls the platoons and performs inter-vehicle communication
#   to prevent crashes
################################################################################
def platoon_control(accTau, accMinGap, targetTau, targetMinGap, platoon_comm):
	allvehicles = traci.vehicle.getIDList();
	
	# Go through and make sure all vehicles are still in simulation
	for veh in settings.platoonedvehicles:
		if not (veh in allvehicles): 
			settings.platoonedvehicles.remove(veh)
	
	index = -1
	for platoon in settings.platoons:
		index += 1
		
		if platoon_maintenance(platoon, accTau, accMinGap, allvehicles) == -1:
			continue
		
		# Communication step
		leader = platoon[2]
		leader_accel = traci.vehicle.getAccel(leader)
		leader_speed = traci.vehicle.getSpeed(leader)
		if len(settings.platoonleaderspeed) > index: # if we are not in the first time step for this platoon
			leader_accel = (leader_speed - settings.platoonleaderspeed[index]) / (settings.step_length*platoon_comm)
		else:
			leader_accel = 0
		target_speed = traci.lane.getMaxSpeed(traci.vehicle.getLaneID(leader))
		
		if (leader_accel < -1.0) or (leader_speed < target_speed):
			for car in platoon[3:]: # go through all followers and have them slow down accordingly
				leading_temp = traci.vehicle.getLeader(car, 100)
				if leading_temp:
					dist = leading_temp[1]
				else:
					dist = 100
				if dist < leader_speed * targetTau: # if we're too close
						traci.vehicle.slowDown(car, leader_speed, settings.step_length*platoon_comm) # slows down the vehicle for the appropriate period

	del settings.platoonleaderspeed[:] # clears the list
	for platoon in settings.platoons: # records the speed of all platoon leaders to calculate acceleration # records the speed of all platoon leaders to calculate acceleration
		settings.platoonleaderspeed.append(traci.vehicle.getSpeed(platoon[2]))


################################################################################
# Platoon Maintenance function
#   This function performs maintenance on platoons by removing vehicles from 
#   them for various reasons
################################################################################
def platoon_maintenance(platoon, accTau, accMinGap, allvehicles): 
	# Remove vehicles that reached destination
	for car in platoon[2:]:
		if not (car in allvehicles): # car not in simulation anymore
			platoon.remove(car)
			if car in settings.platoonedvehicles:        # shouldn't  be necessary, read below
					settings.platoonedvehicles.remove(car) 	# this is causing issues and it should not. Only started after I moved code to a function, come back to it
	


	if len(platoon) < 3: # no vehicles in platoon
		settings.platoons.remove(platoon)
		return -1
	
	if len(platoon) < 4: # only one vehicle in platoon
		make_unplatooned(platoon[2], accTau, accMinGap)
		settings.platoons.remove(platoon)
		return -1
			
	# Check to see lane divergence
	leader = platoon[2]
	curr_lane = traci.vehicle.getLaneID(leader)
	if (curr_lane != platoon[0]) and (curr_lane != platoon[1]) and (curr_lane[:-1] == platoon[1][:-1]):
		# the leader switched lanes within the same road segment, so remove it as leader
		platoon.remove(leader)
		make_unplatooned(leader, accTau, accMinGap)
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
	lane_check = False
	leading_check = True
	
	# checks whether the leading vehicle is still in the platoon
	if leading_check:
		index = 2;
		for car in platoon[3:]:
			index += 1;
			leading_temp = traci.vehicle.getLeader(car, 100) # gets the car ahead, up to 100m
			
			if leading_temp:
				curr_leading = leading_temp[0]
			else:
				curr_leading = None
			
			curr_lane = traci.vehicle.getLaneID(car)
			# checks leading vehicle but also whether it's this car's lane which changed -> if it has simply remove it
			if not (curr_leading in platoon) and (curr_lane != platoon[0]) and (curr_lane != platoon[1]):
				platoon.remove(car)
				make_unplatooned(car, accTau, accMinGap)
			
			# if the lane has not changed, it's the leader that has moved, so make this car the new leader of a new platoon
			if not (curr_leading in platoon) and ((curr_lane == platoon[0]) or (curr_lane == platoon[1])):
				traci.vehicle.setMinGap(car, accMinGap)
				traci.vehicle.setTau(car, accTau)
				if index >= len(platoon): # this is the last vehicle in platoon, so don't make a  new platoon
					traci.vehicle.setColor(car, (0,255,0,0))
					settings.platoonedvehicles.remove(car)
					break
				traci.vehicle.setColor(car, (0,255,255,0))
				new_platoon = platoon[0:1]
				new_platoon.append(car)
				for car2 in platoon[index:]: #add +1 to index,  move cars behind to this platoon to be processed after
					new_platoon.append(car2)
					traci.vehicle.setColor(car2, (255,255,255,0)) # Here we can use 255,255,255 to mark platoon splits
					platoon.remove(car2)
				settings.platoons.append(new_platoon)
				break
	
	# uses lane check to filter vehicles
	if lane_check:
			index = 2;
			for car in platoon[3:]: 
					index += 1;
					curr_lane = traci.vehicle.getLaneID(car)
					if (curr_lane != lane1) and (curr_lane != lane2) and (curr_lane[:-1] == platoon[1][:-1]): # vehicle just changed lane
					# car has switched lanes or reached a new road
							platoon.remove(car)
							make_unplatooned(car, accTau, accMinGap) # remove car and revert it to regular ACC
				
					elif (curr_lane != lane1) and (curr_lane != lane2) and (":" not in curr_lane): # vehicles are lagging behind or branched out, split platoon
						# car has switched lanes or reached a new road
							platoon.remove(car)
							settings.platoonedvehicles.remove(car)
							traci.vehicle.setMinGap(car, accMinGap)
							traci.vehicle.setTau(car, accTau)
							traci.vehicle.setColor(car, (0,255,255,0))
							
							leader_route = traci.vehicle.getRoute(car)
							next_lane = get_next_segment(leader_route, curr_lane[:-2])
							new_platoon = [curr_lane, get_next_segment(leader_route, curr_lane[:-2]) + curr_lane[(len(curr_lane)-2):]]
							new_platoon.append(car)
							for car2 in platoon[index+1:]: # move cars behind to this platoon to be processed after
								new_platoon.append(car2)
								traci.vehicle.setColor(car2, (255,255,255,0))
								platoon.remove(car2)
							settings.platoons.append(new_platoon)
							#settings.platoonleaderspeed.append() # no need for this, I believe
							break	
	# If platoon is gone, delete it
	if len(platoon) < 4:
		make_unplatooned(leader, accTau, accMinGap)
		settings.platoons.remove(platoon)
		return -1
	
	# make sure leader has correct parameters --> this should not be necessary, check back on code to see where bug is but it does fix it technically
	traci.vehicle.setMinGap(platoon[2], accMinGap)
	traci.vehicle.setTau(platoon[2], accTau)
	traci.vehicle.setColor(platoon[2], (0,255,255,0))
	return 0


################################################################################
# Create Platoons function
#   This function creates platoons in a given road segment and cycle time  
#   interval
################################################################################
def create_platoons(road, lane, start_range, end_range, accTau, accMinGap, targetTau, targetMinGap, programPointer):
	road_segment = road + lane;
	if (programPointer >= start_range and programPointer <= end_range):
		first = True # for leader in platoon
		cars = traci.lane.getLastStepVehicleIDs(road_segment) 
		platoon = [road_segment] 
		
		# iterate through cars in order of closest to last and check to see if ACC to add to platoon
		for car in cars[::-1]:			

			cartype = traci.vehicle.getTypeID(car)
			if ("CarA" in cartype): 
				if (car in settings.platoonedvehicles):	
					# If this vehicle is a leader, first do a check to see if car ahead can be the leader instead
					if (traci.vehicle.getColor(car) == (0,255,255,0)):
						leading_temp = traci.vehicle.getLeader(car, 100)
						# There is a vehicle ahead
						if leading_temp:
							type_alt = traci.vehicle.getTypeID(leading_temp[0])
							platoon_alt = get_platoon(leading_temp[0])
							if ("CarA" in type_alt) and (not platoon_alt): # no, the leading vehicle is not in a platoon, but it could be
								platoon_curr = get_platoon(car)

								if platoon_curr != None: #stupid bug where cars are technically platooned but not showing up in platoons variable
									platoon_curr.insert(2, leading_temp[0])
								make_platooned(car, targetTau, targetMinGap) # make it a regular follower, instead of a leader
								
								traci.vehicle.setColor(leading_temp[0], (0,255,255,0)) 	# set its color to cyan, signifying car leader
								first = False
								leader_route = traci.vehicle.getRoute(leading_temp[0]) # gets the route for the leading car
								settings.platoonedvehicles.append(leading_temp[0])
								continue
							
							if ("CarA" in type_alt) and (platoon_alt): # yes, the leading vehicle IS in a platoon, so we can merge
								platoon_curr = get_platoon(car) # get current platoon
								for veh_alt in platoon_curr[2::]: # iterate through vehicles in current platoon and add them to the platoon in front
									platoon_alt.append(veh_alt)
								make_platooned(car, targetTau, targetMinGap) # make it a regular follower, instead of a leader
								settings.platoons.remove(platoon_curr) # remove the platoon that merged with the one in front
								#traci.vehicle.setSpeed(car, target_speed)
								
								first = False
								leader_route = traci.vehicle.getRoute(platoon_alt[2]) # gets the route for the leading car
								continue
																			
					# Leading car is not a leader, so continue  
					if len(platoon) == 3: # if there was a single ACC vehicle
						make_unplatooned(platoon[2], accTau, accMinGap)
					if len(platoon) > 3: # if there were multiple ACC vehicles
						settings.platoons.append(platoon) # add the platoon
						platoon = [road_segment]
					first = True
					platoon = [road_segment]
					continue
								
				if first:
					# leading car maintains the same min gap and tau as before
					
					if car == cars[0]: # if we have a lone vehicle which is last in the lane, don't make it into a platoon
						continue
						
					# Checks if the car ahead is in a platoon it can join
					leading_temp = traci.vehicle.getLeader(car, 100)
					if leading_temp:
						platoon_alt = get_platoon(leading_temp[0])
						if platoon_alt: # yes, it can join a platoon
							platoon_alt.append(car)
							make_platooned(car, targetTau, targetMinGap)
							#traci.vehicle.setSpeed(car, target_speed)
							continue
			
						traci.vehicle.setColor(car, (0,255,255,0)) 	# set its color to cyan, signifying car leader
						#traci.vehicle.setSpeed(car, target_speed) 		# set its speed higher to help ease propogation delay	
						first = False
						leader_route = traci.vehicle.getRoute(car) # gets the route for the leading car
						platoon.append(get_next_segment(leader_route, road) + lane) # gets the leading car's next segment
						platoon.append(car)
						settings.platoonedvehicles.append(car)
				else:
					make_platooned(car, targetTau, targetMinGap)
					#traci.vehicle.setSpeed(car, target_speed) 			# set its speed higher to help ease propogation delay
					platoon.append(car)
					if car == cars[0]: # this platoon includes the last car on this segment
						settings.platoons.append(platoon) # add the platoon

			# if it is manual, stop making the platoon, since no cars behind can accelerate anyways
			else:
				if len(platoon) == 3: # if there was a single ACC vehicles
					make_unplatooned(platoon[2], accTau, accMinGap)
				if len(platoon) > 3: # if there were multiple ACC vehicles
					settings.platoons.append(platoon) # add the platoon
				first = True
				platoon = [road_segment]


################################################################################
# Get next segment function
#   Simply returns the next segment in a vehicles route  
################################################################################
def get_next_segment(leader_route, road_segment): 
		index = 0
		for segment in leader_route:
				index += 1
				if segment == road_segment:
						break
		if len(leader_route) > index:
				return leader_route[index]
		else:
				return "destination"

################################################################################
# Get platoon function
#   Returns the platoon the a vehicle belongs to  
################################################################################
def get_platoon(veh):
	for platoon in settings.platoons:
		if veh in platoon:
			return platoon
	return None

################################################################################
# Make Platooned function
#   Sets vehicle parameters to that of a following car in a platoon
################################################################################
def make_platooned(veh, targetTau, targetMinGap):
	traci.vehicle.setMinGap(veh, targetMinGap) 	# temporarily set its minimum gap
	traci.vehicle.setTau(veh, targetTau) 		# temporarily set its tau
	traci.vehicle.setColor(veh, (255,255,255,0)) 	# set its color to blue, signifying car follower
	traci.vehicle.setSpeedFactor(veh, 1.2) 	# allow it to speed up to close gaps
	if not (veh in settings.platoonedvehicles): # might be leader
			settings.platoonedvehicles.append(veh)
	

################################################################################
# Make Unplatooned function
#   Remove vehicles from being platooned
################################################################################
def make_unplatooned(veh, accTau, accMinGap):
	if veh in settings.platoonedvehicles: # shouldn't be necessary
		settings.platoonedvehicles.remove(veh)
	traci.vehicle.setMinGap(veh, accMinGap)
	traci.vehicle.setTau(veh, accTau)
	traci.vehicle.setColor(veh, (0,255,0,0))
	traci.vehicle.setSpeedFactor(veh, 1.0) 	# allow it to speed up to close gaps