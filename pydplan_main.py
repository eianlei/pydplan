#!/usr/bin/python
# (c) 2018 Ian Leiman, ian.leiman@gmail.com
# pydplan_main
# main module for PYDPLAN, a Python Dive Planner with PyQt5 GUI


# import modules, like PyQt5 stuff
from pydplan_classes import DivePlan, DecoStop
from pydplan_plot import PlotPlanWidget, PlotBelowWidget, PlotPressureGraphWidget, \
    PlotTissuesWidget
from pydplan_table import *
from pydplan_bars import *
from pydplan_heat import *
from pydplan_profiletools import calculatePlan
from pydplan_classes import PlanMode

from PyQt5.QtCore import Qt
from PyQt5.QtGui import  QPalette
from PyQt5.QtWidgets import *

globalDivePlan =  None

# define the main window GUI objects and callbacks
class pydplan_main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.divePlan = DivePlan()
        self.divePlan.setDefaults()
        global globalDivePlan
        globalDivePlan = self.divePlan

        # define the main window structure, menu bar, tool bar, MDI area, status bar
        self.menubar = self.menuBar()                 # menu bar

        ## toolbar buttons for main actions
        toolBar = False
        if toolBar == True:
            self.toolbar = self.addToolBar('tools')  # tool bar
            qa_B1_exec  = QAction("B1", self)
            self.toolbar.addAction(qa_B1_exec)
            self.toolbar.actionTriggered[QAction].connect(self.r_tool_B1_pressed)

        central = QWidget()
        lay_main = QHBoxLayout()

        # create tabbed control panels to left side
        self.tabAllControls = QTabWidget()

        # TAB Plan
        PlanCtrlW = self.initPlanCtrl()
        self.tabAllControls.addTab(PlanCtrlW, 'Plan')

        # TAB Tanks
        tankCtrl = self.initTankCtrl2()
        self.tabAllControls.addTab(tankCtrl, 'Tanks')

        # TAB Model
        modelCtrl = self.initModelCtrl()
        self.tabAllControls.addTab(modelCtrl, 'Model')


        # create tabbed output panels to right hand side
        self.tabOutputs = QTabWidget()

        # PROFILE TAB
        plotPanelWidget = QWidget()
        plotPanelLay = QVBoxLayout()
        splitPlot = QSplitter(Qt.Vertical)
        self.plotPlan = PlotPlanWidget(self.divePlan)
        self.plotPlan.setMinimumWidth(600)
        self.plotPlan.setMinimumHeight(100)
        self.plotBelow = PlotBelowWidget(self.divePlan)
        self.plotBelow.setMinimumHeight(100)
        self.plotBelow.setGeometry(0,0,600, 100)
        splitPlot.addWidget(self.plotPlan)
        splitPlot.addWidget(self.plotBelow)
        plotPanelLay.addWidget(splitPlot)
        plotPanelWidget.setLayout(plotPanelLay)
        self.tabOutputs.addTab(plotPanelWidget, 'Profile')

        # TABLE TAB
        self.tableModel = QTableWidget()
        self.tableModel.setRowCount(100)
        self.tableModel.setColumnCount(2)
        self.tabOutputs.addTab(self.tableModel, 'TABLE')

        # PRESSURE GRAPH
        self.pg =PlotPressureGraphWidget(self.divePlan)
        self.pg.setMinimumWidth(600)
        self.tabOutputs.addTab(self.pg, 'PG')

        # Tissue Compartment
        self.pressure = PlotTissuesWidget(self.divePlan)
        self.pressure.setMinimumWidth(600)
        self.tabOutputs.addTab(self.pressure, 'TC Pressures')

        # compartment bar display
        barsW = QWidget()
        barsLayout = QVBoxLayout()
        barsW.setLayout(barsLayout)
        self.tcBars = PlotTCbarsWidget(self.divePlan)
        self.tcSlider = QSlider(Qt.Horizontal)
        self.tcSlider.setMinimum(0)
        self.tcSlider.setMaximum (200)
        self.tcSlider.setValue(0)
        self.tcSlider.setTickInterval(5)
        self.tcSlider.setSingleStep(1)
        self.tcSlider.setFocusPolicy(Qt.StrongFocus)
        self.tcSlider.setTickPosition(QSlider.TicksBelow)
        self.divePlan.widgetsCtrl['tcSlider'] = self.tcSlider
        self.tcSlider.valueChanged.connect(self.tcSliderChanged)
        barsLayout.addWidget(self.tcSlider)
        barsLayout.addWidget(self.tcBars)
        self.tabOutputs.addTab(barsW, 'Bars')

        # Heat Map
        self.heatW = PlotHeatMapWidget(self.divePlan)
        self.tabOutputs.addTab(self.heatW, 'Heat')

        # Plan print
        self.planout = QWidget()
        self.tabOutputs.addTab(self.planout, 'Plan')

#################################################################################
# control panels to the left, output panels to right, splitter between
        splitter = QSplitter()
        splitter.addWidget(self.tabAllControls)
        splitter.addWidget(self.tabOutputs)
        lay_main.addWidget(splitter)

        central.setLayout(lay_main)
        self.setCentralWidget(central)

        self.drawNewProfile()
        self.show()

        # define one exit action
        exitAct = QAction('exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        # menu items
        r_menu_file = self.menubar.addMenu('&File')
        r_menu_file.addAction(exitAct)
        self.r_menu_win = self.menubar.addMenu('&Window')
        self.r_menu_win = self.menubar.addMenu('&Help')

        # resize, window title, and we are done
        self.resize(1000,600)
        self.setWindowTitle("pydplan dive planner prototype")
        self.show()

    # handler for toolbar buttons
    def r_tool_B1_pressed(self, qact):
        print('toolbar button pressed')

    # lay out the control widgets for dive profile planning
    def initPlanCtrl(self):
        PlanCtrlW = QWidget()
        lay = QGridLayout()
        PlanCtrlW.setLayout(lay)
        PlanCtrlW.setMinimumWidth(300)

        palette1 = QPalette()
        palette1.setColor(QPalette.Background, Qt.white)

        controls = {}
        # row 0
        row = 0
        lay.addWidget(QLabel('<b>Profile plan<\b>'), row, 0)
        lay.addWidget(QLabel('depth (m)'), row, 1)
        lay.addWidget(QLabel('time (min)'), row, 2)
        lay.addWidget(QLabel('gas used'), row, 3)
        # row 1
        row += 1
        lay.addWidget(QLabel('Bottom:'), row, 0)
        controls['depth'] = QSpinBox()
        controls['depth'].setValue(50)
        controls['depth'].setMinimum(20)
        controls['depth'].setMaximum(200)
        controls['depth'].valueChanged.connect(self.drawNewProfile)
        lay.addWidget(controls['depth'], row, 1)
        controls['time'] = QSpinBox()
        controls['time'].setValue(20)
        controls['time'].setMinimum(5)
        controls['time'].setMaximum(99)
        controls['time'].valueChanged.connect(self.drawNewProfile)
        lay.addWidget(controls['time'], row, 2)
        controls['gas'] = QLabel('21/35')
        controls['gas'].setAutoFillBackground(True)
        controls['gas'].setPalette(palette1)
        lay.addWidget(controls['gas'], row, 3)
        self.divePlan.widgetsCtrl['bottom'] = controls

        row += 1
        planAlterativesTabs = QTabWidget()

        planCalculCtrlW = self.initPlanCalcControls()
        planImportCtrlW = QWidget()
        planCustomCtrlW = self.initPlanCustomControls()

        ### lay out tabs
        planAlterativesTabs.addTab(planCalculCtrlW, PlanMode.Calculate.name)
        planAlterativesTabs.addTab(planCustomCtrlW, PlanMode.Custom.name)
        planAlterativesTabs.addTab(planImportCtrlW, PlanMode.Import.name)
        lay.addWidget(planAlterativesTabs, row, 0, 1, 4)
        planAlterativesTabs.currentChanged.connect(self.planTabChanged)

        row += 1
        f1 = QFrame()
        f1.setFrameShape(QFrame.HLine)
        lay.addWidget(f1, row, 0, 1, 4)

        row += 1
        lay.addWidget(QLabel('TOTAL TIME (min)'), row, 0, 1, 2)
        self.divePlan.widgetsCtrl['totalTime'] = QLabel('000')
        self.divePlan.widgetsCtrl['totalTime'].setAutoFillBackground(True)
        self.divePlan.widgetsCtrl['totalTime'].setPalette(palette1)
        lay.addWidget(self.divePlan.widgetsCtrl['totalTime'], row, 2)
        row += 1
        lay.addWidget(QLabel('AVERAGE DEPTH (m)'), row, 0, 1, 2)
        self.divePlan.widgetsCtrl['avgDepth'] = QLabel('000')
        self.divePlan.widgetsCtrl['avgDepth'].setAutoFillBackground(True)
        self.divePlan.widgetsCtrl['avgDepth'].setPalette(palette1)
        lay.addWidget(self.divePlan.widgetsCtrl['avgDepth'], row, 2)

        row += 1
        f1 = QFrame()
        f1.setFrameShape(QFrame.HLine)
        lay.addWidget(f1, row, 0, 1, 4)

        # descent and ascent rates
        spCol = 3
        labelSpan = 3
        row += 1
        lay.addWidget(QLabel('rate (m/min)'), row, spCol)
        row += 1

        for key in self.divePlan.rates.keys():
            rate = self.divePlan.rates[key]
            lay.addWidget(QLabel(rate['label']), row, 0, 1, labelSpan)
            self.divePlan.widgetsCtrl[key] = QSpinBox()
            self.divePlan.widgetsCtrl[key].setValue(rate['default'])
            self.divePlan.widgetsCtrl[key].valueChanged.connect(self.drawNewProfile)
            lay.addWidget(self.divePlan.widgetsCtrl[key], row, spCol)
            row += 1

        row += 1
        f1 = QFrame()
        f1.setFrameShape(QFrame.HLine)
        lay.addWidget(f1, row, 0, 1, 4)


        lay.setAlignment(Qt.AlignTop)
        return PlanCtrlW

    def initTankCtrl(self):
        tankCtrl = QWidget()
        lay = QGridLayout()
        tankCtrl.setLayout(lay)
        # gases
        row = 0
        lay.addWidget(QLabel('tank'), row, 0)
        lay.addWidget(QLabel('use'), row, 1)
        lay.addWidget(QLabel('O2%'), row, 2)
        lay.addWidget(QLabel('He%'), row, 3)
        lay.addWidget(QLabel('from'), row, 4)
        lay.addWidget(QLabel('to'), row, 5)
        #lay.addWidget(QLabel('use/change at'), row, 3)

        for tank in self.divePlan.tankList.keys():
            thisGas = self.divePlan.tankList[tank]
            controls = {}
            row += 1
            lay.addWidget(QLabel(thisGas.label), row, 0)

            key = 'use'
            controls[key] = QCheckBox()
            lay.addWidget(controls[key], row, 1 )
            controls[key].setChecked(thisGas.use)
            self.divePlan.objectOfWidget[controls[key]] = thisGas.setUse
            controls[key].stateChanged.connect (self.tankUseChange)

            key = 'oxygen'
            controls[key] = QSpinBox()
            controls[key].setRange(0, 100)
            controls[key].setValue(thisGas.o2)
            self.divePlan.objectOfWidget[controls[key]] = thisGas.setO2
            controls[key].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key], row, 2 )

            key = 'helium'
            controls[key] = QSpinBox()
            controls[key].setRange(0, 100)
            controls[key].setValue(thisGas.he)
            self.divePlan.objectOfWidget[controls[key]] = thisGas.setHe
            controls[key].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key], row, 3 )

            key = 'from'
            controls[key] = QSpinBox()
            controls[key].setRange(0, 100)
            controls[key].setValue(thisGas.changeDepth)
            #self.divePlan.objectOfWidget[controls['from']] = thisGas.setHe
            #controls['from'].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key], row, 4 )



        row += 1
        f1 = QFrame()
        f1.setFrameShape(QFrame.HLine)
        lay.addWidget(f1, row, 0, 1, 4)
        row += 1
        lay.addWidget(QLabel('tank'), row, 0)
        lay.addWidget(QLabel('liters'), row, 1)
        lay.addWidget(QLabel('start (bar)'), row, 2)
        lay.addWidget(QLabel('SAC'), row, 3)
        lay.addWidget(QLabel('ppo2max'), row, 4)
        for tank in self.divePlan.tankList.keys():
            thisGas = self.divePlan.tankList[tank]
            row += 1
            lay.addWidget(QLabel(thisGas.label), row, 0)

            key = 'liters'
            controls[key] = QSpinBox()
            controls[key].setRange(1, 50)
            controls[key].setValue(thisGas.liters)
            #self.divePlan.objectOfWidget[controls[key]] = thisGas.setO2
            #controls[key].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key], row, 1 )

            key = 'bar'
            controls[key] = QSpinBox()
            controls[key].setRange(1, 300)
            controls[key].setValue(thisGas.bar)
            #self.divePlan.objectOfWidget[controls[key]] = thisGas.setO2
            #controls[key].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key], row, 2 )

            key = 'SAC'
            controls[key] = QSpinBox()
            controls[key].setRange(5, 50)
            controls[key].setValue(thisGas.SAC)
            #self.divePlan.objectOfWidget[controls[key]] = thisGas.setO2
            #controls[key].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key], row, 3 )

            key = 'ppo2max'
            controls[key] = QDoubleSpinBox()
            controls[key].setRange(1.0, 2.0)
            controls[key].setValue(thisGas.ppo2max)
            #self.divePlan.objectOfWidget[controls[key]] = thisGas.setO2
            #controls[key].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key], row, 4 )

        lay.setAlignment(Qt.AlignTop)
        return tankCtrl

    def initTankCtrl2(self):
        tankCtrl = QWidget()
        lay = QGridLayout()
        tankCtrl.setLayout(lay)

        lay.addWidget(QLabel('<b>tank:</b>'), 0, 0)
        lay.addWidget(QLabel('used'), 1, 0)
        lay.addWidget(QLabel('O2%'),  2, 0)
        lay.addWidget(QLabel('He%'),  3, 0)
        lay.addWidget(QLabel('ppO2 max'), 4, 0)
        lay.addWidget(QLabel('MOD'),  5, 0)
        lay.addWidget(QLabel('Min depth'),  6, 0)
        lay.addWidget(QLabel('change gas depth (m)'), 7, 0, 1, 2)
        lay.addWidget(QLabel('liters'), 8, 0)
        lay.addWidget(QLabel('start (bar)'), 9, 0)
        lay.addWidget(QLabel('SAC (L/min)'), 10, 0)
        lay.addWidget(QLabel('end (bar)'), 11, 0)

        allcontrols = {}

        col = 1
        for tank in self.divePlan.tankList.keys():
            controls = {}
            thisGas = self.divePlan.tankList[tank]
            lay.addWidget(QLabel('<b>{}</b>'.format(thisGas.label)), 0, col)

            key = 'use'
            if thisGas.name != 'B': # bottom gas cannot be deselected
                controls[key] = QCheckBox()
                lay.addWidget(controls[key], 1, col )
                controls[key].setChecked(thisGas.use)
                self.divePlan.objectOfWidget[controls[key]] = thisGas.setUse
                controls[key].stateChanged.connect (self.tankUseChange)
            else:
                lay.addWidget(QLabel('YES'), 1, col)

            key = 'oxygen'
            controls[key] = QSpinBox()
            controls[key].setRange(0, 100)
            controls[key].setValue(thisGas.o2)
            self.divePlan.objectOfWidget[controls[key]] = thisGas.setO2
            controls[key].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key], 2, col )

            key = 'helium'
            controls[key] = QSpinBox()
            controls[key].setRange(0, 100)
            controls[key].setValue(thisGas.he)
            self.divePlan.objectOfWidget[controls[key]] = thisGas.setHe
            controls[key].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key], 3, col )

            key = 'ppo2max'
            controls[key] = QDoubleSpinBox()
            controls[key].setRange(1.0, 2.0)
            controls[key].setSingleStep(0.1)
            controls[key].setValue(thisGas.ppo2max)
            self.divePlan.objectOfWidget[controls[key]] = thisGas.setPPo2max
            controls[key].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key], 4, col )

            lay.addWidget(QLabel('--'), 5, col)
            lay.addWidget(QLabel('--'), 6, col)

            if thisGas.name != 'B': # bottom gas change n/a
                key = 'change'
                controls[key] = QSpinBox()
                controls[key].setRange(1, 100)
                controls[key].setValue(thisGas.changeDepth)
                self.divePlan.objectOfWidget[controls[key]] = thisGas.setChangeDepth
                controls[key].valueChanged.connect(self.tankConfigChange)
                lay.addWidget(controls[key], 7, col )

            key = 'liters'
            controls[key] = QSpinBox()
            controls[key].setRange(1, 50)
            controls[key].setValue(thisGas.liters)
            self.divePlan.objectOfWidget[controls[key]] = thisGas.setLiters
            controls[key].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key],  8, col )

            key = 'bar'
            controls[key] = QSpinBox()
            controls[key].setRange(1, 300)
            controls[key].setValue(thisGas.bar)
            self.divePlan.objectOfWidget[controls[key]] = thisGas.setBar
            controls[key].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key], 9, col )

            key = 'SAC'
            controls[key] = QSpinBox()
            controls[key].setRange(5, 50)
            controls[key].setValue(thisGas.SAC)
            self.divePlan.objectOfWidget[controls[key]] = thisGas.setSAC
            controls[key].valueChanged.connect(self.tankConfigChange)
            lay.addWidget(controls[key], 10, col )

            key = 'endbar'
            controls[key] = QLabel('n/a')
            lay.addWidget(controls[key], 11, col)

            col += 1
            allcontrols[thisGas.name] = controls

        self.divePlan.widgetsCtrl['tanks'] = allcontrols
        lay.setAlignment(Qt.AlignTop)
        return tankCtrl

    def initPlanCustomControls(self):
        planCustomCtrlW = QWidget()
        lay = QGridLayout()
        planCustomCtrlW.setLayout(lay)
        palette1 = QPalette()
        palette1.setColor(QPalette.Background, Qt.white)

        # rows 2 to 8 for deco stops
        row = 0
        for decoStop in self.divePlan.stopListUI.keys():
            thisStop = self.divePlan.stopListUI[decoStop]
            controls = {}

            labelTxt = 'stop {}'.format(decoStop)
            lay.addWidget(QLabel(labelTxt), row, 0)
            controls['depth']  = QSpinBox()
            controls['depth'].setValue(thisStop['depth'])
            lay.addWidget(controls['depth'] , row, 1)
            controls['time'] = QSpinBox()
            controls['time'].setValue(thisStop['time'])
            controls['time'].valueChanged.connect(self.drawNewProfile)
            lay.addWidget(controls['time'], row, 2)
            controls['gas'] = QLabel(thisStop['gas'])
            controls['gas'].setAutoFillBackground(True)
            controls['gas'].setPalette(palette1)
            lay.addWidget(controls['gas'], row, 3)
            self.divePlan.widgetsCtrl[decoStop] = controls
            row += 1

        lay.setAlignment(Qt.AlignTop)
        return planCustomCtrlW

    def initPlanCalcControls(self):
        thisWidget = QWidget()
        lay = QGridLayout()
        thisWidget.setLayout(lay)
        calcDecoLabel = QLabel('deco stops:')
        calcDecoLabel.setFont(QtGui.QFont("Courier",8))
        lay.addWidget(calcDecoLabel)
        lay.setAlignment(Qt.AlignTop)

        self.divePlan.widgetsCtrl['calcDecoLabel'] = calcDecoLabel
        return thisWidget

    def initModelCtrl(self):
        modelCtrl = QWidget()
        lay = QGridLayout()
        modelCtrl.setLayout(lay)

        row = 0
        controls = {}
        lay.addWidget(QLabel('Bühlmann model:'), row, 0)
        key = 'modelSelect'
        controls[key] = QComboBox()
        controls[key].addItems( self.divePlan.modelConstants.model.keys())
        controls[key].setCurrentText ('ZHL16c')
        #controls[key].currentIndexChanged.connect(self.PGplotChanged)
        lay.addWidget(controls[key], row, 2)

        row += 1
        lay.addWidget(QLabel('GF'), row, 0)
        lay.addWidget(QLabel('GF low %'), row, 1)
        lay.addWidget(QLabel('GF high %'), row, 2)

        row += 1
        lay.addWidget(QLabel('Gradient Factors:'), row, 0)

        key = 'GF_low'
        controls[key] = QSpinBox()
        controls[key].setRange(1, 100)
        controls[key].setValue(30)
        controls[key].setMinimum(10)
        controls[key].setMaximum(80)
        controls[key].valueChanged.connect(self.gfLowChanged)
        lay.addWidget(controls[key], row, 1)

        key = 'GF_high'
        controls[key] = QSpinBox()
        controls[key].setRange(1, 100)
        controls[key].setValue(80)
        controls[key].setMinimum(31)
        controls[key].setMaximum(100)
        controls[key].valueChanged.connect(self.gfHighChanged)
        lay.addWidget(controls[key], row, 2)

        row += 1
        f1 = QFrame()
        f1.setFrameShape(QFrame.HLine)
        lay.addWidget(f1, row, 0, 1, 4)

        row += 1
        lay.addWidget(QLabel('PG plot:'), row, 0)
        key = 'PGplot'
        controls[key] = QComboBox()
        controls[key].addItems(['Total', 'Nitrogen', 'Helium'])
        controls[key].setCurrentText ('Total')
        controls[key].currentIndexChanged.connect(self.PGplotChanged)
        lay.addWidget(controls[key], row, 2)

        row += 1
        f1 = QFrame()
        f1.setFrameShape(QFrame.HLine)
        lay.addWidget(f1, row, 0, 1, 4)

        row += 1
        colorButton = QPushButton('color')
        lay.addWidget(colorButton, row, 0, 1, 1)
        colorButton.clicked.connect(self.colorSelect)

        self.divePlan.widgetsCtrl['model'] = controls
        lay.setAlignment(Qt.AlignTop)
        return modelCtrl

    def planTabChanged(self, i):
        self.divePlan.planMode = i
        modeString = PlanMode(i).name
        msg= QMessageBox.information(self,
                 "Dive profile plan mode change",
                 "Current Mode: {}".format(modeString))

        self.drawNewProfile()

    def colorSelect(self):
        newColor = QColorDialog.getColor()

    def PGplotChanged(self):
        global globalDivePlan
        sender = self.sender()
        newValue = sender.currentText()
        globalDivePlan.PGplot = newValue
        self.pg.update()

    def gfLowChanged(self):
        global globalDivePlan
        sender = self.sender()
        newValue = sender.value() / 100.0
        globalDivePlan.GFlow = newValue

        self.drawNewProfile()

    def gfHighChanged(self):
        global globalDivePlan
        sender = self.sender()
        newValue = sender.value() / 100.0
        globalDivePlan.GFhigh = newValue
        self.drawNewProfile()

    def tankConfigChange(self):
        # print('tankConfigChange')
        # change the object value
        sender  = self.sender() # find out which widget called this
        newValue = sender.value() # get the new value
        self.divePlan.objectOfWidget[sender](newValue) # call the assigned method to update the value
        self.drawNewProfile()

    def tankUseChange(self):
        # change the object value
        sender  = self.sender() # find out which widget called this
        newState = sender.isChecked() # get the new value
        self.divePlan.objectOfWidget[sender](newState) # call the assigned method to update the value
        self.drawNewProfile()

    def tcSliderChanged(self, tcSelected):
        self.divePlan.tcSelected = tcSelected
        self.tcBars.update()

    def getNewProfileSettings(self):
        divePlan : DivePlan = self.divePlan
        # get inputs from control widgets
        divePlan.bottomTime =   float( divePlan.widgetsCtrl['bottom']['time'].value() ) * 60.0
        divePlan.bottomDepth = float( divePlan.widgetsCtrl['bottom']['depth'].value() )
        divePlan.maxDepth = divePlan.bottomDepth
        # convert rates from m/min to m/sec float types, divide by 60.0
        # fixme: i have changed to rate defs, and these are not corrct now
        divePlan.descRate  =        float(divePlan.widgetsCtrl['descent'].value()         ) / 60.0
        divePlan.ascRateToDeco =    float(divePlan.widgetsCtrl['ascBelow50'].value()    ) / 60.0
        divePlan.ascRateAtDeco =    float(divePlan.widgetsCtrl['ascBelow6m'].value()    ) / 60.0
        divePlan.ascRateToSurface = float(divePlan.widgetsCtrl['ascToSurface'].value() ) / 60.0
        # descening time in seconds
        divePlan.descTime = divePlan.bottomDepth / divePlan.descRate

        # capture the deco stops
        divePlan.decoStopList = []
        stopNumber = 0
        for decoStop in self.divePlan.stopListUI.keys():
            stopDepth = float( divePlan.widgetsCtrl[decoStop]['depth'].value() )
            stopTime  = float( divePlan.widgetsCtrl[decoStop]['time'].value() ) * 60.0
            if stopTime > 0:
                newStop = DecoStop(depth=stopDepth, time=stopTime, number= stopNumber)
                divePlan.decoStopList.append(newStop)
                stopNumber += 1


    def drawNewProfile(self):
        divePlan = self.divePlan
        self.getNewProfileSettings()
        try:
            modelRun = calculatePlan(divePlan)
        except ValueError as error:
            errormsg = error.args[0]
            msg = QMessageBox.information(self,
                                          "calculatePlan() exception",
                                          errormsg)

        # if calc deco mode, then output the stops
        if self.divePlan.planMode == PlanMode.Calculate.value:
            outTextLines = ['runtime stop-at duration']
            for stop in self.divePlan.decoStopsCalculated:
                stopText = '{:>2.0f} min, {:>4.0f} m,  {:>3.0f} min'.format(stop.runtime/60.0, stop.depth, stop.time/60.0)
                outTextLines.append(stopText)
            outText =  '\n'.join(outTextLines)
            self.divePlan.widgetsCtrl['calcDecoLabel'].setText(outText)

        maxIDX = len(divePlan.model) -1
        self.divePlan.widgetsCtrl['tcSlider'].setMaximum( maxIDX)

        # assign the profile to plotter and update the window
        #  self.plotPlan.setPlan(divePlan)
        self.plotPlan.update()
        self.pressure.update()
        self.pg.update()
        self.heatW.update()
        self.plotBelow.update()
        # show the total time of dive profile
        totalTimeMinutes = self.divePlan.profileSampled[-1].time / 60.0
        divePlan.widgetsCtrl['totalTime'].setText('{:.0f}'.format(totalTimeMinutes))
        averageDepth = self.divePlan.profileSampled[-1].depthRunAvg
        divePlan.widgetsCtrl['avgDepth'].setText('{:.1f}'.format(averageDepth))

        # print end pressures of all tanks
        for iTank in divePlan.tankList.keys():
            divePlan.widgetsCtrl['tanks'][divePlan.tankList[iTank].name]\
            ['endbar'].setText('{:.0f}'.format(divePlan.tankList[iTank].pressure))


        # dump model data to a table, that can be seen under tab 'TABLE'
        #tableUpdate(self.tableModel, modelRun)
        #tableUpdate2(self.tableModel, modelRun)
        tableUpdate3(self.tableModel, self.divePlan.profileSampled)

##################################################################################################
# main window loop starts now
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = pydplan_main()
    app_exit_code = app.exec_()
    print('exit code {}'.format(app_exit_code))
    sys.exit(app_exit_code)
# done, end of application