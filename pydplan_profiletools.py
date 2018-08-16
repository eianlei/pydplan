#
# (c) 2018 Ian Leiman, ian.leiman@gmail.com
# pydplan_profiletools.py
# part of PYDPLAN, a Python Dive Planner with PyQt5 GUI
# module for handling dive profile

from pydplan_classes import currentTank, DivePlan, DecoStop
from copy import deepcopy
from pydplan_buhlmann import depth2absolutePressure, Buhlmann, ModelPoint, Constants

# gradient factor object
class gradientFactor():
    def __init__(self, GFlow, GFhigh):
        self.gfSetFlag = False
        self.gfSlope = 0.0
        self.gfCurrent = GFlow
        self.GFlow = GFlow
        self.GFhigh = GFhigh
    def gfSet (self, depthNow):
        '''
        call this to set self.gfSetFlag
        :param depthNow:
        :type depthNow:
        :return:
        :rtype:
        '''
        if self.gfSetFlag == False:
            self.gfSlope = (self.GFhigh - self.GFlow) / depthNow
            self.gfCurrent = self.GFlow
            self.gfSetFlag = True
            return self.GFlow
        else:
            self.gfCurrent = self.GFhigh - (self.gfSlope * depthNow)
            return self.gfCurrent
    def gfGet(self, depthNow):
        if self.gfSetFlag == False:
            return self.GFlow
        else:
            self.gfCurrent = self.GFhigh - (self.gfSlope * depthNow)
            return self.gfCurrent

from pydplan_classes import PlanMode, TankType, ScubaTank
from enum import Enum, auto

# enumeration of dive phase state names, uses Python Enum lib, feature auto() to assign values
class DivePhase(Enum):
    INIT_TANKS = auto()
    STARTING = auto()
    DESCENDING = auto()
    BOTTOM = auto()
    ASCENDING = auto()
    STOP_DECO = auto()
    DECOEND = auto()
    SURFACE = auto()
    DESC_T = auto()
    ASC_T = auto()
    STOP_DESC_T = auto()
    STOP_ASC_T = auto()
    ERROR = auto()
    NULL = auto()


def tanksCheck(diveplan: DivePlan, divephase: DivePhase, beginDepth=0.0, endDepth=0.0,
               intervalMinutes =0.0, runtime = 0):
    '''
    checks for coming tank changes, updates pressure on current tank
    :param diveplan:
    :type diveplan:
    :param divephase:
    :type divephase:
    :param beginDepth:
    :type beginDepth:
    :param endDepth:
    :type endDepth:
    :param intervalMinutes:
    :type intervalMinutes:
    :return:
    :rtype:
    '''
    # defaults
    divephaseNext = DivePhase.NULL

    if divephase == DivePhase.INIT_TANKS:
        # make all tanks full
        diveplan.currentTank = None
        diveplan.nextTank = None
        for iTank in diveplan.tankList.keys():
            diveplan.tankList[iTank].pressure = diveplan.tankList[iTank].bar
            diveplan.tankList[iTank].useFromTime = 0
            diveplan.tankList[iTank].useFromTime2 = 0
            diveplan.tankList[iTank].useUntilTime = 0
            diveplan.tankList[iTank].useUntilTime2 = 0
        divephaseNext = DivePhase.STARTING

    elif divephase== DivePhase.STARTING:
        # select and return bottom or travel tank (B or T1),
        # if travel tank return DivePhase.DESC_CHG_TANK, and changeDepth
        if diveplan.tankList[TankType.TRAVEL].use == True:
            divephaseNext = DivePhase.DESC_T
            diveplan.changeDepth = diveplan.tankList[TankType.TRAVEL].changeDepth
            diveplan.currentTank = diveplan.tankList[TankType.TRAVEL]
            diveplan.tankList[TankType.TRAVEL].useFromTime2 = runtime
            diveplan.nextTank = diveplan.tankList[TankType.BOTTOM]
        else:
            divephaseNext = DivePhase.DESCENDING
            diveplan.currentTank = diveplan.tankList[TankType.BOTTOM]
            diveplan.currentTank.useFromTime = runtime
            if diveplan.tankList[TankType.DECO1].use == True:
                diveplan.nextTank = diveplan.tankList[TankType.DECO1]
                diveplan.changeDepth = diveplan.tankList[TankType.DECO1].changeDepth
            elif diveplan.tankList[TankType.DECO2].use == True:
                diveplan.nextTank = diveplan.tankList[TankType.DECO2]
                diveplan.changeDepth = diveplan.tankList[TankType.DECO2].changeDepth
            else:
                diveplan.nextTank = None
                diveplan.changeDepth = -1
    elif divephase == DivePhase.DESCENDING:
        # just update tank pressure
        divephaseNext = DivePhase.DESCENDING

    elif divephase == DivePhase.DESC_T:
        # just update tank pressure
        divephaseNext = DivePhase.DESC_T

    elif divephase == DivePhase.STOP_DESC_T:
        # change to next tank, which will be BOTTOM at descending
        diveplan.tankList[TankType.TRAVEL].useUntilTime2 = runtime
        diveplan.currentTank = diveplan.nextTank
        diveplan.currentTank.useFromTime = runtime
        # which means that next gas must be TRAVEL again
        diveplan.nextTank = diveplan.tankList[TankType.TRAVEL]
        divephaseNext = DivePhase.DESCENDING

    elif divephase == DivePhase.BOTTOM:
        # just update tank pressure
        divephaseNext = DivePhase.BOTTOM

    elif divephase == DivePhase.ASCENDING:
        # if any tank changes ahead, then ASC_CHG_TANK
        # if at BOTTOM tank and TRAVEL enabled, then TRAVEL comes next
        # else DECO1 or DECO2
        # if previous tank TRAVEL, then change to BOTTOM
        # if previous tank BOTTOM, then change to TRAVEL if enabled
        # else change to DECO1 if enabled, or DECO2
        if diveplan.nextTank == None:
            # there is no tank change ascending
            divephaseNext = DivePhase.ASCENDING
        else:
            divephaseNext = DivePhase.ASC_T
            diveplan.changeDepth = diveplan.nextTank.changeDepth

    elif divephase == DivePhase.ASC_T:
        # just update tank pressure
        divephaseNext = DivePhase.ASC_T

    elif divephase == DivePhase.STOP_ASC_T:
        # change to next tank, which can be TRAVEL, DECO1, DECO2
        diveplan.currentTank.useUntilTime = runtime
        diveplan.currentTank = diveplan.nextTank
        diveplan.currentTank.useFromTime = runtime
        if diveplan.currentTank == diveplan.tankList[TankType.TRAVEL]:
            # now on TRAVEL tank, check if next can be DECO1, DECO2
            if diveplan.tankList[TankType.DECO1].use == True:
                diveplan.nextTank = diveplan.tankList[TankType.DECO1]
                diveplan.changeDepth = diveplan.tankList[TankType.DECO1].changeDepth
                divephaseNext = DivePhase.ASC_T
            elif diveplan.tankList[TankType.DECO2].use == True:
                diveplan.nextTank = diveplan.tankList[TankType.DECO2]
                diveplan.changeDepth = diveplan.tankList[TankType.DECO2].changeDepth
                divephaseNext = DivePhase.ASC_T
            else:
                diveplan.nextTank = None
                diveplan.changeDepth = -1
                divephaseNext = DivePhase.ASCENDING
        elif diveplan.currentTank == diveplan.tankList[TankType.DECO1]:
            # check if DECO2 next
            if diveplan.tankList[TankType.DECO2].use == True:
                diveplan.nextTank = diveplan.tankList[TankType.DECO2]
                diveplan.changeDepth = diveplan.tankList[TankType.DECO2].changeDepth
                divephaseNext = DivePhase.ASC_T
            else:
                diveplan.nextTank = None
                diveplan.changeDepth = -1
                divephaseNext = DivePhase.ASCENDING
        elif diveplan.nextTank == diveplan.tankList[TankType.DECO2]:
            diveplan.nextTank = None
            divephaseNext = DivePhase.ASCENDING


    elif divephase == DivePhase.STOP_DECO:
        pass
    elif divephase == DivePhase.DECOEND:
        pass
    elif divephase == DivePhase.SURFACE:
        # todo: record final tank pressures
        diveplan.currentTank.useUntilTime = runtime

    else:
        print('tanksCheck: error')
        return None, -1, -1

    # calculate gas used to update tank pressure
    if diveplan.currentTank != None:
        beginPressure = depth2absolutePressure(beginDepth)
        endPressure = depth2absolutePressure(endDepth)
        surfaceLitersGasConsumed = diveplan.currentTank.SAC * intervalMinutes
        avgPressure = abs(endPressure + beginPressure) / 2
        depthLitersGasConsumed = avgPressure * surfaceLitersGasConsumed
        litersBefore = diveplan.currentTank.pressure * diveplan.currentTank.liters
        litersLeft = litersBefore - depthLitersGasConsumed
        barsLeft = litersLeft / diveplan.currentTank.liters
        # finally update new pressure into the tank itself
        diveplan.currentTank.pressure = barsLeft

    return divephaseNext


def calculatePlan(diveplan : DivePlan):
    '''Calculates a valid diveplan

    :param diveplan:
    :type diveplan:
    :return:
    :rtype:
    '''


    def calculateStepAscend(depth, interval):
        if depth > (diveplan.bottomDepth / 2.0):
            rate = diveplan.ascRateToDeco
        elif depth > 6.0:
            rate = diveplan.ascRateAtDeco
        else:
            rate = diveplan.ascRateToSurface
        return rate * interval

    gfObject = gradientFactor(GFlow= diveplan.GFlow, GFhigh= diveplan.GFhigh)

    modelConstants = Buhlmann()
    modelUsed = modelConstants.model['ZHL16c']
    diveplan.modelUsed = modelUsed
    model = ModelPoint()
    modelPoints = []
    diveplan.decoStopsCalculated = []
    model.initSurface(modelUsed)

    # reset the maximum pp values
    diveplan.maxPPoxygen = 0.0
    diveplan.maxPPhelium = 0.0
    diveplan.maxPPnitrogen = 0.0
    diveplan.maxTCnitrogen = 0.0
    diveplan.maxTChelium = 0.0

    intervalDescent = diveplan.descTime / 5.0
    stepDescent = diveplan.bottomDepth / 5.0
    intervalBottom = diveplan.bottomTime / 20.0
    intervalAscent = 5.0
    intervalDeco = 60.0
    intervalTankChange = 60.0
    # this is where we record the dive profile
    outProfile = []

    # do some intialization for Custom mode
    if diveplan.planMode == PlanMode.Custom.value:
        if len(diveplan.decoStopList)>0 :
            # we have planned deco stops, intitialize a pointer to the list
            plannedStopPointer = 0
        else:
            # no stops
            # todo: maybe add gfObject.gfSet(diveplan.bottomDepth)
            plannedStopPointer = -1

    # execute a dive
    index = 0
    tanksCheck(diveplan, DivePhase.INIT_TANKS) # intialize tanks
    # note that tanksCheck may select the diveplan.currentTank
    divephase = DivePhase.STARTING
    while True :
        index += 1
        if index > 500:
            print('index >500')
            raise ValueError('over 500 iterations, aborting')
            break

        if divephase == DivePhase.STARTING:
            runtime = 0.0
            # fixme: this should be zero?
            intervalMinutes = 0.01 #fixme?
            beginDepth = 0.0
            endDepth = 0.0
            depthSum = 0.0
            depthRunAvg = 0.0
            ascending = False
            divephase = DivePhase.DESCENDING
            newDecoStop = None
            # select the first tank to use, -> diveplan.currentTank, also affects nextTank, changeDepth
            divephase  = tanksCheck(diveplan, DivePhase.STARTING, runtime=runtime)

        elif divephase == DivePhase.DESCENDING :
            runtime += intervalDescent
            intervalMinutes = intervalDescent / 60.0
            beginDepth = endDepth
            endDepth   = beginDepth + stepDescent
            if endDepth >= diveplan.bottomDepth:
                endDepth = diveplan.bottomDepth
                divephase = DivePhase.BOTTOM
            tanksCheck(diveplan=diveplan, divephase= DivePhase.DESCENDING, beginDepth= beginDepth,
                        endDepth= endDepth, intervalMinutes= intervalMinutes, runtime=runtime)

        elif divephase == DivePhase.DESC_T :
            runtime += intervalDescent
            intervalMinutes = intervalDescent / 60.0
            beginDepth = endDepth
            endDepth   = beginDepth + stepDescent
            if endDepth >= diveplan.changeDepth:
                endDepth = diveplan.changeDepth
                divephase = DivePhase.STOP_DESC_T
            tanksCheck(diveplan, DivePhase.DESC_T, beginDepth, endDepth, intervalMinutes, runtime=runtime)

            pass
        elif divephase == DivePhase.STOP_DESC_T:
            beginDepth = endDepth
            runtime += intervalTankChange
            intervalMinutes = intervalTankChange / 60.0
            divephase = tanksCheck(diveplan, DivePhase.STOP_DESC_T,
                                   beginDepth, endDepth, intervalMinutes, runtime=runtime)


        elif divephase == DivePhase.BOTTOM:
            runtime += intervalBottom
            intervalMinutes = intervalBottom / 60.0
            beginDepth = diveplan.bottomDepth
            endDepth   = diveplan.bottomDepth
            if runtime >= (diveplan.descTime + diveplan.bottomTime):
                divephase = DivePhase.ASCENDING
                diveplan.ascentBegins = runtime # this controls many things!
                ascending = True
            tanksCheck(diveplan, DivePhase.BOTTOM, beginDepth, endDepth, intervalMinutes, runtime=runtime)


        elif divephase == DivePhase.ASCENDING:
            runtime += intervalAscent
            intervalMinutes = intervalAscent / 60.0
            beginDepth = endDepth
            stepAscend = calculateStepAscend(beginDepth, intervalAscent)
            endDepth   = beginDepth - stepAscend
            if endDepth <= 0.0:
                divephase = DivePhase.SURFACE
                beginDepth = 0.0
                endDepth = 0.0
                tanksCheck(diveplan, DivePhase.SURFACE, beginDepth, endDepth, intervalMinutes, runtime=runtime)
            else:
                divephase = tanksCheck(diveplan, DivePhase.ASCENDING,
                                                      beginDepth, endDepth, intervalMinutes, runtime=runtime)

        elif divephase == DivePhase.ASC_T:
            runtime += intervalAscent
            intervalMinutes = intervalAscent / 60.0
            beginDepth = endDepth
            stepAscend = calculateStepAscend(beginDepth, intervalAscent)
            endDepth   = beginDepth - stepAscend
            if endDepth <= diveplan.changeDepth:
                endDepth = diveplan.changeDepth
                divephase = DivePhase.STOP_ASC_T
            tanksCheck(diveplan, DivePhase.ASC_T, beginDepth, endDepth, intervalMinutes, runtime=runtime)
            pass

        elif divephase == DivePhase.STOP_ASC_T:
            beginDepth = endDepth
            runtime += intervalTankChange
            intervalMinutes = intervalTankChange / 60.0
            divephase = tanksCheck(diveplan, DivePhase.STOP_ASC_T,
                                   beginDepth, endDepth, intervalMinutes, runtime=runtime)
            #print('+ STOP_CHG_TANK_ASC at {} m '.format(endDepth))

        elif divephase == DivePhase.STOP_DECO:
            runtime += intervalDeco
            intervalMinutes = intervalDeco / 60.0
            tanksCheck(diveplan, DivePhase.STOP_DECO, beginDepth, endDepth, intervalMinutes, runtime=runtime)

        elif divephase ==  DivePhase.DECOEND:
            runtime += intervalDeco
            intervalMinutes = intervalDeco / 60.0
            divephase = DivePhase.ASCENDING
            tanksCheck(diveplan, DivePhase.DECOEND, beginDepth, endDepth, intervalMinutes, runtime=runtime)

        elif divephase == DivePhase.SURFACE:
            tank.useUntilTime = runtime
            tanksCheck(diveplan, DivePhase.SURFACE, beginDepth, endDepth, 0.1, runtime=runtime)
            break
        else:
            break

        tank = diveplan.currentTank
        newPoint = DiveProfilePoint(runtime, endDepth, tank, divephase=divephase,
                                    gfSet=gfObject.gfSetFlag, ascending=ascending)
        newPoint.gfNow = gfObject.gfGet(endDepth)
        depthSum += endDepth * intervalMinutes
        depthRunAvg = depthSum / (float(runtime +0.001) / 60.0)
        newPoint.depthRunAvg = depthRunAvg
        newPoint.currentTankPressure = tank.pressure

        heliumFraction = tank.he / 100.0 # convert percentage to ratio
        oxygenFraction = tank.o2 / 100.0
        nitrogenFraction = 1.0 - heliumFraction - oxygenFraction
        # record the current Partial Pressures of all gases breathed
        newPoint.ppOxygen   = newPoint.pressure * oxygenFraction / Constants.surfacePressure
        newPoint.ppNitrogen = newPoint.pressure * nitrogenFraction / Constants.surfacePressure
        newPoint.ppHelium   = newPoint.pressure * heliumFraction / Constants.surfacePressure
        # record the maximum Partial Pressures
        diveplan.maxPPoxygen = max(diveplan.maxPPoxygen, newPoint.ppOxygen)
        diveplan.maxPPhelium = max(diveplan.maxPPhelium, newPoint.ppHelium)
        diveplan.maxPPnitrogen = max(diveplan.maxPPnitrogen, newPoint.ppNitrogen)
        diveplan.maxPPanyGas = max(diveplan.maxPPoxygen, diveplan.maxPPhelium, diveplan.maxPPnitrogen)

        # do the model calculation for all tissue compartments
        model.calculateAllTissuesDepth(modelUsed = modelUsed,
                                  beginDepth= beginDepth, endDepth= endDepth,
                                  intervalMinutes= intervalMinutes,
                                  heliumFraction= heliumFraction, nitrogenFraction = nitrogenFraction,
                                  gfNow= gfObject.gfGet(endDepth))

        # search and record max N2, He TC pressures
        diveplan.maxTCnitrogen = max(diveplan.maxTCnitrogen, model.maxNitrogenPressure)
        diveplan.maxTChelium = max(diveplan.maxTChelium, model.maxHeliumPressure)

        # then deepcopy and append the model state to the list of model states
        modelCopy = deepcopy( model)        # must deepcopy to keep a snapshot of what the state was here
        modelPoints.append(modelCopy)       # append to the list of saved model states
        newPoint.modelpoint = modelCopy     # also link the model point to the profile point
        outProfile.append(newPoint)         # append to the list of dive  profile

        # here we start the deco stops when ascending, or check if deco stop can be ended
        if divephase in [DivePhase.ASCENDING, DivePhase.STOP_DECO, DivePhase.ASC_T,
                         DivePhase.STOP_ASC_T]:
            # which mode of operation: 'Custom', 'Calculate', 'Import'
            if diveplan.planMode == PlanMode.Calculate.value:
                # we are in Calculate mode, check that next step will not cross ceiling
                if endDepth <= model.leadCeilingStop and divephase != DivePhase.STOP_DECO:
                    # we have hit a deco ceiling, check if starting or ongoing deco
                    divephase = DivePhase.STOP_DECO
                    currentDecoDone = 0.0
                    # force the next depth to be at the step
                    beginDepth= model.leadCeilingStop
                    endDepth= beginDepth
                    # now set the gradient factor
                    newPoint.gfNow = gfObject.gfSet(endDepth)
                    newPoint.gfSet = True
                    # the decos near surface take longer, so longer intervals used
                    if beginDepth == 3.0:
                        intervalDeco = 180.0
                    elif beginDepth == 6.0:
                        intervalDeco = 120.0
                    else:
                        intervalDeco = 60.0
                    #record the new deco stop
                    newDecoStop = DecoStop(depth=beginDepth, time=0.0, number=0)
                    newDecoStop.runtime = runtime
                elif divephase == DivePhase.STOP_DECO:
                    # ongoing deco stop, increment the timer
                    currentDecoDone += intervalDeco
                    #todo: check long it has been now?
                    if newDecoStop != None:
                        newDecoStop.time = currentDecoDone
                    # check if time to end deco
                    if endDepth  > model.leadCeilingMeters + 3.0:
                        divephase = DivePhase.ASCENDING
                        diveplan.decoStopsCalculated.append(newDecoStop)
                        newDecoStop = None
                        #divephase = DivePhase.DECOEND

            ############ check if in Custom mode ########################
            elif diveplan.planMode == PlanMode.Custom.value:
                # we are in Custom mode, check if planned deco stop here
                if plannedStopPointer >= 0:
                    # yes we have planned deco stops
                    if divephase in [DivePhase.ASCENDING, DivePhase.ASC_T]:
                        # check if we have planned deco stop here
                        # fixme: we should test for next step, instead of current depth that might already be above the stop
                        if endDepth <= diveplan.decoStopList[plannedStopPointer].depth :
                            # so start a deco stop and reset timer
                            divephase = DivePhase.STOP_DECO
                            diveplan.decoStopList[plannedStopPointer].done = 0.0
                            newPoint.depth = diveplan.decoStopList[plannedStopPointer].depth
                            endDepth = newPoint.depth
                            beginDepth  = newPoint.depth
                            # now set the gradient factor
                            newPoint.gfNow = gfObject.gfSet(endDepth)
                            newPoint.gfSet = True
                    elif divephase == DivePhase.STOP_DECO:
                        # planned deco stop ongoing, increment timer, check if then done with it
                        diveplan.decoStopList[plannedStopPointer].done += intervalDeco
                        if diveplan.decoStopList[plannedStopPointer].done >= \
                                diveplan.decoStopList[plannedStopPointer].time:
                            # we have done the deco, now start ascending again
                            divephase = DivePhase.ASCENDING
                            plannedStopPointer += 1
                            if plannedStopPointer >= len(diveplan.decoStopList):
                                # we have consumed the list of deco stops, stop checking for them
                                plannedStopPointer = -1
                pass
            else:
                # getting here is actually a disastrous bug, should handle it more seriously...
                print('unsupported mode')
                break

    # dive has ended, now save the data for plotting and printing
    diveplan.profileSampled = outProfile
    diveplan.model = modelPoints
    return modelPoints


class DiveProfilePoint():
    def __init__(self, pTime, pDepth, tank, divephase=DivePhase.NULL, gfSet = False, ascending = False):
        '''
        Object to store a point in executed dive profile, append these into a list to store the entire profile
        :param pTime:
        :type pTime:
        :param pDepth:
        :type pDepth:
        :param tank:
        :type tank:
        :param divephase:
        :type divephase:
        :param gfSet:
        :type gfSet:
        :param ascending:
        :type ascending:
        '''
        self.time = float(pTime)           # current time in seconds, float
        self.depth = float(pDepth)  # current depth in meters, a float
        self.pressure = depth2absolutePressure(pDepth)
        self.divephase = divephase
        self.tank = tank
        self.modelpoint = None
        #self.ceilings_all = []  # list of ceiling depths per each tissue compartment

        self.leadTC_now = -1
        self.ceiling_now = 0
        self.ceiling_now_3m = 0
        self.gfNow = 1.0
        self.gfSet = gfSet
        self.ascending = ascending

        self.depthRunAvg = 0.0
        self.ppOxygen = 0.0
        self.ppHelium = 0.0
        self.ppNitrogen = 0.0

        self.currentTankPressure = 0.0

    def ppOxygenGet(self):
        return self.ppOxygen

