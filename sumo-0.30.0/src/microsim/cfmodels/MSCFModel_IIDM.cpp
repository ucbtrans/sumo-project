/****************************************************************************/
// The Improved Intelligent Driver Model (IIDM) car-following model
/****************************************************************************/
// SUMO, Simulation of Urban MObility; see http://sumo.dlr.de/
// Copyright (C) 2001-2015 DLR (http://www.dlr.de/) and contributors
/****************************************************************************/


// ===========================================================================
// included modules
// ===========================================================================
#ifdef _MSC_VER
#include <windows_config.h>
#else
#include <config.h>
#endif

#include <iostream>
using namespace std;

#include "MSCFModel_IIDM.h"
#include <microsim/MSVehicle.h>
#include <microsim/MSLane.h>
#include <utils/common/RandHelper.h>
#include <utils/common/SUMOTime.h>


// ===========================================================================
// method definitions
// ===========================================================================
MSCFModel_IIDM::MSCFModel_IIDM(const MSVehicleType* vtype,
                             SUMOReal accel, SUMOReal decel, SUMOReal emergencyDecel,
                             SUMOReal headwayTime, SUMOReal delta,
                             SUMOReal internalStepping) :
	  MSCFModel(vtype, accel, decel, emergencyDecel, decel, headwayTime), delta2(delta),
      myAdaptationFactor(1.), myAdaptationTime(0.),
      myIterations(MAX2(1, int(TS / internalStepping + .5))),
      myTwoSqrtAccelDecel(SUMOReal(2 * sqrt(accel* decel))) {
}


MSCFModel_IIDM::MSCFModel_IIDM(const MSVehicleType* vtype,
                             SUMOReal accel, SUMOReal decel, SUMOReal emergencyDecel, 
                             SUMOReal headwayTime,
                             SUMOReal adaptationFactor, SUMOReal adaptationTime,
                             SUMOReal internalStepping) :
	  MSCFModel(vtype, accel, decel, emergencyDecel, decel, headwayTime), delta2(4.),
      myAdaptationFactor(adaptationFactor), myAdaptationTime(adaptationTime),
      myIterations(MAX2(1, int(TS / internalStepping + .5))),
      myTwoSqrtAccelDecel(SUMOReal(2 * sqrt(accel* decel))) {
}


MSCFModel_IIDM::~MSCFModel_IIDM() {}


SUMOReal
MSCFModel_IIDM::moveHelper(MSVehicle* const veh, SUMOReal vPos) const {
    const SUMOReal vNext = MSCFModel::moveHelper(veh, vPos);
    if (myAdaptationFactor != 1.) {
        VehicleVariables* vars = (VehicleVariables*)veh->getCarFollowVariables();
        vars->levelOfService += (vNext / veh->getLane()->getVehicleMaxSpeed(veh) - vars->levelOfService) / myAdaptationTime * TS;
    }
    return vNext;
}


SUMOReal
MSCFModel_IIDM::followSpeed(const MSVehicle* const veh, SUMOReal speed, SUMOReal gap2pred, SUMOReal predSpeed, SUMOReal /*predMaxDecel*/) const {
    //return _v(veh, gap2pred, speed, predSpeed, veh->getLane()->getVehicleMaxSpeed(veh));
	return _v(veh, gap2pred, speed, predSpeed, MIN2(veh->getLane()->getSpeedLimit(), veh->getMaxSpeed()));
}


SUMOReal
MSCFModel_IIDM::stopSpeed(const MSVehicle* const veh, const SUMOReal speed, SUMOReal gap2pred) const {
    if (gap2pred < 1) {
        return 0;
    }
    //return _v(veh, gap2pred, speed, 0, veh->getLane()->getVehicleMaxSpeed(veh), false);
	return _v(veh, gap2pred, speed, 0, MIN2(veh->getLane()->getSpeedLimit(), veh->getMaxSpeed()), false);
}


/// @todo update interactionGap logic to IIDM
SUMOReal
MSCFModel_IIDM::interactionGap(const MSVehicle* const veh, SUMOReal vL) const {
    // Resolve the IIDM equation to gap. Assume predecessor has
    // speed != 0 and that vsafe will be the current speed plus acceleration,
    // i.e that with this gap there will be no interaction.
    const SUMOReal acc = myAccel * (1. - pow(veh->getSpeed() / veh->getLane()->getVehicleMaxSpeed(veh), delta2));
    const SUMOReal vNext = veh->getSpeed() + acc;
    const SUMOReal gap = (vNext - vL) * (veh->getSpeed() + vL) / (2 * myDecel) + vL;

    // Don't allow timeHeadWay < deltaT situations.
    return MAX2(gap, SPEED2DIST(vNext));
}


SUMOReal
MSCFModel_IIDM::_v(const MSVehicle* const veh, const SUMOReal gap2pred, const SUMOReal egoSpeed,
                  const SUMOReal predSpeed, const SUMOReal desSpeed, const bool respectMinGap) const {
// IIDM speed update
    SUMOReal headwayTime = myHeadwayTime;
    if (myAdaptationFactor != 1.) {
        const VehicleVariables* vars = (VehicleVariables*)veh->getCarFollowVariables();
        headwayTime *= myAdaptationFactor + vars->levelOfService * (1. - myAdaptationFactor);
    }
    SUMOReal newSpeed = egoSpeed;
    SUMOReal gap = gap2pred;

    for (int i = 0; i < myIterations; i++) {
        const SUMOReal delta_v = newSpeed - predSpeed;
        // s is S* in IIDM equation
        SUMOReal s = MAX2(SUMOReal(0), newSpeed * headwayTime + newSpeed * delta_v / myTwoSqrtAccelDecel);

        if (respectMinGap)
            s += myType->getMinGap();

        // This is equation for IDM:
        //const SUMOReal acc = myAccel * (1. - pow(newSpeed / desSpeed, delta2) - pow(s/gap, delta1));
        
        ////////////// For IIDM:
        SUMOReal afree;
		SUMOReal acc = myAccel * (1. - pow(s / gap, delta1));

        if (newSpeed <= desSpeed) { // if we want to speed up or remain (V <= V0)
			afree = myAccel * (1 - pow(newSpeed / desSpeed, delta2)); // free acceleration function

			if ((s / gap) < 1) { // we are too close to leader
        		acc = afree * (1 - pow(s / gap, delta1 * myAccel / afree));
        	}
        }
        else { // if we want to slow down (V > V0)
			afree = -myDecel * (1 - pow(desSpeed / newSpeed, myAccel * delta2 / myDecel)); // free acceleration function
    		
			if ((s / gap) >= 1) {
        		acc += afree;
        	}
        	else {
        		acc = afree;
        	}
        }

        ////////////// End IIDM
		
		SUMOReal oldSpeed = newSpeed;
        newSpeed += ACCEL2SPEED(acc) / myIterations;
        //TODO use more realistic position update which takes accelerated motion into account
		gap -= MAX2(SUMOReal(0), SPEED2DIST((newSpeed - predSpeed) / myIterations));
    }
//    return MAX2(getSpeedAfterMaxDecel(egoSpeed), newSpeed);
    return MAX2(SUMOReal(0), newSpeed);
}


MSCFModel*
MSCFModel_IIDM::duplicate(const MSVehicleType* vtype) const {
	return new MSCFModel_IIDM(vtype, myAccel, myDecel, myEmergencyDecel, myHeadwayTime, delta2, TS / myIterations);
}
