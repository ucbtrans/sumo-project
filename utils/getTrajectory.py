import os
import sys
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '..'))
from sumolib.output import *
from sumolib.miscutils import Statistics
import pdb
import matplotlib.pyplot as plt
import numpy as np

#functions used in trajectoryData
def _prefix_keyword(name, warn=False):
		result = name
		# create a legal identifier (xml allows '-', ':' and '.' ...)
		result = ''.join([c for c in name if c.isalnum() or c == '_'])
		if result != name:
				if result == '':
						result == 'attr_'
		if iskeyword(name):
				result = 'attr_' + name
		return result

def parse_time_fast(xmlfile,element_name,attrnames,warn=False):
		pattern = '.*'.join(['<%s' % element_name] +
												['%s="([^"]*)"' % attr for attr in attrnames])
		attrnames = [_prefix_keyword(a, warn) for a in attrnames]
		Record = namedtuple(element_name, attrnames)
		reprog = re.compile(pattern)

		time_pattern = '.*'.join(['<%s' % 'timestep'] +
														 ['%s="([^"]*)"' % 'time'])
		time_attrnames = [_prefix_keyword('time',warn)]
		time_Record = namedtuple('timestep',time_attrnames)
		time_reprog = re.compile(time_pattern)

		f = open(xmlfile)
		line = f.readline()

		while line:
			line = f.readline()
			t = time_reprog.search(line)
			if t: #always find a timestep first before vehicle data
							#then start looking for the vehicle data between timestep time = x and <\timestep>
				while '</timestep>' not in line:
					line = f.readline()
					m = reprog.search(line)
					if m:
						yield ( Record(*m.groups()) , time_Record(*t.groups()) )

#main function
def trajectoryData(netstate,ids):
	lastSpeed = {}
	veh = ['veh' +  s for s in ids]
	xval = [[] for i in range(len(veh))]
	yval = [[] for i in range(len(veh))]
	tval = [[] for i in range(len(veh))]

	#stats = Statistics(
		#"Accelerations", histogram=True, printMin=True, scale=0.2)
	#print stats

	for vehicle, timestamp in parse_time_fast(netstate, 'vehicle', ['id', 'x','y','speed', 'pos']):
		if vehicle.id in veh:
			idx = veh.index(vehicle.id)
			xval[idx].append(vehicle.x)
			yval[idx].append(vehicle.y)
			tval[idx].append(timestamp.time)
			#tval.append(timestep.time)
		
		#speed = float(vehicle.speed)
		#prevSpeed = lastSpeed.get(vehicle.id, speed)
		#stats.add(speed - prevSpeed, (vehicle.id, vehicle.speed))
		#lastSpeed[vehicle.id] = speed
	xpos = np.array(xval)
	ypos = np.array(yval)
	t = np.array(tval)

	dist = distance_array(xpos,ypos)

	return t,dist

def distance_array(x,y):
	x = [map(float,a) for a in x.tolist()]
	y = [map(float,a) for a in y.tolist()]
	dx = [np.diff(a) for a in x]
	dy = [np.diff(a) for a in y]
	dist_step = [pow(pow(a,2)+pow(b,2),0.5) for a,b in zip(dx,dy)]
	dist = [np.cumsum(a) for a in dist_step]
	return dist
#get vehicle id
def request_id():
	while True: #infinite loop
	 ipt = raw_input(' Enter the vehicle id: ')
	 try:
			ipt = int(ipt)
			break  #got an integer -- break from this infinite loop.
	 except ValueError:  #uh-oh, didn't get an integer, better try again.
			print ("Vehicle id must be an ineger? Try again ...")
	return ipt

def inputnumber():
	num = raw_input('Enter Vehicle Id(s): ').split(',')
	return map(str,[int(n) for n in num])


if __name__ == "__main__":
	file_name = ''.join(sys.argv[1:])
	#veh_id = request_id()
	veh_id = inputnumber() #do vehicles 1 and 4
	t,dist = trajectoryData(file_name,veh_id)

	for i in range(len(dist)):
		plt.plot(t[i][:len(t[i])-1],dist[i])

	plt.xlabel('Time (s)')
	plt.ylabel('Distance Travelled')
	plt.title('Trajectory')
	plt.legend(['Veh ' + str for str in veh_id])
	plt.show()

	for i in range(len(dist)):
		plt.plot(t[i][:len(t[i])-1],dist[i])

	plt.xlabel('Time (s)')
	plt.ylabel('Distance Travelled')
	plt.title('Trajectory')
	plt.legend(['Veh ' + str for str in veh_id])
	plt.show()

'''
	for i in range(len(x)):
		plt.plot(t[i],x[i])
	plt.xlabel('Time (s)')
	plt.ylabel('X position')
	plt.title('X trajectory vs Time')
	plt.show()
	'''



