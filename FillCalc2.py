#!/usr/bin/python
# (c) 2018 Ian Leiman, ian.leiman@gmail.com
# tmx_gui_pyqt5.py
# github project https://github.com/eianlei/trimix-fill/
# Python-3 GUI using trimix blending calculator
#  uses PyQt5 framework
#  this GUI uses function tmx_calc
# use at your own risk, no guarantees, no liability!
#
# TODO add the ppo2 input SB
# TODO print also the date/time + cost + MOD
# TODO add HELP, EXIT
# TODO add error popup dialog
# TODO add a combobox for standard mixes
# TODO fix the 300 bar bug
# TODO change the start_pressSB max according to tankEndPressComboBox
from PyQt5.QtGui import QPalette

tmx_gui_version = "2.0"

# import modules, like PyQt5 stuff
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
                             QLabel, QWidget, QSpinBox, QDoubleSpinBox,
                             QMainWindow, QFrame, QVBoxLayout, QTabWidget, QMenu,
                             QAction)

# import calculation modules
from tmx_calc import *


# define the main window GUI objects and callbacks
class fill_calc_main(QMainWindow):
    '''GUI for calculating trimix fills using PyQt5'''
    def __init__(self):
        super().__init__()

        self.central = QWidget()
        self.controlW = QWidget()
        self.outputW = QFrame()
        self.lay_main = QVBoxLayout()
        self.menuMain = self.menuBar()

        # menu items
        self.menuFile = self.menuMain.addMenu('&File')
        self.menuEdit = self.menuMain.addMenu('&Edit')
        self.menuHelp = self.menuMain.addMenu('&Help')
        self.menuFileOpen = QMenu('&Open')
        self.menuFile.addMenu(self.menuFileOpen)
        self.menuFileSave = QMenu('&Save')
        self.menuFile.addMenu(self.menuFileSave)

        # define one exit action
        exitAct = QAction('exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)
        self.menuFile.addAction(exitAct)

        # GroupBox to hold starting tank mix spinboxes and labels for them
        startGroup = QGroupBox("Current tank mix")
        # define SpinBoxes to input data
        # input for current/starting pressure
        start_pressLabel = QLabel("Current tank pressure (bar):")
        self.start_pressSB = QSpinBox()
        self.start_pressSB.setRange(0, 300)  # min 0, max 300 bar
        self.start_pressSB.setSingleStep(1)  # steps of 1
        self.start_pressSB.setSuffix(' bar')  # show bar suffix
        self.start_pressSB.setValue(100)  # default is 100 bar
        self.start_pressSB.setToolTip("the starting pressure of the tank to be filled")

        # input for current/starting O2%
        start_O2pctLabel = QLabel("Current Oxygen %:")
        self.start_O2pctSB = QSpinBox()
        self.start_O2pctSB.setRange(10, 100)  # min 10%, max 100% O2
        self.start_O2pctSB.setSingleStep(1)  # steps of 1
        self.start_O2pctSB.setSuffix('%')  # show % suffix
        self.start_O2pctSB.setValue(21)  # default is air

        # input for current He%
        start_HEpctLabel = QLabel("Current Helium %:")
        self.start_HEpctSB = QSpinBox()
        self.start_HEpctSB.setRange(0, 100)  # min 0%, max 100% He
        self.start_HEpctSB.setSingleStep(1)  # steps of 1
        self.start_HEpctSB.setSuffix('%')  # show % suffix
        self.start_HEpctSB.setValue(35)  # default is 35 for tmx21/35

        # layout the group into grid
        startLayout = QGridLayout()
        startLayout.addWidget(start_pressLabel, 0, 0)
        startLayout.addWidget(self.start_pressSB, 0, 1)
        startLayout.addWidget(start_O2pctLabel, 1, 0)
        startLayout.addWidget(self.start_O2pctSB, 1, 1)
        startLayout.addWidget(start_HEpctLabel, 2, 0)
        startLayout.addWidget(self.start_HEpctSB, 2, 1)
        startGroup.setLayout(startLayout)

        # GroupBox to hold WANTED tank mix spinboxes and labels for them
        wantGroup = QGroupBox("Wanted tank mix")
        # define SpinBoxes to input data
        # input for wanted pressure, a combobox
        want_pressLabel = QLabel("Wanted tank pressure (bar):")
        self.want_pressSB = QSpinBox()
        self.tankEndPressComboBox = QComboBox()
        self.tankTypeList = ['200', '232', '300']
        for i in range(len(self.tankTypeList)) :
            self.tankEndPressComboBox.addItem(self.tankTypeList[i])

        self.gasDict = {'AIR': (21,0),'EAN32': (32,0),'EAN50': (50,0), 'OXYGEN':(100,0),
                        'TMX 10/70':(10,70),'TMX 12/65':(12,65),'TMX 15/55':(15,55),'TMX 18/45':(18,45),
                        'TMX 21/35':(21,35),'TMX 35/25':(35,25),'TMX 30/30':(30,30)}
        modinmixLabel = QLabel("Std mixes:")
        self.modinComboBox = QComboBox()
        for i in self.gasDict.keys() :
            self.modinComboBox.addItem(i)

        # callback for the value changes  mix_change()
        self.modinComboBox.activated.connect(self.mix_change)

        # input for wanted O2%
        want_O2pctLabel = QLabel("Wanted Oxygen %:")
        self.want_O2pctSB = QSpinBox()
        self.want_O2pctSB.setRange(10, 100)  # min 10%, max 100% O2
        self.want_O2pctSB.setSingleStep(1)  # steps of 1
        self.want_O2pctSB.setSuffix('%')  # show % suffix
        self.want_O2pctSB.setValue(21)  # default is air

        # input for wanted He%
        want_HEpctLabel = QLabel("Wanted Helium %:")
        self.want_HEpctSB = QSpinBox()
        self.want_HEpctSB.setRange(0, 100)  # min 0%, max 100% He
        self.want_HEpctSB.setSingleStep(1)  # steps of 1
        self.want_HEpctSB.setSuffix('%')  # show % suffix
        self.want_HEpctSB.setValue(35)  # default is 35 for tmx21/35

        # layout the group into grid
        wantLayout = QGridLayout()
        wantLayout.addWidget(want_pressLabel, 0, 0)
        wantLayout.addWidget(self.tankEndPressComboBox, 0, 1)
        wantLayout.addWidget(modinmixLabel,1,0)
        wantLayout.addWidget(self.modinComboBox, 1, 1)
        wantLayout.addWidget(want_O2pctLabel, 2, 0)
        wantLayout.addWidget(self.want_O2pctSB, 2, 1)
        wantLayout.addWidget(want_HEpctLabel, 3, 0)
        wantLayout.addWidget(self.want_HEpctSB, 3, 1)
        wantGroup.setLayout(wantLayout)

        # connect all widgets to calculateGas
        self.start_pressSB.valueChanged.connect(self.calculateGas)
        self.start_O2pctSB.valueChanged.connect(self.calculateGas)
        self.start_HEpctSB.valueChanged.connect(self.calculateGas)
        self.want_pressSB.valueChanged.connect(self.calculateGas)
        self.want_O2pctSB.valueChanged.connect(self.calculateGas)
        self.want_HEpctSB.valueChanged.connect(self.calculateGas)

        self.tankEndPressComboBox.currentIndexChanged.connect(self.calculateGas)

        # GroupBox to hold fill cost calculation spinboxes and labels for them
        costGroup = QGroupBox("Fill cost calculation")
        # define SpinBoxes to input data
        # input for tank size
        tankSizeLabel = QLabel("Tank size (liters):")
        self.tankSizeSB = QSpinBox()
        self.tankSizeSB.setRange(1, 50)  # min 1, max 50 liters
        self.tankSizeSB.setSingleStep(1)  # steps of 1
        self.tankSizeSB.setSuffix(' L')  # show L suffix
        self.tankSizeSB.setValue(24)  # default is 24 liters
        # input Oxygen cost
        o2costLabel = QLabel("Oxygen cost (€/m^3):")
        self.o2costSB = QDoubleSpinBox()
        self.o2costSB.setRange(1.0, 50.0)  # min - max
        self.o2costSB.setSingleStep(0.1)  # steps of 0.1
        self.o2costSB.setSuffix(' €/m^3')  # show suffix
        self.o2costSB.setValue(4.14)  # default
        # input Helium cost
        HEcostLabel = QLabel("Helium cost (€/m^3):")
        self.HEcostSB = QDoubleSpinBox()
        self.HEcostSB.setRange(1.0, 500.0)  # min - max
        self.HEcostSB.setSingleStep(0.1)  # steps of 0.1
        self.HEcostSB.setSuffix(' €/m^3')  # show suffix
        self.HEcostSB.setValue(25.0)  # default
        # input compress fill cost
        compCostLabel = QLabel("compressor run cost (€):")
        self.compCostSB = QDoubleSpinBox()
        self.compCostSB.setRange(1.0, 50.0)  # min - max
        self.compCostSB.setSingleStep(0.01)  # steps of 0.1
        self.compCostSB.setSuffix(' €')  # show suffix
        self.compCostSB.setValue(5.00)  # default

        costLayout = QGridLayout()
        costLayout.addWidget(tankSizeLabel, 0, 0)
        costLayout.addWidget(self.tankSizeSB, 0, 1)
        costLayout.addWidget(o2costLabel, 1, 0)
        costLayout.addWidget(self.o2costSB, 1, 1)
        costLayout.addWidget(HEcostLabel, 2, 0)
        costLayout.addWidget(self.HEcostSB, 2, 1)
        costLayout.addWidget(compCostLabel, 3, 0)
        costLayout.addWidget(self.compCostSB, 3, 1)

        self.costOutput = QLabel('total cost of fill')
        palette1 = QPalette()
        palette1.setColor(QPalette.Background, Qt.white)
        self.costOutput.setAutoFillBackground(True)
        self.costOutput.setPalette(palette1)
        self.costOutput.setFrameStyle(QFrame.Box | QFrame.Raised)
        costLayout.addWidget(self.costOutput, 4, 0, 4, 2)
        costGroup.setLayout(costLayout)

        self.tankSizeSB.valueChanged.connect(self.calculateGas)
        self.o2costSB.valueChanged.connect(self.calculateGas)
        self.HEcostSB.valueChanged.connect(self.calculateGas)
        self.compCostSB.valueChanged.connect(self.calculateGas)

        ################################################
        # lay out all sub grids to top level grid
        layCtrl = QGridLayout()
        layCtrl.addWidget(startGroup, 0, 0)
        layCtrl.addWidget(wantGroup, 1, 0)
        layCtrl.addWidget(costGroup, 0, 1, 2, 1)

        self.controlW.setLayout(layCtrl)
        self.lay_main.addWidget(self.controlW)
        self.createTabOut()
        self.tabOut.currentChanged.connect(self.calculateGas)

        self.central.setLayout(self.lay_main)
        self.setCentralWidget(self.central)

        # window title, and we are done
        self.setWindowTitle("Trimix blending calculator PyQt5 v {}".format(tmx_gui_version))
        self.show()

        self.calculateGas()


    # callback when combobox modinComboBox changes value
    def mix_change(self, index):
        mixo2, mixHe = self.gasDict[self.modinComboBox.currentText()]
        self.want_O2pctSB.setValue(mixo2)
        self.want_HEpctSB.setValue(mixHe)

    def createTabOut(self):
        self.tabOut = QTabWidget()

        # TODO: convert this into a loop
        # tabList = {'Air' : self.createAirFill(), }
        # for tab in tabList :

        # tab for air fill
        self.tabAir = QWidget()
        self.lay_tabAir = QGridLayout()
        self.createAirFill()
        self.tabAir.setLayout(self.lay_tabAir)
        self.tabOut.addTab(self.tabAir, 'Air')

        # tab for Nitrox fill
        self.tabNitrox = QWidget()
        self.lay_tabNitrox = QGridLayout()
        self.createNitroxFill()
        self.tabNitrox.setLayout(self.lay_tabNitrox)
        self.tabOut.addTab(self.tabNitrox, 'Nitrox')

        # tab for Trimix fill
        self.tabTrimix = QWidget()
        self.lay_tabTrimix = QGridLayout()
        self.createTrimixFill()
        self.tabTrimix.setLayout(self.lay_tabTrimix)
        self.tabOut.addTab(self.tabTrimix, 'Trimix')

        # tab for Partial Pressure fill
        self.tabPP = QWidget()
        self.lay_tabPP = QGridLayout()
        self.createPPfill()
        self.tabPP.setLayout(self.lay_tabPP)
        self.tabOut.addTab(self.tabPP, 'Partial Pressure')

        # tab for Helium + Nitrox fill
        self.tabHeNx = QWidget()
        self.lay_tabHeNx = QGridLayout()
        self.createHeNxFill()
        self.tabHeNx.setLayout(self.lay_tabHeNx)
        self.tabOut.addTab(self.tabHeNx, 'He + Nitrox')

        self.lay_main.addWidget(self.tabOut)

    def createAirFill(self):
        self.t0 = QLabel('<b>Calculation for air fill</b>')
        self.t0r2 = QLabel('-')
        self.lay_tabAir.addWidget(self.t0, 0, 0, 1, 5)
        self.lay_tabAir.addWidget(self.t0r2, 1, 0, 4, 5)

    def createNitroxFill(self):
        self.t1 = QLabel('<b>Calculation for Nitrox CFM (Continuous Flow Mixing) fill</b>')
        self.t1r2 = QLabel('-')
        self.lay_tabNitrox.addWidget(self.t1, 0, 0, 1, 5)
        self.lay_tabNitrox.addWidget(self.t1r2, 1, 0, 4, 5)

    def createTrimixFill(self):
        self.t2 = QLabel('<b>Calculation for TRIMIX CFM (Continuous Flow Mixing) fill</b>')
        self.t2r2 = QLabel('-')
        self.lay_tabTrimix.addWidget(self.t2, 0, 0, 1, 5)
        self.lay_tabTrimix.addWidget(self.t2r2, 1, 0, 4, 5)

    def createPPfill(self):
        self.t3 = QLabel('<b>Calculation for Partial Pressure He+O2+Air fill</b>')
        self.t3r2 = QLabel('-')
        self.lay_tabPP.addWidget(self.t3, 0, 0, 1, 5)
        self.lay_tabPP.addWidget(self.t3r2, 1, 0, 4, 5)

    def createHeNxFill(self):
        self.t4 = QLabel('<b>Calculation for Helium decant + Nitrox CFM fill</b>')
        self.t4r2 = QLabel('-')
        self.lay_tabHeNx.addWidget(self.t4, 0, 0, 1, 5)
        self.lay_tabHeNx.addWidget(self.t4r2, 1, 0, 4, 5)


    def calculateGas(self):
        startbar = self.start_pressSB.value()
        endbar = float(self.tankEndPressComboBox.currentText())
        start_o2 =  self.start_O2pctSB.value()
        start_he =  self.start_HEpctSB.value()
        end_o2 =  self.want_O2pctSB.value()
        end_he =  self.want_HEpctSB.value()
        he_ig = False
        o2_ig = False
        # cost calculation input
        liters =  self.tankSizeSB.value()
        o2_cost_eur =  self.o2costSB.value()
        he_cost_eur =  self.HEcostSB.value()
        fill_cost_eur =  self.compCostSB.value()

        currentTab = self.tabOut.currentIndex()
        cm = ['air', 'nx', 'tmx','pp','cfm']
        calc_method = cm[currentTab]
        result = tmx_calc(calc_method, startbar, endbar, start_o2, start_he,
                          end_o2, end_he, he_ig, o2_ig)

        add_o2 = result['add_o2']
        add_he = result['add_he']
        cost_result = tmx_cost_calc(liters, endbar, add_o2, add_he, o2_cost_eur,
                                    he_cost_eur, fill_cost_eur)
        self.costOutput.setText (cost_result['result_txt'])

        if currentTab == 0:
            self.t0r2.setText(result['status_text'])
        elif currentTab == 1:
            self.t1r2.setText(result['status_text'])
        elif currentTab == 2:
            self.t2r2.setText(result['status_text'])
        elif currentTab == 3:
            self.t3r2.setText(result['status_text'])
            # self.r3heFrom.setText("{:.1f}".format(startbar))
            # self.r3heAdd.setText("{:.1f}".format(result['add_he']))
            # self.r3O2From.setText("{:.1f}".format( startbar + result['add_he'] ))
            # self.r3O2Add.setText("{:.1f}".format(result['add_o2']))
            # self.r3airFrom.setText("{:.1f}".format( startbar + result['add_he'] + result['add_o2']))
            # self.r3airAdd.setText("{:.1f}".format(endbar - result['add_o2'] - result['add_he'] -startbar))
        elif currentTab == 4:
            self.t4r2.setText(result['status_text'])

        pass


# main window loop starts now
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = fill_calc_main()
    window.show()
    sys.exit(app.exec_())
# done, end of application
