#!/usr/bin/python
# (c) 2018 Ian Leiman, ian.leiman@gmail.com
# mod_gui_sb_sliders.py
# github project https://github.com/eianlei/trimix-fill/
#  this GUI uses function mod_calc() from tmx_calc.py
# use at your own risk, no guarantees, no liability!
#
# GUI to calculate MOD using pyqt5 and spinboxes and sliders
#  almost same UI design as mod_gui_sb.py which is done with tkinter, this is with pyqt5
#  changed control widgets to spinboxes plus added sliders

gui_version = "0.1"

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
                             QLabel, QLineEdit, QWidget, QPushButton, QSpinBox, QDoubleSpinBox,
                             QSlider)

# import modules, like PyQt5 stuff
from tmx_calc import mod_calc


# define the main window GUI objects and callbacks
class mod_gui_win(QWidget):
    def __init__(self):
        super(mod_gui_win, self).__init__()
        o2pctChanged = pyqtSignal(int)
        ## ppo2Changed = pyqtSignal(int)
        self.gasDict = {'AIR':21,'EAN32':32,'EAN50':50, 'OXYGEN':100,
                        'TMX 10/70':10,'TMX 12/65':12,'TMX 15/55':15,'TMX 18/45':18,
                        'TMX 21/35':21,'TMX 35/25':25,'TMX 30/30':30}

        # GroupBox to hold input value Spinboxes and labels for them
        modinGroup = QGroupBox("Input values for calculating MOD")
        # a ComboBOx to quicky select O2% for some commong mixes
        modinmixLabel = QLabel("Std mixes:")
        self.modinComboBox = QComboBox()
        for i in self.gasDict.keys() :
            self.modinComboBox.addItem(i)

        # callback for the value changes  mix_change()
        self.modinComboBox.activated.connect(self.mix_change)

        # input for O2%
        modin_o2pctLabel = QLabel("Oxygen %:")
        self.o2pctSpinBox = QSpinBox()
        self.o2pctSpinBox.setRange(10, 100)  # min 10%, max 100% O2
        self.o2pctSpinBox.setSingleStep(1)  # steps of 1
        self.o2pctSpinBox.setSuffix('%')  # show % suffix
        self.o2pctSpinBox.setValue(21)  # default is EAN32
        # recalculte MOD every time value changes calc_cmd()
        self.o2pctSpinBox.valueChanged.connect(self.calc_cmd)
        # add a slider too
        self.o2pctSlider = QSlider(Qt.Horizontal)
        self.o2pctSlider.setFocusPolicy(Qt.StrongFocus)
        self.o2pctSlider.setTickPosition(QSlider.TicksBothSides)
        self.o2pctSlider.setMinimum(10)
        self.o2pctSlider.setMaximum(100)
        self.o2pctSlider.setValue(21)
        self.o2pctSlider.setTickInterval(10)
        self.o2pctSlider.setSingleStep(1)
        # connect the slider to spinbox
        self.o2pctSlider.valueChanged.connect(self.o2pctSpinBox.setValue)


        # input for ppO2
        modin_ppo2Label = QLabel("ppO2 in bar/ATA:")
        self.ppo2SpinBox = QDoubleSpinBox()
        self.ppo2SpinBox.setRange(1.0, 2.0)  # min 1.0, max 2.0
        self.ppo2SpinBox.setSingleStep(0.1)  # steps of 0.1
        self.ppo2SpinBox.setValue(1.4)  # most common ppO2
        # recalculte MOD every time value changes
        self.ppo2SpinBox.valueChanged.connect(self.calc_cmd)
        # add a slider too
        self.ppo2Slider = QSlider(Qt.Horizontal)
        self.ppo2Slider.setFocusPolicy(Qt.StrongFocus)
        self.ppo2Slider.setTickPosition(QSlider.TicksBothSides)
        # slider cannot handle 1.0 to 2.0 range, we need to use 10x conversion
        self.ppo2Slider.setMinimum(10)
        self.ppo2Slider.setMaximum(20)
        self.ppo2Slider.setValue(14)
        self.ppo2Slider.setTickInterval(1)
        self.ppo2Slider.setSingleStep(1)
        # connect the slider to spinbox by using callback
        # note, slider can only have integer values, so we need conversion /10
        self.ppo2Slider.valueChanged.connect(self.ppo2SliderValueChanged)

        # EXIT button
        self.calc_btn = QPushButton('EXIT', self)
        self.calc_btn.clicked.connect(self.exit_button)

        # lay out all widgets to two grids
        # first the inputs
        modinLayout = QGridLayout()
        modinLayout.addWidget(modinmixLabel, 0, 0)
        modinLayout.addWidget(self.modinComboBox, 0, 1)
        modinLayout.addWidget(modin_o2pctLabel, 1, 0)
        modinLayout.addWidget(self.o2pctSpinBox, 1, 1)
        modinLayout.addWidget(self.o2pctSlider,2,0,1,2)
        modinLayout.addWidget(modin_ppo2Label, 3, 0)
        modinLayout.addWidget(self.ppo2SpinBox, 3, 1)
        modinLayout.addWidget(self.ppo2Slider,4,0,1,2)
        modinLayout.addWidget(self.calc_btn, 5, 0)
        modinGroup.setLayout(modinLayout)

        # output grid
        modoutGroup = QGroupBox("MOD result is")
        self.modout = QLineEdit()
        modoutLayout = QGridLayout()
        modoutLayout.addWidget(self.modout, 0, 0)
        unitLabel = QLabel("meters")
        modoutLayout.addWidget(unitLabel, 0, 1)
        modoutGroup.setLayout(modoutLayout)

        # lay out both sub grids to top level grid
        layout = QGridLayout()
        layout.addWidget(modinGroup, 0, 0)
        layout.addWidget(modoutGroup, 1, 0)
        self.setLayout(layout)

        # window title, and we are done
        self.setWindowTitle("MOD calculator pyqt5 SB, v {}".format(gui_version))

    # calculation callback, all spinboxes changing value
    def calc_cmd(self):
        '''callback for calculate button '''
        o2pct = self.o2pctSpinBox.value()
        self.o2pctSlider.setValue(o2pct)
        ppo2 = self.ppo2SpinBox.value()
        self.ppo2Slider.setValue(int(ppo2*10))
        mod_m = mod_calc(ppo2, o2pct)
        self.modout.setText("{:.1f}".format(mod_m))
        #print("calc_cmd o2pct= {} ppo2= {} => mod= {}".format(o2pct, ppo2, mod_m))
        pass

    # callback when combobox modinComboBox changes value
    def mix_change(self, index):
        #print("mix_change: {}, current text: {}".format(index,
        #                                                self.modinComboBox.currentText()))
        mixo2 = self.gasDict[self.modinComboBox.currentText()]
        self.o2pctSpinBox.setValue(mixo2)
        self.o2pctSlider.setValue(mixo2)
        pass

    # callback to make spinbox to follow slider, scale by 10
    def ppo2SliderValueChanged(self, value):
        newppo2 = value / 10
        self.ppo2SpinBox.setValue(newppo2)

    # EXIT button callback
    def exit_button(self):
        sys.exit()


# main window loop starts now
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = mod_gui_win()
    window.show()
    sys.exit(app.exec_())
# done, end of application
