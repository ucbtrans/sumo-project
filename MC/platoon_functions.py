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
# Updated 1/11/17 - Armin Askari
# -- fixed merging issues for platooning and splitting problems with leaders
# -- fixed issues with succestive platoons combining into one platoon
# -- fixed issues with platoon maintenance and cars changing routes
# -- realized the rate of platoon_comm should divide platoon_create
################################################################################



################################################################################
# Platoon Control function
#   This function controls the platoons and performs inter-vehicle communication
#   to prevent crashes
################################################################################
def platoon_control(accTau, accMinGap, targetTau, targetMinGap, platoon_comm,time):
	allvehicles = traci.vehicle.getIDList();


	# Go through and make sure all vehicles are still in simulation
	for veh in settings.platoonedvehicles:
		if not (veh in allvehicles): 
			settings.platoonedvehicles.remove(veh)
	
	index = -1
	
	merge_platoons(targetTau,targetMinGap)


	for platoon in settings.platoons:
		index += 1

		
		if platoon_maintenance(platoon, accTau, accMinGap, allvehicles,targetTau,targetMinGap,time) == -1:
			continue
		
		# Communication step
		leader = platoon[2]
		try:
			leader_accel = traci.vehicle.getAccel(leader)
			leader_speed = traci.vehicle.getSpeed(leader)
			if len(settings.platoonleaderspeed) > index: # if we are not in the first time step for this platoon
				leader_accel = (leader_speed - settings.platoonleaderspeed[index]) / (settings.step_length*platoon_comm)
			else:
				leader_accel = 0
			target_speed = traci.lane.getMaxSpeed(traci.vehicle.getLaneID(leader))
			
			if (leader_accel < -1.0) or (leader_speed < target_speed):
				for car in platoon[3:]: # go through all followers and have them slow down accordingly
					try:
						leading_temp = traci.vehicle.getLeader(car, 100)
						if leading_temp:
							dist = leading_temp[1]
						else:
							dist = 100
						if dist < leader_speed * targetTau: # if we're too close
								traci.vehicle.slowDown(car, leader_speed, settings.step_length*platoon_comm) # slows down the vehicle for the appropriate period
						continue
					except:
						print("no leader")
						continue
			continue
		except:
			print("no leader anymore")
			continue
	del settings.platoonleaderspeed[:] # clears the list
	for platoon in settings.platoons: # records the speed of all platoon leaders to calculate acceleration # records the speed of all platoon leaders to calculate acceleration
		try:
			settings.platoonleaderspeed.append(traci.vehicle.getSpeed(platoon[2]))
			continue
		except:
			print("platoon leader left simulation")
			continue


################################################################################
# Platoon Maintenance function
#   This function performs maintenance on platoons by removing vehicles from 
#   them for various reasons
################################################################################
def platoon_maintenance(platoon, accTau, accMinGap, allvehicles,targetTau,targetMinGap,time): 
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
		try:
			make_unplatooned(platoon[2], accTau, accMinGap)
			settings.platoons.remove(platoon)
		except:
			print("one vehicle in platoon left simulation")
		return -1
			
	# Check to see lane divergence
	leader = platoon[2]

	try:
		curr_lane = traci.vehicle.getLaneID(leader) #if in middle of intersection, will give random numbers
		if (curr_lane != platoon[0]) and (curr_lane != platoon[1]) and (curr_lane[:-1] == platoon[1][:-1]):
			# the leader switched lanes within the same road segment, so remove it as leader
			platoon.remove(leader)
			make_unplatooned(leader, accTau, accMinGap)
			# Configure the new leader
			leader = platoon[2]
			curr_lane = traci.vehicle.getLaneID(leader)
			make_leader(leader,accTau,accMinGap)

		
		if (curr_lane != platoon[0]) and (curr_lane != platoon[1]) and (":" not in curr_lane):
			# our leader has moved on to a new lane.
			platoon[0] = platoon[1];
			platoon[1] = curr_lane
	except: 
		print("leader left simulation")
		pdb.set_trace()
	
	lane1 = platoon[0]; lane2 = platoon[1];
	
	# Go through follower vehicles
	lane_check = False
	leading_check = True
	flag = False

	
	# checks whether the leading vehicle is still in the platoon
	if leading_check:
		remove_counter = 0
		index = 2;
		for car in platoon[3:]:
			index += 1;

			try:
				leading_temp = traci.vehicle.getLeader(car, 100) # gets the car ahead, up to 100m
				
				
				if leading_temp:
					curr_leading = leading_temp[0]
				else:
					curr_leading = None
				
				curr_lane = traci.vehicle.getLaneID(car)
				# checks leading vehicle but also whether it's this car's lane which changed -> if it has simply remove it
				if not (curr_leading in platoon) and (curr_lane != platoon[0]) and (curr_lane != platoon[1]):
					remove_counter += 1
					platoon.remove(car)
					make_unplatooned(car, accTau, accMinGap)

					# make_leader(car,accTau,accMinGap)

					# new_platoon = platoon[1:2] #should be just platoon[1], but platoon[1:2] makes it an array
					# new_route = traci.vehicle.getRoute(car) # gets the route for the leading car
					# road,lane = get_RoadLane(traci.vehicle.getLaneID(car))
					# new_platoon.append(get_next_segment(new_route, road)) # gets the leading car's next segment
					# new_platoon.append(car)
					for car2 in platoon[index+1-remove_counter:]: #add +1 to index,  move cars behind to this platoon to be processed after
						#new_platoon.append(car2)
						#traci.vehicle.setColor(car2, (255,255,255,0)) # Here we can use 255,255,255 to mark platoon splits
						make_unplatooned(car2,accTau,accMinGap)
						platoon.remove(car2)
					#settings.platoons.append(new_platoon)
					break
				
				# if the lane has not changed, it's the leader that has moved, so make this car the new leader of a new platoon if there are
				# more vehicles behind it
				if not (curr_leading in platoon) and ((curr_lane == platoon[0]) or (curr_lane == platoon[1])):
					remove_counter += 1
					platoon.remove(car)
					
					make_leader(car,accTau,accMinGap)

					if index == 3 and curr_leading == None: #the leader changed route, so remove it from platoon 
						make_unplatooned(platoon[2],accTau,accMinGap)
						flag = True


					if index+1 >= len(platoon) + remove_counter: # this is the last vehicle in platoon, so don't make a  new platoon
						traci.vehicle.setColor(car, (0,255,0,0))
						if car in settings.platoonedvehicles:
							settings.platoonedvehicles.remove(car)
						if len(platoon) == 4: #last vehicle in platoon, so make the leader normal
							make_unplatooned(platoon[2],accTau,accMinGap)
						break

					new_platoon = platoon[0:1]
					new_route = traci.vehicle.getRoute(car) # gets the route for the leading car
					road,lane = get_RoadLane(traci.vehicle.getLaneID(car))
					new_platoon.append(get_next_segment(new_route, road)) # gets the leading car's next segment
					new_platoon.append(car)
					for car2 in platoon[index+1-remove_counter:]: #add +1 to index,  move cars behind to this platoon to be processed after
						new_platoon.append(car2)
						#traci.vehicle.setColor(car2, (255,255,255,0)) # Here we can use 255,255,255 to mark platoon splits
						make_platooned(car2,targetTau,targetMinGap)
						platoon.remove(car2)
					settings.platoons.append(new_platoon)
					break
				continue #everything normal
			except:
				print("car not in simulation anymore")
				pdb.set_trace()
				continue

		if flag:
			platoon.remove(platoon[2])
			flag = False

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
								print 'CANT POSSIBLY BE HERE'
								platoon.remove(car2)
							settings.platoons.append(new_platoon)
							#settings.platoonleaderspeed.append() # no need for this, I believe
							break	
	# If platoon is gone, delete it
	if len(platoon) < 4:
		try:
			make_unplatooned(leader, accTau, accMinGap)
			settings.platoons.remove(platoon)
			return -1
		except:
			return -1
	
	# make sure leader has correct parameters --> this should not be necessary, check back on code to see where bug is but it does fix it technically
	try:
		make_leader(platoon[2],accTau,accMinGap)
	except:
		print("leader correct parameters")
	return -1


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

			# if 'veh2470' == car: #t =1306, platooning creation error somewhere
			# 	pdb.set_trace()

			# if 'veh282' in car: #veh765' in car:
			# 	aa = ['veh282' in a for a in settings.platoons]
			# 	print (True in aa)
			# 	pdb.set_trace() 

			cartype = traci.vehicle.getTypeID(car)
			if ("CarA" in cartype) or ("CarIIDM" in cartype): 
				if (car in settings.platoonedvehicles):	
					# If this vehicle is a leader, first do a check to see if
					# car ahead can be the leader instead
					if get_platoon(car): #car already in a platoon, don't need to do anything except check 
										 #if platoon infront you can join
						if car == cars[-1]: #first car in line, nothing you can join (if not here, itll loop and make a
											# a cylical platoon)
							continue
						else:
							if traci.vehicle.getColor(car) == (0,255,255,0): #you're a leader
								car_array = cars[::-1]
								front_car = car_array[car_array.index(car)-1]
								front_pltn = get_platoon(front_car)
								ff = traci.vehicle.getLeader(car)
								dist = ff[1]

								if front_pltn and dist <= 70: #if car infront is part of a platoon and within 70m, join in
									behind_pltn = get_platoon(car)
									
									for car_pltnB in behind_pltn[2:]:
										make_platooned(car_pltnB,targetTau,targetMinGap)
										front_pltn.append(car_pltnB) #add the trailing platoon vehicles to the front one

									settings.platoons.remove(behind_pltn) #get rid of the trailing platoon
									continue
							else: #you're a follower
								continue

					if (traci.vehicle.getColor(car) == (0,255,255,0)):
						leading_temp = traci.vehicle.getLeader(car, 100)
						# There is a vehicle ahead
						if leading_temp:
							type_alt = traci.vehicle.getTypeID(leading_temp[0])
							platoon_alt = get_platoon(leading_temp[0])
							if (("CarA" in type_alt) or ("CarIIDM" in type_alt)) and (not platoon_alt) and (leading_temp[1] <= 70): # no, the leading vehicle is not in a platoon, but it could be and within 70m
								platoon_curr = get_platoon(car)

								if platoon_curr != None: #stupid bug where cars are technically platooned but not showing up in platoons variable
									platoon_curr.insert(2, leading_temp[0])
								make_platooned(car, targetTau, targetMinGap) # make it a regular follower, instead of a leader
								
								make_leader(leading_temp[0],accTau,accMinGap)

								first = False
								leader_route = traci.vehicle.getRoute(leading_temp[0]) # gets the route for the leading car
								settings.platoonedvehicles.append(leading_temp[0])
								continue
							
							if (("CarA" in type_alt) or ("CarIIDM" in type_alt)) and (platoon_alt) and (leading_temp[1] <= 70): # yes, the leading vehicle IS in a platoon, so we can merge and within 70m
								platoon_curr = get_platoon(car) # get current platoon
								if platoon_curr != None:
									for veh_alt in platoon_curr[2::]: # iterate through vehicles in current platoon and add them to the platoon in front
										platoon_alt.append(veh_alt)
								make_platooned(car, targetTau, targetMinGap) # make it a regular follower, instead of a leader

								if platoon_curr != None:
									settings.platoons.remove(platoon_curr) # remove the platoon that merged with the one in front
								#traci.vehicle.setSpeed(car, target_speed)
								
								first = False
								try:
									leader_route = traci.vehicle.getRoute(platoon_alt[2]) # gets the route for the leading car
									continue
								except:
									print("no leader anymore")
									pdb.set_trace()
									continue
								continue
							else:
								continue

					if (traci.vehicle.getColor(car) == (255,255,255,0)): #if already a follower
						follower_pltn = get_platoon(car)
						leading_temp = traci.vehicle.getLeader(car, 100)
						if leading_temp:
							type_alt = traci.vehicle.getTypeID(leading_temp[0]) 

							if follower_pltn and (leading_temp[1] <= 70) and \
							(("CarA" in type_alt) or ("CarIIDM" in type_alt)): #car belongs to another platoon, but changed lanes so can be part of another one
								platoon.append(car)
								follower_pltn.remove(car)
								if len(platoon) == 3:
									make_leader(car)
						else: #its a follower but not part of a platoon (bug catcher b/c not possible)
							platoon.append(car)

																			
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
					# Checks if the car ahead is in a platoon it can join
					leading_temp = traci.vehicle.getLeader(car, 100)

					# if car == cars[0] and leading_temp: #
					# 	if (leading_temp[1] > 70):# if we have a vehicle which is last in the lane and car infront too far
					# 	                         # don't make it into a platoon
					# 		continue
					# 	else:

						
					if leading_temp: # and (leading_temp[0] not in settings.platoonedvehicles): #if there is a platoonable car infront, that becomes the leader and u become follower
							platoon_alt = get_platoon(leading_temp[0])
							if platoon_alt and (leading_temp[1] <= 70): # yes, it can join a platoon and within 70m
								platoon_alt.append(car)
								make_platooned(car, targetTau, targetMinGap)
								#traci.vehicle.setSpeed(car, target_speed)
								continue
					# elif leading_temp and (leading_temp[0] in settings.platoonedvehicles): #car infront is in a platoon, giddy up 
					# 	make_platooned(car,targetTau,targetMinGap)
					# 	platoon_alt = get_platoon()

					if car == cars[0]: # and (not leading_temp): #vehicle at end, with no one infront - don't make platoon
						continue

					car_array = cars[::-1]
					behind_car = car_array[car_array.index(car)+1]

					if get_platoon(behind_car): #if the next car is in a platoon, add that platoon to the front car
						first = True
						platoon_alt = get_platoon(behind_car)

						lead_platoon_alt = platoon_alt[2]
						try:
							ff = traci.vehicle.getLeader(lead_platoon_alt,100)
							dist = ff[1]
						except:
							#pdb.set_trace() #IIDM 75, time 240 #DEBUG HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE#################################################
							continue

						if dist <= 70: #platoon is within 70m of the front vehicle, so mere

							make_leader(car,accTau,accMinGap)
							leader_route = traci.vehicle.getRoute(car) # gets the route for the leading car
							platoon.append(get_next_segment(leader_route, road) + lane) # gets the leading car's next segment
							platoon.append(car)


							for cars_pltnB in platoon_alt[2:]:
								try:
									platoon.append(cars_pltnB)
									make_platooned(cars_pltnB,targetTau,targetMinGap)
								except:
									print ("follower left simulation")
							settings.platoons.remove(platoon_alt)	

							settings.platoons.append(platoon)
							platoon = [road_segment]
							continue
						else: #shouldnt continue platoon formation
							continue

					else: #not in platoon, so acc too far or manual - do regular formation 
						make_leader(car,accTau,accMinGap)
						#traci.vehicle.setSpeed(car, target_speed) 		# set its speed higher to help ease propogation delay	

						leader_route = traci.vehicle.getRoute(car) # gets the route for the leading car
						platoon.append(get_next_segment(leader_route, road) + lane) # gets the leading car's next segment
						platoon.append(car)
						first = False

				else:
					leading_temp = traci.vehicle.getLeader(car, 100)
					if leading_temp[1] <= 70 and (traci.vehicle.getColor(leading_temp[0]) == (255,255,255,0) or\
					traci.vehicle.getColor(leading_temp[0]) == (0,255,255,0)): #if within 70m to make platoon, and the car infront is follower
																			   #or leader
						make_platooned(car, targetTau, targetMinGap)

						platoon_infront = get_platoon(leading_temp[0])
						if platoon_infront: #this is if a legit platoon exists infront, if not a platoon is being formed
							platoon_infront.append(car)
							continue
						else: #forming new platoon
							#traci.vehicle.setSpeed(car, target_speed) 			# set its speed higher to help ease propogation delay
							platoon.append(car)
							if car == cars[0]: # this platoon includes the last car on this segment
								settings.platoons.append(platoon) # add the platoon
							else: #theres more cars
								car_array = cars[::-1]
								behind_car = car_array[car_array.index(car)+1]
								if get_platoon(behind_car): #if the next car is in a platoon - just end platoon formation here
														  #later the merge platoon function will take care of making them 1 platoon
									first = True
									
									if len(platoon) == 3: #no platoon, just 1 car
										make_unplatooned(platoon[2],accTau,accMinGap)
										platoon = [road_segment]
										continue

									settings.platoons.append(platoon)
									platoon = [road_segment]
								else: #not in platoon, so regular acc or manual
									continue #since if either, platoon formation continues or gets halted by else case at bottom

					else: #the car cannot join the platoon because too far, so stop the platoon formation here and start another one
						if len(platoon) == 3: # if there was a single ACC vehicles
							make_unplatooned(platoon[2], accTau, accMinGap)
						if len(platoon) > 3: # if there were multiple ACC vehicles
							settings.platoons.append(platoon) # add the platoon
						first = True
 	
						if car != cars[0]: #its not the last car so we can still try to make platoons, else we're done
							platoon = [road_segment]
							make_leader(car,accTau,accMinGap)

							leader_route = traci.vehicle.getRoute(car) # gets the route for the leading car
							platoon.append(get_next_segment(leader_route, road) + lane) # gets the leading car's next segment
							platoon.append(car)
							first = False

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
# Merge platoons function
#   Combines two platoons if they happen to be on the same road together
#	--covers a bug where you can have two platoons beside each other with
#   --one car that overlaps between the platoons BUT there is no manual
#	--vehicle inbetween preventing the formation of one large platoon  
################################################################################
def merge_platoons(targetTau,targetMinGap):
	idxs = []
	for i in range(len(settings.platoons)):
		for j in range(i+1,len(settings.platoons)):
			platoon1 = settings.platoons[i]
			platoon2 = settings.platoons[j]
			# if  (platoon1[0] == platoon2[0]) and (platoon1[1] == platoon2[1]) and \
			# (i != j):

			if (i!=j):
				try:
					if (platoon1[-1] == platoon2[2]): #last car of platoon1 == first car of platoon2
						idxs.append([i,j])
					if (platoon1[2] == platoon2[-1]):
						idxs.append([j,i])
				except:
					#pdb.set_trace()
					print "platoon error somewhere"


	try:
		for k in idxs:
			idx1 = k[0]
			idx2 = k[1]
			platoon2_veh = settings.platoons[idx2][3:]
			settings.platoons[idx1].extend(platoon2_veh)
			make_platooned(settings.platoons[idx2][2],targetTau,targetMinGap)
	except:
		print "middle man car has left simulation"

	try:
		for l in idxs:
			idx1 = l[0]
			del settings.platoons[idx1]
	except:
		print "index out of range"



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
	traci.vehicle.setType(veh,'CarIIDM')
	traci.vehicle.setMinGap(veh, targetMinGap) 	# temporarily set its minimum gap
	traci.vehicle.setTau(veh, targetTau) 		# temporarily set its tau
	traci.vehicle.setColor(veh, (255,255,255,0)) 	# set its color to white, signifying car follower
	traci.vehicle.setSpeedFactor(veh, 1.5) 	# allow it to speed up to close gaps

	if not (veh in settings.platoonedvehicles): # might be leader
			settings.platoonedvehicles.append(veh)
	#traci.vehicle.setVehicleClass(veh,"IIDM")
	
	

################################################################################
# Make Unplatooned function
#   Remove vehicles from being platooned
################################################################################
def make_unplatooned(veh, accTau, accMinGap):
	if veh in settings.platoonedvehicles: # shouldn't be necessary
		settings.platoonedvehicles.remove(veh)

	traci.vehicle.setType(veh,'CarA')
	traci.vehicle.setMinGap(veh, accMinGap)
	traci.vehicle.setTau(veh, accTau)
	traci.vehicle.setColor(veh, (0,255,0,0))
	traci.vehicle.setSpeedFactor(veh, 1.0) 	

################################################################################
# Make Leader function
#   Make platoon leaders (same parameters as ACC vehicles but cyan color)
################################################################################
def make_leader(veh,accTau,accMinGap):
	traci.vehicle.setType(veh,'CarA')
	traci.vehicle.setMinGap(veh, accMinGap)
	traci.vehicle.setTau(veh, accTau)
	traci.vehicle.setColor(veh, (0,255,255,0))
	traci.vehicle.setSpeedFactor(veh, 1.0) 
	if not (veh in settings.platoonedvehicles): # might be leader
			settings.platoonedvehicles.append(veh)	



################################################################################
# get_RoadLane function
#   Get the road and lane that a car is on
################################################################################
def get_RoadLane(path):
	road,lane = path.split('_')
	return road,lane 

