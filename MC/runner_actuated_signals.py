#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
import xml.etree.ElementTree as ET
import intersection_controller

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

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))  #sumo-0.30
sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(os.path.dirname(__file__), "..", "..", ".."))))


#parse configuration file for actuated signals
tree = ET.parse('network/actuated_signals_cfg.xml')
root = tree.getroot()




def run():
    #initialization
    step = 0
    length = len(root.getchildren())
    i=range(0,length)# a list containing different intersections' time in a stage
    t=range(0,length)# a list containing different intersections' time in a cycle
    stage=range(0,length)# a list containing different intersections' stages
    f = range(0,length)
    l = range(0,length)
    x = range(0,length)# a list containing different intersections' extension index

        

    #initialize offsets
    for intersection in root:
        tl = intersection.attrib['id']
        no = int(intersection.attrib['no'])
        num = len(intersection.getchildren())
        offset = int(intersection.attrib['offset'])
        cycle_time = int(intersection.attrib['cycletime'])
        lastyellow = int(intersection[num-1].attrib['min_green'])
        t[no]=cycle_time-offset
        stage[no]=0
        traci.trafficlights.setPhase(tl,stage[no])
        i[no] = 1
        
        



    step += 1
    for q in range(0,length):
        f[q] = 0
        l[q] = 0
        x[q] = 0
    traci.simulationStep()
    


    #start simulation
    while traci.simulation.getMinExpectedNumber() > 0:
        for intersection in root:
            #get parameters for each intersection
            tl = intersection.attrib['id']
            no = int(intersection.attrib['no'])
            cycle_time = int(intersection.attrib['cycletime'])
            ext = int(intersection.attrib['extension'])
            gap = int(intersection.attrib['gap'])
            num = len(intersection.getchildren())
            #control time indices and stages for each intersection
            ii=i[no]
            tt=t[no]
            sstage=stage[no]
            ff =f[no]
            ll=l[no]
            xx=x[no]

            min_green= int(intersection[sstage].attrib['min_green'])
            max_green= int(intersection[sstage].attrib['max_green'])

            mini=[]
            maxi=[]
            for phase in intersection:
                mini.append(int(phase.attrib['min_green']))
                maxi.append(int(phase.attrib['max_green']))


            
            #go through controller, and decide for each intersection which stage to invoke
            backlist=intersection_controller.intersection_controller(tl,cycle_time,ext,gap,num,min_green,max_green,ii,sstage,tt,intersection,ff,ll,xx,mini,maxi)

            i[no]=backlist[0]
            t[no]=backlist[1]
            stage[no]=backlist[2]
            f[no]=backlist[3]
            l[no]=backlist[4]
            x[no]=backlist[5]
        
        
        traci.simulationStep()
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
        #sumoBinary = checkBinary('sumo')


    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "network/testmap.sumocfg",
                             "--tripinfo-output", "tripinfo.xml",
                             "--xml-validation", "never",
                             "--verbose", "True"])#specify your own files here
    run()
