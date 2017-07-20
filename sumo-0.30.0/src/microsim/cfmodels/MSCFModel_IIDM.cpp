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

#include <stdio.h>
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
                               double accel, double decel, double emergencyDecel,
                               double headwayTime, double delta1, double delta2,
                               double internalStepping) :
	  MSCFModel(vtype, accel, decel, emergencyDecel, decel, headwayTime),
	  delta1(delta1), delta2(delta2),
      myIterations(MAX2(1, int(TS / internalStepping + .5))),
	  myTwoSqrtAccelDecel(double(2 * sqrt(accel* decel))) {
}


MSCFModel_IIDM::~MSCFModel_IIDM() {}


double
MSCFModel_IIDM::moveHelper(MSVehicle* const veh, double vPos) const {
	const double vNext = MSCFModel::moveHelper(veh, vPos);
    /*if (myAdaptationFactor != 1.) {
        VehicleVariables* vars = (VehicleVariables*)veh->getCarFollowVariables();
        vars->levelOfService += (vNext / veh->getLane()->getVehicleMaxSpeed(veh) - vars->levelOfService) / myAdaptationTime * TS;
    }*/
    return vNext;
}


double
MSCFModel_IIDM::followSpeed(const MSVehicle* const veh, double speed, double gap2pred, double predSpeed, double) const {
    //return _v(veh, gap2pred, speed, predSpeed, veh->getLane()->getVehicleMaxSpeed(veh));
	return _v(veh, gap2pred, speed, predSpeed, MIN2(veh->getLane()->getSpeedLimit(), veh->getMaxSpeed()), true);
}


/*double
MSCFModel_IIDM::stopSpeed(const MSVehicle* const veh, const double speed, double gap2pred) const {
    if (gap2pred < 1) {
        return 0;
    }
    //return _v(veh, gap2pred, speed, 0, veh->getLane()->getVehicleMaxSpeed(veh), false);
	return _v(veh, gap2pred, speed, 0, MIN2(veh->getLane()->getSpeedLimit(), veh->getMaxSpeed()), false);
}*/

double
MSCFModel_IIDM::stopSpeed(const MSVehicle* const veh, const double speed, double gap) const {
	// NOTE: This allows return of smaller values than minNextSpeed().
	// Only relevant for the ballistic update: We give the argument headway=TS, to assure that
	// the stopping position is approached with a uniform deceleration also for tau!=TS.
	return MIN2(maximumSafeStopSpeed(gap, speed, false, TS), maxNextSpeed(speed, veh));
}


/// @todo update interactionGap logic to IIDM
double
MSCFModel_IIDM::interactionGap(const MSVehicle* const veh, double vL) const {
    // Resolve the IIDM equation to gap. Assume predecessor has
    // speed != 0 and that vsafe will be the current speed plus acceleration,
    // i.e that with this gap there will be no interaction.
	const double acc = myAccel * (1. - pow(veh->getSpeed() / MIN2(veh->getLane()->getSpeedLimit(), veh->getMaxSpeed()), delta2));
	const double vNext = veh->getSpeed() + acc;
	double gap = (vNext - vL) * (veh->getSpeed() + vL) / (2 * myDecel) + vL;
	//gap = (vNext - vL) * ((veh->getSpeed() + vL) / (2.*myDecel) + myHeadwayTime) + vL * myHeadwayTime;

    // Don't allow timeHeadWay < deltaT situations.
    return MAX2(gap, SPEED2DIST(vNext));
}

/*double
MSCFModel_IIDM::interactionGap(const MSVehicle* const veh, double vL) const {
	// Resolve the vsafe equation to gap. Assume predecessor has
	// speed != 0 and that vsafe will be the current speed plus acceleration,
	// i.e that with this gap there will be no interaction.
	const double vNext = MIN2(maxNextSpeed(veh->getSpeed(), veh), veh->getLane()->getVehicleMaxSpeed(veh));
	const double gap = (vNext - vL) *
		((veh->getSpeed() + vL) / (2.*myDecel) + myHeadwayTime) +
		vL * myHeadwayTime;

	// Don't allow timeHeadWay < deltaT situations.
	return MAX2(gap, SPEED2DIST(vNext));
}*/


double
MSCFModel_IIDM::_v(const MSVehicle* const veh, const double gap2pred, const double egoSpeed,
                   const double predSpeed, const double desSpeed, const bool respectMinGap) const {
// IIDM speed update
	double headwayTime = myHeadwayTime;
    /*if (myAdaptationFactor != 1.) {
        const VehicleVariables* vars = (VehicleVariables*)veh->getCarFollowVariables();
        headwayTime *= myAdaptationFactor + vars->levelOfService * (1. - myAdaptationFactor);
    }*/
	double newSpeed = egoSpeed;
	double gap = gap2pred;
	double myIterations0 = myIterations;

	const double delta_v = newSpeed - predSpeed;
	double s = MAX2(0., newSpeed * headwayTime + newSpeed * delta_v / myTwoSqrtAccelDecel);
	if (respectMinGap)
		s += myType->getMinGap();

	if (newSpeed < 1 && predSpeed < 1) {
		gap += 0.75 * myType->getMinGap();
	}

    for (int i = 0; i < myIterations0; i++) {
		double oldSpeed = newSpeed;
		//gap = MAX2(SUMOReal(0.000001), gap);
		//newSpeed = MAX2(SUMOReal(0), newSpeed);
		/*const double delta_v = newSpeed - predSpeed;
		double s = MAX2(0., newSpeed * headwayTime + newSpeed * delta_v / myTwoSqrtAccelDecel);
		if (respectMinGap)
		    s += myType->getMinGap();*/

        // This is equation for IDM:
        //const SUMOReal acc = myAccel * (1 - pow(newSpeed / desSpeed, delta2) - pow(s/gap, delta1));
        
        ////////////// For IIDM:

		double afree;
		double acc = myAccel * (1 - pow(s / gap, delta1));

        if (newSpeed <= desSpeed) { // if we want to speed up or remain (V <= V0)
			afree = myAccel * (1 - pow(newSpeed / desSpeed, delta2)); // free acceleration function

			if (s < gap) { // we are far enough from the leader
				if (afree < 0.0000001) {
					acc = 0;
				}
				else {
					acc = afree * (1 - pow(s / gap, delta1 * myAccel / afree));
				}
        	}
        }
        else { // if we want to slow down (V > V0)
			afree = -myDecel * (1 - pow(desSpeed / newSpeed, myAccel * delta2 / myDecel)); // free acceleration function
    		
			if (s >= gap) {
        		acc += afree;
        	}
        	else {
        		acc = afree;
        	}
        }

		//acc = MAX2(acc, -myDecel);

        ////////////// End IIDM
		
        newSpeed += ACCEL2SPEED(acc) / myIterations0;

        //TODO use more realistic position update which takes accelerated motion into account
		gap -= MAX2(0., SPEED2DIST((newSpeed - predSpeed) / myIterations0));
    }
	
//    return MAX2(getSpeedAfterMaxDecel(egoSpeed), newSpeed);
    return MAX2(0., newSpeed);
}


MSCFModel*
MSCFModel_IIDM::duplicate(const MSVehicleType* vtype) const {
	return new MSCFModel_IIDM(vtype, myAccel, myDecel, myEmergencyDecel, myHeadwayTime, delta1, delta2, TS / myIterations);
}
