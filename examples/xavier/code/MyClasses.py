"""
@Author Xavier Lavenir
@Title Final Year Project
@Institution - University of California, Berkeley
@Date - 2015-2016
"""

from __future__ import division
import os
import sys
import constants
import random
from pandas import DataFrame
import shutil

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
from enum import Enum
import xml.etree.ElementTree as ET
import math

class Platoon:
	#Class variables, default values
	_vehicleList = [] #elements are of type 'Vehicle'
	_id = ""
	_headway = 0.1#[m]
	_platoonDesSpeed = 12 #[m/s]
	_baseRoute =[]
	_edgeList = []
	_laneList = []

	#Access to classVariables
	def GetVehicleList(self):
		return self._vehicleList

	def SetVehicleList(self, vehicleList):
		self._vehicleList = vehicleList

	def GetID(self):
		return self._id

	def SetHeadway(self, headway):
		self._headway = headway

	def GetHeadway(self):
		return self._headway

	def SetHeadway(self, speed):
		self._platoonDesSpeed = speed

	def GetPlatoonDesSpeed(self):
		return self._platoonDesSpeed

	def GetPosition(self):
		#Return the position of the lead vehicle
		#Notes: assumes tat the vehicle list is ordered
		if(len(self._vehicleList)>0):
			return self._vehicleList[0].GetPosition()
		else:
			return None

	def GetBaseRoute(self):
		return self._baseRoute

	def SetBaseRoute(self, newBaseRoute):
		self._baseRoute = newBaseRoute

	def Count(self):
		return len(self._vehicleList)

	def GetVehicleListID(self):
		theList = []
		for k in range(0, len(self._vehicleList)):
			theList.append(self._vehicleList[k].GetID())

		return theList

	#Constructor
	def __init__(self, platoonID):
		#Provides an id for the platoon
		self._id = platoonID
		#Resets the class
		self._vehicleList = []
		self._baseRoute =[]
		self._getEdgeIDList()
		self._laneList = traci.lane.getIDList() #*This contains internal lanes...

	#Methods
	def Add(self, veh):
		self._vehicleList.append(veh)#Adds the car to the platoon
		veh.AddToPlatoon(self._id,len(self._vehicleList)-1)

	def GetLeaderID(self):
		return _vehicleList[0].GetID()

	def Remove(self, veh):
		self._vehicleList.remove(veh)#Removes the car from the platoon
		veh.RemoveFromPlatoon()

	def Update(self):
		#Update
		self.UpdatePlatoonOrder()#Makes sure they are in order
		self.UpdateBaseRoute()#Updates the platoon route
		self.UpdateVehicleLaneDynamics()#Make sure they are on the correct lanes
		self.CheckRemovalVehicle()#Removes vehicle from the platoon if need be
		self.CheckPlatoonIntruders()
		self.UpdateVehicles()

	def UpdateVehicles(self):
		for v in self._vehicleList:
			v.Update()

	def _determineLeadVehicle(self, veh1, veh2): #Certified
		#Returns the id of the lead vehicle or None otherwise, returns none if at a junction
		#Returns 1 if first vehicle, 2 if second, 0 if undertermined, None if not relevant
		
		#Gets the ID's of the vehicles
		vehID1 = veh1.GetID()
		vehID2 = veh2.GetID()

		#Stores the roads the vehicles are on
		Road1 = traci.vehicle.getRoadID(vehID1)#This could say it's at a junction
		Road2 = traci.vehicle.getRoadID(vehID2)#Ditto
		Route1 = traci.vehicle.getRoute(vehID1)
		Route2 = traci.vehicle.getRoute(vehID2)

		#First determines if each vehicle is on it's own route or if it's @ a junction
		if ((Road1 in Route1) and (Road2 in Route2)):
			#Checks if they are both on the same edge
			if (Road1 == Road2):
				return (1 if (traci.vehicle.getLanePosition(vehID1) > traci.vehicle.getLanePosition(vehID2)) else 2)
			else:
				#The vehicles are on different edges --> check which one is ahead
				#Assume vehicle 1 is ahead and if it isn't then return the other
				if (Road1 in Route2):
					ind1 = Route2.index(Road1)
					ind2 = Route2.index(Road2)
					return (1 if (ind1>ind2) else 2)
				elif(Road2 in Route1):
					ind1 = Route1.index(Road1)
					ind2 = Route1.index(Road2)
					return (1 if (ind1>ind2) else 2)
				else:
					raise ValueError('They should not be in the same platoon')
					return None
			return 0
		else:
			#The routes just before the ineterection
			R1 = Route1[traci.vehicle.getRouteIndex(vehID1)]
			R2 = Route2[traci.vehicle.getRouteIndex(vehID2)]

			if((Road1 not in Route1) and (Road2 not in Route2)):#both at intersections
				if(R1 == R2):
					return (1 if (traci.vehicle.getLanePosition(vehID1) > traci.vehicle.getLanePosition(vehID2)) else 2)
				else:
					return self._determineLeadeHelper(Route1,Route2,R1,R2)
			elif(Road1 not in Route1):#Veh 1 is at the intersection
				return (1 if (R1 == R2) else self._determineLeadeHelper(Route1,Route2,R1,R2))
			else:#Veh 2 is at the intersection
				return(2 if (R1 == R2) else self._determineLeadeHelper(Route1,Route2,R1,R2))

	def _determineLeadeHelper(self, Route1, Route2, R1, R2):
		if (R1 in Route2):
			return (1 if (Route2.index(R1)>Route2.index(R2)) else 2)
		elif (R2 in Route1):
			return (1 if (Route1.index(R1)>Route1.index(R2)) else 2)
		else:
			raise ValueError('They should not be in the same platoon')
			return None

	def UpdatePlatoonOrder(self):#Works but may be inneficient
		#Updates the position of each vehicle within the platoon
		
		i = 0
		while i < len(self._vehicleList) - 1:#Loops through all vehicles in platoon
			rank = self._determineLeadVehicle(self._vehicleList[i],self._vehicleList[i+1])#Compares the two first vehicles
			
			if(rank == 2):#If the second vehicle is in front
				#Swap the order of the vehicles
				tempVeh = self._vehicleList[i]
				self._vehicleList[i] = self._vehicleList[i+1]
				self._vehicleList[i+1] = tempVeh
				i = 0 #Restart the looping.. this may be inneficient
			else:
				#Itterate
				i+=1

		#Re-itterates and numbers the position of each vehicle
		j = 0
		while j < len(self._vehicleList):
			self._vehicleList[j].SetPosition(j)
			#print str(self._vehicleList[j].GetID()) + ': ' + str(self._vehicleList[j].GetPosition())
			j+=1

	def PrintPlatoon(self):

		word = self.GetID() + ":"
		for i in range(0,len(self._vehicleList)):
			word += self._vehicleList[i].GetID() + ' - '

		print word

	def UpdateBaseRoute(self):
		#This updates the base route of the platoon. Should be updated everytime a platoon
		# is created or when a vehicle is added/removed

		#Assumes that the _vehicleList is ordered
		vid = self._vehicleList[len(self._vehicleList)-1].GetID()

		#New test
		ind = traci.vehicle.getRouteIndex(vid)
		R = traci.vehicle.getRoute(vid)

		for i in range(ind, len(R)):
			valid = True
			commonEdge = R[i]

			for j in range(0,len(self._vehicleList)-1):
				if(commonEdge not in traci.vehicle.getRoute(self._vehicleList[j].GetID())):
					valid = False
					break
			if(valid):
				break

		#This is the most recent common edge they share (the last vehicle is on it)
		#commonEdge = traci.vehicle.getRoadID(self._vehicleList[len(self._vehicleList)-1].GetID())
		newBaseRoute = [commonEdge]#The first common road... Make sure it's not a junction
		newListVeh = self._vehicleList

		#We assume that the routes of all vehicles in the platoon contains the baseRoute
		#Loop through all of the vehicles within the platoon
		ex = False

		j = 1#Continues looping until is has found a route which two vehicles are taking
		while(len(newListVeh) > 1 and ex == False):
			
			i = 0#Loops through all of the vehicles
			myNewList = []
			while i < len(newListVeh):
				R = traci.vehicle.getRoute(newListVeh[i].GetID())#Get the route of veh i
				edgeIndex = R.index(newBaseRoute[0])+j #Get the edge index within veh i's route
	
				#If the curr veh has no more edges, get rid of it
				if(edgeIndex >= len(R)):
					ex = True
					i+=1
					break
				#get the name of the edge
				e = R[edgeIndex]
				#Creates a list of edges and the number of vehicles
				# travelling along the edges in the next 'step'

				#Adds the vehicle to the list
				if(len(myNewList)>0):
					if (e in myNewList[0]) == False:
						myNewList[0].append(e)
						
						#Adds the vehicle to the correct list
						myNewList.append([newListVeh[i]])
					else:
						#Adds the vehicle to the correct list
						myNewList[myNewList[0].index(e)+1].append(newListVeh[i])
				else:
					myNewList.append([e])
					#Adds the vehicle to the correct list
					myNewList.append([newListVeh[i]])

				i+=1#iterate
			
			if(len(myNewList) < 1):
				break

			#default value for the index of the edge with the most vehicles
			maxI = [-1]	
			m = 0
			
			#print myNewList

			#Determines which is the longest list
			for k in range(0,len(myNewList[0])):
				if(len(myNewList[k+1])>m):
					maxI = [k]
					m = len(myNewList[k+1])
				elif (len(myNewList[k+1]) == m):
					oldMaxI = maxI
					maxI = [oldMaxI, k]

			if(m < 1):
				print 'm less than 1'
				break

			#If there are equally many vehicles travelling on some path, 
			#then we need to look deeper and see how many are follow the next
			if(len(maxI) == 1):
				newBaseRoute.append(myNewList[0][maxI[0]])
				newListVeh = myNewList[maxI[0]+1]
				#print newListVeh
			else:
				'ERROR - HAVE NOT PROGRAMMED THIS YET'

			j+=1

		self.SetBaseRoute(newBaseRoute)#Update base route


	def PrintPlatoonVehicleInfo(self):
		word = ""
		for i in range(0,len(self._vehicleList)):
			word += str(traci.vehicle.getSpeed(self._vehicleList[i].GetID())) + ' - '

		print word	

	def RemoveVehicle(self, veh):
		for v in self._vehicleList:
			if v == veh:
				self._vehicleList.remove(v)

	def CheckRemovalVehicle(self):
		#Checks if the upcoming platoon edge is the same as it's own. 
		#If not then checks how long before it reaches end of lane. If it's less than a certain distance, it leaves the platoon

		#This case is when a vehicle has a different course then the platoon
		for v in self._vehicleList:
			vid = v.GetID()
			R = traci.vehicle.getRoute(vid)
			i = traci.vehicle.getRouteIndex(vid)
			distance = 0
			buff = False

			if(traci.vehicle.getRoadID(vid) == R[i]):#If the vehicle is on a road and not at a junction
				distance += traci.lane.getLength(R[i] + "_0") - traci.vehicle.getLanePosition(vid)

			while(i+1 < len(R)):#If it's not on the last edge of the route
				buff = True
				nextEdge =R[i+1]
				if(nextEdge not in self.GetBaseRoute()):
					break
				else:
					distance+=traci.lane.getLength(nextEdge + '_0')
					if(distance > constants.CONST_EXIT_PLATOON_BUFFER):#If it's already bigger, don't waste time looping
						break
					i+=1

			if(distance < constants.CONST_EXIT_PLATOON_BUFFER and buff):
				#Remove the vehicle from the platoon
				self.Remove(v)

		#If the gap between vehicles becomes too large, split the platoon at that gap.
		for i in range(1,len(self._vehicleList)):
			#ASSUMES IN ORDER

			#Vehicles 
			veh1 = self._vehicleList[i-1]
			veh2 = self._vehicleList[i]
			vid1 = veh1.GetID()
			vid2 = veh2.GetID()

			#routes of the subsequent vehicles & #index of the edge which the vehicle is on within its routs
			Ro1 = traci.vehicle.getRoute(vid1)
			ind1 = traci.vehicle.getRouteIndex(vid1)
			Ro2 = traci.vehicle.getRoute(vid2)
			ind2 = traci.vehicle.getRouteIndex(vid2)

			splitDistance = 0#Distance between two vehicles
			
			#If on the same edge -->Ignores fact they may be at a junction (Assumes that the junction length is negligible)
			if(Ro1[ind1] == Ro2[ind2]):
				splitDistance = traci.vehicle.getLanePosition(vid1) -  traci.vehicle.getLanePosition(vid2)
			else:#If not on the same edge
				#If the second vehicle won't eventuaally be on the leaders edge, then skip them!
				if(Ro1[ind1] not in Ro2):
					continue

				for j in range(ind2,Ro2.index(Ro1[ind1])):
					splitDistance += traci.lane.getLength(Ro2[j] + "_0")

				#Need to consider the case where one of the vehicles is at a junction
				
				if(traci.vehicle.getRoadID(vid2)==Ro2[ind2]):#Not at junction
					splitDistance-=traci.vehicle.getLanePosition(vid2)
				else:#At junction
					splitDistance-=traci.lane.getLength(Ro2[ind2] + "_0")

				if(traci.vehicle.getRoadID(vid1)==Ro1[ind1]):
					splitDistance+=traci.vehicle.getLanePosition(vid1)


			if(splitDistance > constants.CONST_SPLIT_DISTANCE):
				#May be a better way to do this but I just remove all subsequent vehicles from the platoon
				#print 'Platoon Split (' + self.GetID() + '), distance = ' + str(splitDistance) + ' between ' + vid1 + ' and ' + vid2

				#Keeps the first i vehicles
				while(i<len(self._vehicleList)):
					self.Remove(self._vehicleList[i])

				break;

	def UpdateVehicleSpeedDynamics(self):
		if(len(self._vehicleList) <1):
			return

		#Limits the speed of the leader vehicle to the platoon speed
		if(traci.vehicle.getSpeed(self._vehicleList[0].GetID()) > self._platoonDesSpeed):
			traci.vehicle.setSpeed(self._vehicleList[0].GetID(), self._platoonDesSpeed)

		if(len(self._vehicleList)>1):
			#Update the second cars speed to get a fixed distance from the second car
			K = 0.1
			
			for j in range(1,len(self._vehicleList)):
				lead = traci.vehicle.getLeader(self._vehicleList[j].GetID())
				if(lead != None):

					if (traci.vehicle.getSpeed(self._vehicleList[j-1].GetID()) != 0):
						#print 'update'
						speed =  traci.vehicle.getSpeed(self._vehicleList[j-1].GetID()) + K*(lead[1]-self._headway)

						#Makes sure the speed does't exceed the speed limit
						speedLim  = traci.lane.getMaxSpeed(traci.vehicle.getRoadID(self._vehicleList[j-1].GetID()) + "_0")
						if(speed>speedLim):
							speed = speedLim

						traci.vehicle.setSpeed(self._vehicleList[j].GetID(), speed)

						#If the vehicle is deccelerating then match it
						leadVAccel = traci.vehicle.getAccel(self._vehicleList[j-1].GetID())
						if(traci.vehicle.getAccel(self._vehicleList[j-1].GetID()) < 0 or traci.vehicle.getAccel(self._vehicleList[j].GetID())<0):
							print "ERROROOOROOR	"
				else:
					#The vehicle follows the previous speed until is is given a new speed--?if the leader is out of sight, start the car model again
					traci.vehicle.setSpeed(self._vehicleList[j].GetID(), -1)

	def printSpeeds(self):
		word = ""
		for i in range(0,len(self._vehicleList)):
			word += self._vehicleList[i].GetID() + ": " + str(traci.vehicle.getSpeed(self._vehicleList[i].GetID())) + ' - '
		print word

	def printAccelss(self):
		word = ""
		for i in range(0,len(self._vehicleList)):
			word += self._vehicleList[i].GetID() + ": " + str(traci.vehicle.getAccel(self._vehicleList[i].GetID())) + ' - '
		print word

	def UpdateVehicleLaneDynamics(self):
		#All of the follower vehicles should just follow the leader vehicle
		#Ensures all of the vehicles are on the same lane as the one in front
		#If we have the junction id, can we predict which road it's going to?
		
		for i in range(1,len(self._vehicleList)):
			#Road id's
			vid1 = self._vehicleList[i-1].GetID()
			vid2 = self._vehicleList[i].GetID()
			RJ1 = traci.vehicle.getRoadID(vid1)#Could return junction
			RJ2 = traci.vehicle.getRoadID(vid2)#Could return junction

			#This is a more secure way of determining the road ID
			Ro1 = traci.vehicle.getRoute(vid1)
			Ro2 = traci.vehicle.getRoute(vid2)
			ind1 = traci.vehicle.getRouteIndex(vid1)
			ind2 = traci.vehicle.getRouteIndex(vid2)
			
			case = -1
			if(RJ1 not in self._edgeList and RJ2 not in self._edgeList):#Both at junction
				case = 0
			elif(RJ1 not in self._edgeList and RJ2 in self._edgeList):#1 at junction
				case = 1
			elif(RJ1 in self._edgeList and RJ2 not in self._edgeList):#2 at junction
				case = 2# If the follower is at a junction, make it adjust to the right lane
				#print 'Name: ' + self._vehicleList[i].GetID() + ', curr edge: ' + RJ2 +', currLaneIndex: ' + str(traci.vehicle.getLaneIndex(self._vehicleList[i].GetID())) + ', Total lanes: ' + str(self.GetNumberOfLanes(RJ2))
				#myInd = traci.getLaneIndex(self._vehicleList[i].GetID())
				#An error was being thrown where if a vehicle was at junction between two edges, it would sometime think that the vehicle was at the prior edge
				#and not at the junction... weird glitch --> I think it is because a bit of the vehicle is still on the edge so i added a condition where it had to be past the edge
				#if(traci.vehicle.getLanePosition(vid2) > 1.5*traci.vehicle.getLength(vid2)):
				#	traci.vehicle.changeLane(self._vehicleList[i].GetID(), traci.vehicle.getLaneIndex(self._vehicleList[i-1].GetID()), constants.CONST_LANE_CHANGE_DURATION)
					#print 'Name: ' + self._vehicleList[i].GetID() + ', curr edge: ' + RJ2 +', currLaneIndex: ' + str(traci.vehicle.getLaneIndex(self._vehicleList[i].GetID())) + ', Total lanes: ' + str(self.GetNumberOfLanes(RJ2))

				#print traci.vehicle.getLaneIndex(self._vehicleList[i].GetID())
			elif(RJ1 in self._edgeList and RJ2 in self._edgeList):#neither at junction
				case = 3
				#2 cases, on same road or not on same road
				#Gets the lanes that the vehicle is on regardless of the edge
				L1 = traci.vehicle.getLaneIndex(self._vehicleList[i-1].GetID())
				L2 = traci.vehicle.getLaneIndex(self._vehicleList[i].GetID())

				if(RJ1 == RJ2):#On the same edge
					if(L1 != L2):#May need to add an update here so that if the leader is on a different lane, then it leaves the platoon
						self.Remove(self._vehicleList[0])
						break
					else:#This forces the vehicle to be on the same lane as the leader (or sumo overides this)
						traci.vehicle.changeLane(self._vehicleList[i].GetID(), L1, constants.CONST_LANE_CHANGE_DURATION)
				else:#Not on the same edge
					connected = False
					if(RJ1 in Ro2):#Make sure the follower vehicle is going to end up on the lead vehicles edge
						baseLane = -1
						#Let's say that the lead vehicle can be max 2 edges ahead otherwise we transfer cotnrol
						if(Ro2.index(RJ1) - ind2 <=2):
							j1 = 0
							while j1 <= self.GetNumberOfLanes(Ro2[ind2]) -1:#loop through all lanes on 1st edge
								locLaneList = []
								for k in range(0, self.GetNumberOfLanes(Ro2[ind2])):
									locLaneList.append(k)

								locLaneList.remove(L2)
								locLaneList.insert(0,L2)
								rawLinks = traci.lane.getLinks(Ro2[ind2] + '_' + str(locLaneList[j1]))
								myLinks = []

								for k in range(0,len(rawLinks)):#Strips down the list
									myLinks.append(rawLinks[k][0])

								for j2 in range(0,(len(myLinks))):#loop through all links which lane is connected to
									if(myLinks[j2] == RJ1 + '_' + str(L1)):
										connected = True
										baseLane = locLaneList[j1]
										break
									else:
										rawLinks2 = traci.lane.getLinks(myLinks[j2])
										myLinks2 = []

										for k in range(0,len(rawLinks2)):#Strips down the list
											myLinks2.append(rawLinks2[k][0])

										for j3 in range(0,(len(myLinks2))):#loop through all links which lane is connected to
											if(myLinks2[j3] == RJ1 + '_' + str(L1)):
												connected = True
												baseLane = locLaneList[j1]
												break

									if (connected):
										break

								if (connected):
										break

								j1+=1


					if(connected):
						traci.vehicle.changeLane(self._vehicleList[i].GetID(), locLaneList[j1], constants.CONST_LANE_CHANGE_DURATION)


	def ShouldVehicleJoin(self, vehID):
		#This checks if the vehicle should join the platoon
		#Distance they can travel together
		if(self.Count() >= constants.CONST_MAXSIZE):
			return False

		totalDistance = 0

		#routes of the subsequent vehicles
		R = traci.vehicle.getRoute(vehID)

		#index of the edge which the vehicle is on within its routs
		ind = traci.vehicle.getRouteIndex(vehID)
		
		if(R[ind] not in self.GetBaseRoute()):
			return False
		else:
			bInd = self.GetBaseRoute().index(R[ind])

		#Loops through the first route starting from the index
		for i in range(bInd,len(self.GetBaseRoute())):

			if(R[ind]!=self.GetBaseRoute()[bInd]):
				break;
			else:
				#Update distance etc...
				totalDistance += traci.lane.getLength(R[ind] + "_0")

				#Update counters
				ind+=1
				bInd+=1

		#Gets total distance and removes the distance it has travelled along the current lane
		totalDistance = totalDistance - traci.vehicle.getLanePosition(vehID)

		return True if(totalDistance >constants.CONST_MIN_PLATOON_DISTANCE) else False

	def GetNumberOfLanes(self, edgeID):
		counter = 1
		cont = True

		while cont:
			if(edgeID + '_' + str(counter) not in self._laneList):
				cont = False
				break
			else:
				counter+=1
		
		return counter

	def _getEdgeIDList(self):
		#The list from the TRACI function contains internal edges as well
		self._edgeList = traci.edge.getIDList()

		i = 0
		l = len(self._edgeList)
		while (i < l):
			if(self._edgeList[i][0] == ':'):
				self._edgeList.pop(i)
				l = len(self._edgeList)
			else:
				i+=1

	def CheckPlatoonIntruders(self):
		#Checks to see if there are any vehicle which do not belong to the platoon which have intruded
		for i in range(1,len(self._vehicleList)):
			vid1 = self._vehicleList[i-1].GetID()
			vid2 = self._vehicleList[i].GetID()

			vehAhead = traci.vehicle.getLeader(vid2)
			if(vehAhead != None):#checks vehicle directly in front
				if(vehAhead[0] not in self.GetVehicleListID()):
					#print 'Breaking up platoon: ' + vid1 + ', ' + vid2
					
					while(i<len(self._vehicleList)):#Keeps the first i vehicles
						self.Remove(self._vehicleList[i])

					break;

class PlatoonManager:
	#The purpose of this class is to manage all of the platoons in the system
	
	#Class variables, default values
	_platoonList = [] #This is a list of type 'Platoon'

	#Properties
	def GetPlatoonIdList(self):
		l = []
		for i in range(0,len(self._platoonList)):
			l.append(self._platoonList[i].GetID())
		return l

	def GetPlatoon(self, platoonID):
		if(platoonID in self.GetPlatoonIdList()):
			for p in self._platoonList:
				if(p.GetID() == platoonID):
					return p
		else:
			print ('Platoon :' + str(platoonID) + ' does not exist.')
			return None

	#Constructor
	# def __init__(self):
	# 	print 'Platoon Manager is initialised'

	def AddPlatoon(self, listOfVehicles):

		i = 0
		unique = False #Make sure the platoon id is unique
		while not unique:
			newPID = 'platoon' + str(len(self._platoonList) + i)

			if(newPID not in self.GetPlatoonIdList()):
				unique = True
			i+=1

		myPlat = Platoon(newPID)#Initialise the platoon
		
		#Loops through all of the vehicles
		for veh in listOfVehicles:
			myPlat.Add(veh)

		#Need to update the 'base route' of the platoon

		#Add to the list to be managed
		self._platoonList.append(myPlat)
		myPlat = None #Delete the temp obj

	def RemovePlatoon(self, platoonID):
		#Remove all of the vehicles in the platoon and then delete the platoon
		p = self.GetPlatoon(platoonID)

		for veh in p.GetVehicleList():
			veh.RemoveFromPlatoon()

		for i in range(0,len(self._platoonList)):
			if (p.GetID() == self._platoonList[i].GetID()):
				self._platoonList.pop(i)
				break
		p = None

	def Update(self):

		i = 0
		while i <len(self._platoonList):
			self._platoonList[i].Update()

			#Removes any platoons with less than 2 vehicles
			if(self._platoonList[i].Count() < constants.CONST_MINSIZE):
				self.RemovePlatoon(self._platoonList[i].GetID())
			else:
				i+=1

	def RemoveVehicle(self, veh):
		if(veh.GetPlatoonID() != None):
			i = self.GetPlatoonIdList().index(veh.GetPlatoonID())#Gets the index of the vehicle from ID list
			self._platoonList[i].RemoveVehicle(veh)

	def RequestVehicleJoin(self, vehID, platoonID):
		p = self.GetPlatoon(platoonID)
		return False if(p == None) else p.ShouldVehicleJoin(vehID)#Returns whether the vehicle should join the platoon

	def MergePlatoons(self, platoonID1, platoonID2):
		p1 = self.GetPlatoon(platoonID1)
		newListofVeh = self.GetPlatoon(platoonID2).GetVehicleList()
		self.RemovePlatoon(platoonID2);

		for i in range(0, len(newListofVeh)):
			p1.Add(newListofVeh[i])

		newListofVeh = None

class ProgramManager:
	#The purpose of this class is to manage the entire system

	#class variables
	vehicleManager = None #Manages the vehicles
	_baseFile = ''
	_cfgFile = ''
	_junctionDictionary = {}
	_intersectionFlow = {}
	_oldIntersectionFlowVehIds = {}
	_simulationTimestep = 0
	_configFile = ""

	#Properties
	def GetCFGFile(self):
		return self._cfgFile

	def GetBaseFile(self):
		return self._baseFile

	def GetJunctionDictionary(self):
		return self._junctionDictionary

	def GetSimulationTimestep(self):
		return self._simulationTimestep

	def SetSimulationTimestep(self, timeStep):
		self._simulationTimestep = timeStep


	#Constructor
	def __init__(self, basePath, nameOfCFGFile, configFile):
		#Gets a list of all of the lanes in the network
		constants.UpdateParameters(configFile)
		self._configFile = configFile
		self._baseFile = basePath
		self._cfgFile = nameOfCFGFile
		self.UpdateJunctionList()
		self.InitialiseOldIntersectionFlow()

		#Initialise the vehicle manager
		self.vehicleManager = VehicleManager(basePath, nameOfCFGFile)


	def Update(self, timeStep):
		#Gets a list of all of the vehicles in the network
		listOfVehicles = traci.vehicle.getIDList()

		#Adds the vehicles to the list
		self.vehicleManager.UpdateListActiveVehicles(listOfVehicles)
		if(constants.CONST_ENABLE_PLATOONING):
			self.vehicleManager.Update(timeStep)
		self.SetSimulationTimestep(timeStep)
		#self.UpdateFlowRateCounters()

	def InitialiseOldIntersectionFlow(self):
		#Loops through all junction to measure
		for j in range(0,len(constants.CONST_JUNCTIONS_TO_MEASURE)):
			self._intersectionFlow[constants.CONST_JUNCTIONS_TO_MEASURE[j]] = []
			self._oldIntersectionFlowVehIds[constants.CONST_JUNCTIONS_TO_MEASURE[j]] = []
			edgeList = self._junctionDictionary[constants.CONST_JUNCTIONS_TO_MEASURE[j]]#Retrieves the edges connected to the junction

			for i in range(0,len(edgeList)):
				self._oldIntersectionFlowVehIds[constants.CONST_JUNCTIONS_TO_MEASURE[j]].append([])

	def UpdateJunctionList(self):
		#reads the xml .net file and gets the list of edges connectd to each junction
		tree = ET.parse(self.GetBaseFile() + self.GetCFGFile())
		root = tree.getroot()

		theNetAddress = ''

		for child in root:
			if(child.tag == 'input'):
				for sub in child:
					if(sub.tag == 'net-file'):
						theNetAddress =  sub.attrib['value']
					break


		tree = ET.parse(self.GetBaseFile() + theNetAddress)
		root = tree.getroot()

		myJunctionDic = {}

		for child in root:
			if(child.tag == 'junction'):
				theSubDic = child.attrib
				if(theSubDic['id'][0] != ':'):#No internal edges
					allLanesList = theSubDic['incLanes'].split()
					uniqueEdgeList = []
					for i in allLanesList:
						edge = i.split('_')[0]

						if(edge not in uniqueEdgeList):
							uniqueEdgeList.append(edge)

					myJunctionDic[theSubDic['id']] = uniqueEdgeList

		self._junctionDictionary = myJunctionDic

	def UpdateFlowRateCounters(self):
		#Updates the number of vehicles going through

		#Determines which index should the counter be stored in
		index = int(math.floor(self.GetSimulationTimestep()/constants.CONST_MEASUREMENT_INTERVAL))
		for j in range(0,len(constants.CONST_JUNCTIONS_TO_MEASURE)):
			edgeList = self._junctionDictionary[str(constants.CONST_JUNCTIONS_TO_MEASURE[j])]#Retrieves the edges connected to the junction

			#Loop through all of the edges
			for i in range(0,len(edgeList)):
				counter = 0
				newVehIds = traci.edge.getLastStepVehicleIDs(edgeList[i])
				

				for oldVeh in self._oldIntersectionFlowVehIds[str(constants.CONST_JUNCTIONS_TO_MEASURE[j])][i]:
					#print 
					if oldVeh not in newVehIds and oldVeh != '':
						counter +=1

				if(index < len(self._intersectionFlow[str(constants.CONST_JUNCTIONS_TO_MEASURE[j])])):
					self._intersectionFlow[str(constants.CONST_JUNCTIONS_TO_MEASURE[j])][index] += counter
				else:
					self._intersectionFlow[str(constants.CONST_JUNCTIONS_TO_MEASURE[j])].append(counter)

				if(len(newVehIds)> 1):#Update the old list
					self._oldIntersectionFlowVehIds[str(constants.CONST_JUNCTIONS_TO_MEASURE[j])][i] = newVehIds
				elif(len(newVehIds) == 1):
					self._oldIntersectionFlowVehIds[str(constants.CONST_JUNCTIONS_TO_MEASURE[j])][i] = newVehIds
				else:
					self._oldIntersectionFlowVehIds[str(constants.CONST_JUNCTIONS_TO_MEASURE[j])][i] = []


	def OnExit(self):
		#Does all of the initialising and saves the flow data

		intersectionFlowRates = {}
		#Loop through all of the junctions
		for i in self._intersectionFlow:
			#Loop through all of the intervals
			localFlowRates = []
			for x in range(0,len(self._intersectionFlow[i])):
				localFlowRates.append(3600*self._intersectionFlow[i][x]/constants.CONST_MEASUREMENT_INTERVAL)
			intersectionFlowRates[i] = localFlowRates

		intersectionFlowRates['Time'] = range(0,len(intersectionFlowRates[i])*constants.CONST_MEASUREMENT_INTERVAL,constants.CONST_MEASUREMENT_INTERVAL)
		df = DataFrame(intersectionFlowRates)

		folderName = constants.CONST_EXPERIMENT_NAME
		newFolderurl = os.path.abspath(os.path.join(os.getcwd(),os.pardir)) + '\\MyProgram\\Tests\\Experiments\\' + folderName
		counter = 0
		while os.path.exists(newFolderurl):
			newFolderurl = os.path.abspath(os.path.join(os.getcwd(),os.pardir)) + '\\MyProgram\\Tests\\Experiments\\' + folderName + '_' + str(counter)
			counter +=1

		os.makedirs(newFolderurl)
		df.to_excel(newFolderurl + '\\' + constants.CONST_FLOW_FILE_NAME, sheet_name='sheet1', index=False)


		#Saves the settings file as well in the same folder
		shutil.copyfile(self._configFile, newFolderurl  + '\\' + self._configFile.split("\\")[-1])



class VehicleManager:
	#The purpose of this class is to manage all of the vehicles in the system



	#Class variables, default values
	_vehicleList = [] #This is a list of Type 'MyVehicle'
	platoonManager = PlatoonManager() #Manages the platoons
	_laneList = []
	_quit = False
	#Properties
	def GetVehicleList(self):
		return self._vehicleList

	def GetVehicleListIDs(self):
		theList = []
		for k in range(0,len(self._vehicleList)):
			theList.append(self._vehicleList[k].GetID())
		return theList

	def Quit(self):
		return self._quit

	#Constructor
	def __init__(self, basePath, nameOfCFGFile):
		#Gets a list of all of the lanes in the network
		self._laneList = traci.lane.getIDList()


	def UpdateListActiveVehicles(self, listOfActiveVehicles):
		#This takes in the active vehicles in SUMO and updates the lists in this class
		_newVehiclesID = []
		_oldVehiclesID = []

		#This is where we add all of the new vehicles in the newtwork
		#Loops through all of the active vehicles in SUMO
		for vehID in listOfActiveVehicles:
			#Checks if it's the currently vehicle list i.e. has it just been added or not?
			exists = False

			for i in range(0,len(self._vehicleList)):
				if(vehID == self._vehicleList[i].GetID()):
					exists = True
					break 

			if (not exists):#If it's a new vehicle, add it to the internal vehicle list (not TRACI)
				_newVehiclesID.append(vehID)
				self.AddVehicle(vehID)

		#This is where we delete vehicles which have left the network
		myL = len(self._vehicleList)
		k=0
		while k < myL:#Loops through all vehicles in the internal list (NOT TRACI)
			vehID = self._vehicleList[k].GetID()

			if vehID not in listOfActiveVehicles:#If it's no longer in the network

				self.RemoveVehicle(vehID)#This changes the size of the vehicle list
				myL = len(self._vehicleList)#Update loop
			else:
				k+=1


	def AddVehicleList(seld, listOfVehIDs):
		#Add a list of vehicles to the system
		for vehID in listOfVehIDs:
			self.AddVehicle(vehID)

	def AddVehicle(self, vehID):
		state = State.Connected if (random.random()  <= constants.CONST_PROPORTION_CONNECTED_VEHICLES) else State.Unconnected #Get state (connected or unconnected)
		veh = MyVehicle(vehID, state)#Create vehicle classs
		self._vehicleList.append(veh)#Add vehicle to the system

	def RemoveVehicle(self, vehID):
		i = self.GetVehicleListIDs().index(vehID)#Gets the index of the vehicle from ID list
		if(self._vehicleList[i].GetPlatoonID != None):
			self.platoonManager.RemoveVehicle(self._vehicleList[i])#Remove vehicle from platoons etc...
		self._vehicleList.pop(i)#Remove the vehicle from the vehicle list

	def CreatePlatoon(self, listOfVehIDs):
		self.platoonManager.AddPlatoon(self.GetVehicleListFromIDs(listOfVehIDs))

	def Update(self, timeStep):
		#Update each platoon
		self.platoonManager.Update()#Update the patoons
		self.FormPlatoons()

	def GetVehicleListFromIDs(self, listOfVehicleIds):
		vehIDsList = self.GetVehicleListIDs()
		localVehicleList = []

		for k in range(0, len(listOfVehicleIds)):
			localVehicleList.append(self._vehicleList[vehIDsList.index(listOfVehicleIds[k])])

		return localVehicleList

	def GetVehicleFromID(self, vehID):
		return self._vehicleList[self.GetVehicleListIDs().index(vehID)]
	
	def GetNumberConnectedVehicles(self, listOfVehicleIds):
		counter = 0
		for vid in listOfVehicleIds:
			if (self.GetVehicleFromID(vid).GetState() == State.Connected):
				counter+=1

		return counter

	def InitialiseOldIntersectionFlow(self):
		#Loops through all junction to measure
		for j in range(0,len(constants.CONST_JUNCTIONS_TO_MEASURE)):
			self._intersectionFlow[constants.CONST_JUNCTIONS_TO_MEASURE[j]] = []
			self._oldIntersectionFlowVehIds[constants.CONST_JUNCTIONS_TO_MEASURE[j]] = []
			edgeList = self._junctionDictionary[constants.CONST_JUNCTIONS_TO_MEASURE[j]]#Retrieves the edges connected to the junction

			for i in range(0,len(edgeList)):
				self._oldIntersectionFlowVehIds[constants.CONST_JUNCTIONS_TO_MEASURE[j]].append([])

	def FormPlatoons(self):
		#Loops through all of the id's of the lanes in the network
		for i in self._laneList:
			#List of platoons which have at least one vehicle on the lane
			lanePlatoonList = []

			#List of ifs of the vehicles which are on the lane
			locVehList = traci.lane.getLastStepVehicleIDs(i)
			#Jumps to the next lane if there are not 2 vehicles in the lane
			if (self.GetNumberConnectedVehicles(locVehList) < 2):
				continue

			#Loops through all of the vehicles on the lane
			#print locVehList
			for j in range(1,len(locVehList)):

				#Compare subsequent vehicles
				veh1 = self.GetVehicleFromID(locVehList[j])
				veh2 = self.GetVehicleFromID(locVehList[j-1])

				#Check if they are connected first...
				if(veh1.GetState() == State.Unconnected or veh2.GetState() == State.Unconnected):
					continue

				#If the susbsequent vehicles are within the 'search distance'
				if(abs((traci.vehicle.getLanePosition(veh1.GetID()) - traci.vehicle.getLanePosition(veh2.GetID())) < constants.CONST_SEARCH_DISTANCE)):
					
					#First we need to check if one of them is in a platoon
					if(veh1.GetInPlatoon() and veh2.GetInPlatoon()):
						#they are both in platoons
						if(veh1.GetPlatoonID() != veh2.GetPlatoonID()):#Not in same platoon... can we merge them?
							#Compare both base routes and if they line up then merge them
							if(self.ShouldPlatoonsMerge(veh1.GetPlatoonID(),veh2.GetPlatoonID(),veh1,veh2)):
								self.platoonManager.MergePlatoons(veh1.GetPlatoonID(),veh2.GetPlatoonID())
							continue
						else:
							continue#In the same platoon..continue
					elif(veh1.GetInPlatoon() and (not veh2.GetInPlatoon())):#Veh1 in platoon and veh2 not in platoon
						#Need to check if veh2 should join the platoon. does it travel far enough with the platoon?
						if(self.platoonManager.RequestVehicleJoin(veh2.GetID(), veh1.GetPlatoonID())):
							self.platoonManager.GetPlatoon(veh1.GetPlatoonID()).Add(veh2)
							#print 'Adding: ' + veh2.GetID()+ ' because of ' + veh1.GetID()
						else:
							continue
					elif(veh2.GetInPlatoon() and (not veh1.GetInPlatoon())):#Veh1 not in platoon and veh2  in platoon
						#Need to check if veh1 should join the platoon. does it travel far enough with the platoon?
						if(self.platoonManager.RequestVehicleJoin(veh1.GetID(), veh2.GetPlatoonID())):
							self.platoonManager.GetPlatoon(veh2.GetPlatoonID()).Add(veh1)
							#print 'Adding: ' + veh1.GetID() + ' because of ' + veh2.GetID()
						else:
							continue
					else:#neither in platoon
						#Distance they can travel together
						totalDistance = self._getDistanceTravelledTogether(locVehList[j-1],locVehList[j]) - traci.vehicle.getLanePosition(locVehList[j-1])
						
						if(totalDistance > constants.CONST_MIN_PLATOON_DISTANCE):
							newPlatoon = [veh1, veh2]
							self.platoonManager.AddPlatoon(newPlatoon)

	def ShouldPlatoonsMerge(self, platoonID1, platoonID2, veh1, veh2):
		#Checks whether 2 platoons should merge, the two vehicles 
		#are the ones who initiated the convo

		#Assume platoon 1 is ahead of platoon 2
		#Assume veh 1 is ahead of veh 2
		vehID1 = veh1.GetID()
		vehID2 = veh2.GetID()

		#Compare their base routes
		p1 = self.platoonManager.GetPlatoon(platoonID1)
		p2 = self.platoonManager.GetPlatoon(platoonID2)
		BR1 = p1.GetBaseRoute()
		BR2 = p2.GetBaseRoute()

		if(len(BR1) == 0 or len(BR2) ==0):
			return False

		#Only merge if the veh are the last and first in their respective platoons
		if(veh1.GetPosition() != p1.Count() - 1 or veh2.GetPosition() != 0):
			return False

		#If the merged platoon would be too big, return false
		if(p1.Count() + p2.Count() > constants.CONST_MAXSIZE):
			return False 

		R1 = traci.vehicle.getRoute(vehID1)
		R2 = traci.vehicle.getRoute(vehID2)

		#index of the edge which the vehicle is on within its routs
		indV1 = traci.vehicle.getRouteIndex(vehID1)
		indV2 = traci.vehicle.getRouteIndex(vehID2)

		#Indices within the base routes
		ind1 = BR1.index(R1[indV1])
		ind2 = BR2.index(R2[indV2])

		totalDistance = 0#Distance they can travel together
		
		if(len(BR1) - ind1 < len(BR2) - ind2):#Loops through the first route starting from the index
			for i in range(ind1,len(BR1)):
				if(BR1[ind1]!=BR2[ind2]):
					break;
				else:
					totalDistance += traci.lane.getLength(BR1[ind1] + "_0")#Update distance etc...

					ind1+=1#Update counters
					ind2+=1
		else:
			for i in range(ind2,len(BR2)):
				if(BR1[ind1]!=BR2[ind2]):
					break;
				else:
					totalDistance += traci.lane.getLength(BR1[ind1] + "_0")#Update distance etc...
				
					ind1+=1#Update counters
					ind2+=1

		totalDistance-=traci.vehicle.getLanePosition(vehID2)#Subtract current pos

		return (totalDistance > constants.CONST_MIN_PLATOON_DISTANCE)

	def _getDistanceTravelledTogether(self, vehID1, VehID2):
		#Distance they can travel together
		totalDistance = 0

		#routes of the subsequent vehicles
		R1 = traci.vehicle.getRoute(vehID1)
		R2 = traci.vehicle.getRoute(VehID2)

		#index of the edge which the vehicle is on within its routs
		ind1 = traci.vehicle.getRouteIndex(vehID1)
		ind2 = traci.vehicle.getRouteIndex(VehID2)

		#Loops through the first route starting from the index
		for i in range(ind1,len(R1)):
			if(R1[ind1]!=R2[ind2]):
				break
			else:
				#Update distance etc...
				totalDistance += traci.lane.getLength(R1[ind1] + "_0")

				#Update counters
				ind1+=1
				ind2+=1
		return totalDistance

class MyVehicle:
	#The vehicle class provided by TracCI is more of a "static class"

	#Class variables
	_id = ""
	_inPlatoon = False
	_platoonID = None
	_platoonPosition = 2
	_state = None
	_tau = 0

	#Constructor
	def __init__(self, vehicleID, state):
		#Provides an id for the platoon
		self._id = vehicleID
		self._state = state
		
		if (self._state == State.Connected):
			self.SetTau(constants.CONST_TAU_CONNECTED_NO_PLATOON)
		elif (self._state == State.Unconnected):
			self.SetTau(constants.CONST_TAU_UNCONNECTED)
		else:
			print 'Error'

		self.UpdateColor()

	#Properties
	def GetState(self):
		return self._state

	def SetTau(self, newTau):
		traci.vehicle.setTau(self._id, newTau)
		self._tau = newTau#Update internal tau

	def GetTau(self):
		return traci.vehicle.getTau(self._id)

	def GetID(self):
		return self._id

	def GetPlatoonID(self):
		return self._platoonID

	def GetPosition(self):
		return self._platoonPosition

	def SetPosition(self, position):
		if (self._platoonPosition != position):
			self._platoonPosition = position
			self.UpdateColor()

	def GetPreviousEdgeID(self):
		return 'not impl'

	def GetInPlatoon(self):
		return self._inPlatoon

	#Methods
	def Update(self):
		#If it's the leader, it can change lanes more easily than the follower vehicles
		if(self._platoonPosition == 0):
			if(self._tau != constants.CONST_TAU_CONNECTED_NO_PLATOON):
				self.SetTau(constants.CONST_TAU_CONNECTED_NO_PLATOON)
			if(traci.vehicle.getSpeed(self.GetID())<constants.CONST_STOP_SPEED):
				traci.vehicle.setLaneChangeMode(self._id,533)
			else:
				traci.vehicle.setLaneChangeMode(self._id,517)
		else:
			traci.vehicle.setLaneChangeMode(self._id,512)
			if(self._tau != constants.CONST_TAU_CONNECTED_PLATOON):
				self.SetTau(constants.CONST_TAU_CONNECTED_PLATOON)


	def AddToPlatoon(self, platoonID, platoonPosition):
		self._platoonID = platoonID
		self._platoonPosition = platoonPosition
		self._inPlatoon = True
		traci.vehicle.setLaneChangeMode(self._id,512)
		self.SetTau(constants.CONST_TAU_CONNECTED_PLATOON)
		self.UpdateColor()

	def RemoveFromPlatoon(self):
		self._platoonID = None
		self._platoonPosition = 2
		self._inPlatoon = False
		traci.vehicle.setLaneChangeMode(self._id,597)
		self.SetTau(constants.CONST_TAU_CONNECTED_NO_PLATOON)
		self.UpdateColor()
	def UpdateColor(self):
		if(self._inPlatoon):
			if(self._platoonPosition == 0):
				traci.vehicle.setColor(self._id, (255,0,0,0))#Red: leader
			else:
				traci.vehicle.setColor(self._id, (100,149,237,0))#Blue: platoon
		else:
			if(self.GetState() == State.Connected):
				traci.vehicle.setColor(self._id, (255,255,0,0))#Yellow: not in platoon
			else:
				traci.vehicle.setColor(self._id, (0,204,0,0))#Green: unconnected

class State(Enum):
	Connected = 1
	Unconnected = 2