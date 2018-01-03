from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random


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

def intersection_controller(tl,cycle_time,ext,gap,num,min_green,max_green,ii,sstage,tt,intersection,ff,ll,xx):
    #for the last unactuated stage to control cyclelength, usually the major through movement, the coordinated movement
    if sstage == 0:
        if ff==0:
            ll = cycle_time - tt

        if ii < ll:
            traci.trafficlights.setPhase(tl, sstage)
            ii += 1
        else:
            sstage += 1
            traci.trafficlights.setPhase(tl, sstage)
            ii = 1
        ff += 1
    #for all other stages, including actuated stages/unactuated yellow
    else:
        if ii < min_green:
            traci.trafficlights.setPhase(tl, sstage)
            ii += 1
        #only actuated stages go through this condition
        elif ii >=min_green and ii < max_green:
            if xx==0:
                s=0
                for detector in intersection[sstage]:
                    detectorid = detector.attrib['id']
                    if traci.inductionloop.getLastStepOccupancy(detectorid) > 0 or traci.inductionloop.getTimeSinceDetection(detectorid) < gap:
                        s += 1
                    else:
                        s += 0
                if s > 0: 
                    traci.trafficlights.setPhase(tl, sstage)
                    ii += 1
                    xx = ext-1
                elif s==0 and sstage == num - 2:
                    sstage += 1
                    traci.trafficlights.setPhase(tl, sstage)
                    ii = 1
                else:
                    v=0
                    if sstage == num - 1:
                        nextactuatedstage = 1
                    else:
                        nextactuatedstage=sstage + 2
                    for detector in intersection[nextactuatedstage]:
                        detectorid = detector.attrib['id']
                        if traci.inductionloop.getLastStepOccupancy(detectorid) > 0:
                            v += 1
                        else:
                            v += 0
                    if v > 0: 
                        sstage += 1
                        traci.trafficlights.setPhase(tl, sstage)
                        ii = 1
                    else:
                        traci.trafficlights.setPhase(tl, sstage)
                        ii += 1
            else:
                traci.trafficlights.setPhase(tl, sstage)
                ii += 1
                xx = xx-1
        else:
            xx=0
            if sstage == num - 1:
                sstage = 0
                traci.trafficlights.setPhase(tl, sstage)
                ii = 1
            else:
                sstage += 1
                traci.trafficlights.setPhase(tl, sstage)
                ii = 1
    #calculate cycletime here and force to reinitialize when a cycle ends
    if tt < cycle_time:
        tt += 1
    else:
        tt = 1
        sstage = 1
        traci.trafficlights.setPhase(tl, sstage)
        ii = 1
        ff = 0

    return [ii,tt,sstage,ff,ll,xx]
