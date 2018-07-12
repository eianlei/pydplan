from PyQt5.QtCore import Qt
from pydplan.pydplan_buhlmann import Buhlmann

from enum import Enum, auto


class PlanMode(Enum):
    Custom = 1
    Calculate = 0
    Import = 2

class TankType(Enum):
    BOTTOM = auto()
    DECO1 = auto()
    DECO2 = auto()
    TRAVEL = auto()

class DivePlan():
    def __init__(self):
        self.GFhigh = 1.0
        self.GFlow = 1.0
        self.planMode = PlanMode.Calculate.value
        self.widgetsCtrl = dict()
        self.objectOfWidget = dict()
        # profileSegments = []
        self.profileSampled = []
        self.stopListUI = dict()
        self.tankList = dict()
        self.currentTank = None
        self.nextTank = None
        self.changeDepth = -1
        self.currentDepth = 0
        self.currentRuntime = 0
        self.rates = dict()
        self.model = []
        self.modelUsed = []
        self.modelConstants = None
        self.PGplot = 'Total'
        self.tcSelected = 0
        self.maxDepth = 0.0
        self.bottomDepth = 0.0
        self.bottomTime = 0.0
        self.descRate = 0.0
        self.descTime = 0.0
        self.ascRateToDeco = 0.0
        self.ascRateAtDeco = 0.0
        self.ascRateToSurface  = 0.0
        self.stopCount = 0
        self.decoStopList = []
        self.decoStopsCalculated = []
        # capture maximum values
        self.maxPPoxygen = 0.0
        self.maxPPnitrogen = 0.0
        self.maxPPhelium = 0.0
        self.maxPPanyGas = 0.0
        self.maxTCpressure = 0.0
        self.maxTCnitrogen = 0.0
        self.maxTChelium = 0.0

    def setDefaults(self):
        self.GFhigh = 0.80
        self.GFlow = 0.30
        self.modelConstants = Buhlmann()

        self.ascentBegins = 0
        self.stopListUI = {
            'deco1': {'depth': 27, 'time': 0, 'gas': '-/-'},
            'deco2': {'depth': 24, 'time': 0, 'gas': '-/-'},
            'deco3': {'depth': 21, 'time': 3, 'gas': '50/0'},
            'deco4': {'depth': 18, 'time': 0, 'gas': '50/0'},
            'deco5': {'depth': 15, 'time': 1, 'gas': '50/0'},
            'deco6': {'depth': 12, 'time': 1, 'gas': '50/0'},
            'deco7': {'depth': 9, 'time': 3, 'gas': '50/0'},
            'deco8': {'depth': 6, 'time': 5, 'gas': '100/0'},
            'deco9': {'depth': 3, 'time': 6, 'gas': '100/0'},
        }

        self.tankList = {
            TankType.BOTTOM:
                ScubaTank(label = 'Bottom', name ='B', use=True,
                          o2 = 21, he= 35,
                          SAC = 15, ppo2max = 1.4,
                          liters=24.0, bar=200.0, pressure=200.0,
                          useFromTime= 0, useUntilTime=0,
                          type='bottom', useOrder = 1, color = Qt.magenta),
            TankType.DECO1:
                ScubaTank(label = 'deco 1', name ='D1', use=True,
                          o2 = 50, he= 0,
                          changeDepth = 21.0,
                          SAC=13, ppo2max=1.6,
                          liters=7.0, bar=200.0, pressure=200.0,
                          useFromTime= 0, useUntilTime=0,
                          type='deco', useOrder = 2, color = Qt.cyan),
            TankType.DECO2:
                ScubaTank(label = 'deco 2', name ='D2', use=True,
                          o2 = 100, he= 0,
                          changeDepth= 6.0,
                          SAC=13, ppo2max=1.6,
                          liters=7.0, bar=200.0, pressure=200.0,
                          useFromTime= 0, useUntilTime=0,
                          type='deco', useOrder = 3, color = Qt.darkGray),
            TankType.TRAVEL:
                ScubaTank(label = 'travel 1', name ='T1', use=False,
                          o2 = 21, he= 25,
                          changeDepth = 40.0,
                          SAC=16, ppo2max=1.4,
                          liters=11.0, bar=200.0, pressure=200.0,
                          useFromTime= 0, useUntilTime=0,
                          useFromTime2=0, useUntilTime2=0,
                          type='travel', useOrder = 0, color = Qt.yellow),
        }
        self.rates = {
            'descent' : {'label': 'descent rate, surface to bottom', 'default': 20},
            'ascBelow75': {'label': 'ascent rate below 75% max depth', 'default': 9},
            'ascBelow50': {'label': 'ascent rate 75% to 50% max depth', 'default': 9},
            'ascBelow6m': {'label': 'ascent rate from 50% max depth to 6 m', 'default': 6},
            'ascToSurface': {'label': 'ascent rate from 6 m to surface', 'default': 3},
        }

class DecoStop():
    def __init__(self, depth, time, number):
        self.depth = depth
        self.time = time
        self.number = number
        self.done = 0.0
        self.runtime = 0.0

class ScubaTank():
    def __init__(self, label, name, use,  o2, he,
                 liters, bar, pressure, SAC, ppo2max,
                 useFromTime, useUntilTime,
                 type, useOrder, color,
                 changeDepth = 0.0,
                 useFromTime2=0.0, useUntilTime2=0.0,
                 ):
        self.label = label
        self.name = name
        self.use = use
        self.changeDepth = changeDepth
        self.o2 = o2
        self.he = he
        self.liters = liters
        self.bar = bar
        self.pressure = pressure
        self.SAC = SAC
        self.ppo2max = ppo2max

        self.useFromTime = useFromTime
        self.useUntilTime = useUntilTime
        self.useFromTime2 = useFromTime2
        self.useUntilTime2 = useUntilTime2

        self.type = type
        self.useOrder = useOrder
        self.color = color
    def setO2(self, new):
        self.o2 = new
    def setHe(self, new):
        self.he = new
    def setUse(self, state):
        self.use = state
    def setLiters(self, new):
        self.liters = new
    def setSAC(self, new):
        self.SAC = new
    def setBar(self, new):
        self.bar = new
    def setChangeDepth(self, new):
        self.changeDepth = new
    def setPPo2max(self, new):
        self.ppo2max = new

def currentTank(tanks, depth, type):
        if type == 'bottom' :
            for tank in tanks.keys():
                if type == tanks[tank].type :
                    return tanks[tank]
        if type == 'deco':
            for tank in tanks.keys() :
                if type == tanks[tank].type and \
                    depth <= tanks[tank].useFromDepth and \
                    depth >= tanks[tank].useUntilDepth and \
                        tanks[tank].use == True  :
                    return tanks[tank]

        return None

