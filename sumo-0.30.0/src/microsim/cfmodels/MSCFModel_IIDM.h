// The Improved Intelligent Driver Model (IIDM) car-following model
/****************************************************************************/
// SUMO, Simulation of Urban MObility; see http://sumo.dlr.de/
// Copyright (C) 2001-2015 DLR (http://www.dlr.de/) and contributors
/****************************************************************************/
#ifndef MSCFMODEL_IIDM_H
#define MSCFMODEL_IIDM_H

// ===========================================================================
// included modules
// ===========================================================================
#ifdef _MSC_VER
#include <windows_config.h>
#else
#include <config.h>
#endif

#include "MSCFModel.h"
#include <microsim/MSLane.h>
#include <microsim/MSVehicle.h>
#include <microsim/MSVehicleType.h>
#include <utils/xml/SUMOXMLDefinitions.h>

#ifndef SUMOReal
#define SUMOReal double
#endif


// ===========================================================================
// class definitions
// ===========================================================================
/** @class MSCFModel_IIDM
 * @brief The Improved Intelligent Driver Model (IIDM) car-following model
 * @see MSCFModel
 */
class MSCFModel_IIDM : public MSCFModel {
public:
    /** @brief Constructor
     * @param[in] accel The maximum acceleration
     * @param[in] decel The maximum deceleration
     * @param[in] headwayTime the headway gap
     * @param[in] delta1 a model constant
	 * @param[in] delta2 a model constant
     * @param[in] internalStepping internal time step size
     */
	MSCFModel_IIDM(const MSVehicleType* vtype, SUMOReal accel, SUMOReal decel, SUMOReal emergencyDecel,
		SUMOReal headwayTime, SUMOReal delta1, SUMOReal delta2, SUMOReal internalStepping);


    /** @brief Constructor
     * @param[in] accel The maximum acceleration
     * @param[in] decel The maximum deceleration
     * @param[in] headwayTime the headway gap
     * @param[in] adaptationFactor a model constant
     * @param[in] adaptationTime a model constant
     * @param[in] internalStepping internal time step size
     */
/*	MSCFModel_IIDM(const MSVehicleType* vtype, SUMOReal accel, SUMOReal decel, SUMOReal emergencyDecel,
                  SUMOReal headwayTime, SUMOReal adaptationFactor, SUMOReal adaptationTime,
                  SUMOReal internalStepping);*/


    /// @brief Destructor
    ~MSCFModel_IIDM();


    /// @name Implementations of the MSCFModel interface
    /// @{

    /** @brief Applies interaction with stops and lane changing model influences
     * @param[in] veh The ego vehicle
     * @param[in] vPos The possible velocity
     * @return The velocity after applying interactions with stops and lane change model influences
     */
    SUMOReal moveHelper(MSVehicle* const veh, SUMOReal vPos) const;


    /** @brief Computes the vehicle's safe speed (no dawdling)
     * @param[in] veh The vehicle (EGO)
     * @param[in] speed The vehicle's speed
     * @param[in] gap2pred The (netto) distance to the LEADER
     * @param[in] predSpeed The speed of LEADER
     * @return EGO's safe speed
     * @see MSCFModel::ffeV
     */
    SUMOReal followSpeed(const MSVehicle* const veh, SUMOReal speed, SUMOReal gap2pred, SUMOReal predSpeed, SUMOReal predMaxDecel) const;


    /** @brief Computes the vehicle's safe speed for approaching a non-moving obstacle (no dawdling)
     * @param[in] veh The vehicle (EGO)
     * @param[in] gap2pred The (netto) distance to the the obstacle
     * @return EGO's safe speed for approaching a non-moving obstacle
     * @see MSCFModel::ffeS
     * @todo generic Interface, models can call for the values they need
     */
    SUMOReal stopSpeed(const MSVehicle* const veh, const SUMOReal speed, SUMOReal gap2pred) const;


    /** @brief Returns the maximum gap at which an interaction between both vehicles occurs
     *
     * "interaction" means that the LEADER influences EGO's speed.
     * @param[in] veh The EGO vehicle
     * @param[in] vL LEADER's speed
     * @return The interaction gap
     * @todo evaluate signature
     * @see MSCFModel::interactionGap
     */
    SUMOReal interactionGap(const MSVehicle* const , SUMOReal vL) const;


    /** @brief Returns the model's name
     * @return The model's name
     * @see MSCFModel::getModelName
     */
    int getModelID() const {
        return myAdaptationFactor == 1. ? SUMO_TAG_CF_IDM : SUMO_TAG_CF_IIDM;
    }
    /// @}



    /** @brief Duplicates the car-following model
     * @param[in] vtype The vehicle type this model belongs to (1:1)
     * @return A duplicate of this car-following model
     */
    MSCFModel* duplicate(const MSVehicleType* vtype) const;


    VehicleVariables* createVehicleVariables() const {
        if (myAdaptationFactor != 1.) {
            return new VehicleVariables();
        }
        return 0;
    }


private:
    class VehicleVariables : public MSCFModel::VehicleVariables {
    public:
        VehicleVariables() : levelOfService(1.) {}
        /// @brief state variable for remembering speed deviation history (lambda)
        SUMOReal levelOfService;
    };


private:
    SUMOReal _v(const MSVehicle* const veh, const SUMOReal gap2pred, const SUMOReal mySpeed,
                const SUMOReal predSpeed, const SUMOReal desSpeed, const bool respectMinGap = true) const;


private:
    /// @brief The IDM delta exponent
	const SUMOReal delta1;
	const SUMOReal delta2;

    /// @brief The IDMM adaptation factor beta
    const SUMOReal myAdaptationFactor;

    /// @brief The IDMM adaptation time tau
    const SUMOReal myAdaptationTime;

    /// @brief The number of iterations in speed calculations
    const int myIterations;

    /// @brief A computational shortcut
    const SUMOReal myTwoSqrtAccelDecel;

private:
    /// @brief Invalidated assignment operator
    MSCFModel_IIDM& operator=(const MSCFModel_IIDM& s);
};

#endif /* MSCFMODEL_IIDM_H */
