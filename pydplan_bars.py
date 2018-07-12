#
# (c) 2018 Ian Leiman, ian.leiman@gmail.com
# pydplan_plot
# part of PYDPLAN, a Python Dive Planner with PyQt5 GUI
# bar plotting tools

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPainterPath, QLinearGradient, QBrush, QPalette, QPen, QColor
from PyQt5.QtWidgets import *
from pydplan.pydplan_buhlmann import *
from pydplan.pydplan_plot import colors

class TCbarsController(QWidget):
    def __init__(self, plan=None):
        super().__init__()
        self.plan = plan

        mainW = QWidget()
        layout = QVBoxLayout()
        slider = QSlider(Qt.Horizontal)
        barW = PlotTCbarsWidget(self.plan)
        layout.addWidget(slider)
        layout.addWidget(barW)
        mainW.setLayout(layout)
        self.show()

    def setPlan(self, plan):
        self.plan = plan


class PlotTCbarsWidget(QWidget):
    def __init__(self, plan=None):
        super().__init__()
        self.plan = plan
        self.initUI()

    def initUI(self):
        self.qp = QPainter()
        self.show()

    def setPlan(self, plan):
        self.plan = plan

    def paintEvent(self, e):
        self.qp.begin(self)
        self.drawSize(self.qp)
        self.drawBars(self.qp)
        self.qp.end()

    def drawSize(self, qp):
        size = self.size()
        self.plot_width = size.width()
        self.plot_height = size.height()

    def drawBars(self, qp, plot ='Total'):
        if not self.plan.model :
            return
        maxnum = len(self.plan.model) -1
        selected = self.plan.tcSelected
        if selected > maxnum:
            selected = maxnum
        sTissues = self.plan.model[selected].tissues
        ambP = self.plan.model[selected].ambient
        depth = pressure2depth(ambP - Constants.surfacePressure)
        profile = self.plan.profileSampled
        gfNow = profile[selected].gfNow

        qp.drawText(0 , 9, '{}/{} Pamb={:.1f} depth= {:.1f} m time= {:.0f} s GF={:.0f}%'.format(
            selected, maxnum, ambP, depth, profile[selected].time, gfNow*100 ))


        # plot bars for all tissues
        for tc in range(ModelPoint.COMPS):

            sTissue = sTissues[tc]
            ppN2 = sTissue.nitrogenPressure
            ppHe = sTissue.heliumPressure

            ambTolP = sTissue.ambTolP

            ambTolDepth = pressure2depth(ambTolP - Constants.surfacePressure)
            deltaP = ambTolP - ambP
            gfHighP = self.plan.GFhigh * deltaP + ambP
            gfLowP = self.plan.GFlow * deltaP + ambP
            gfNowP = gfNow * deltaP + ambP

            ppTot = ppN2 + ppHe
            barN2 = ppN2 * 50
            barHe = ppHe * 50
            saturation = ppTot / ambP
            satPct = saturation * 100.0

            color = colors[tc]
            qp.setPen(QPen(color, 1, Qt.SolidLine))
            x1 = 20+tc*30
            qp.drawText(x1, 20, '{}'.format(tc))
            if gfNowP >= ppTot:
                brushN2 = QBrush(QColor(0,255, 0, 127))
                brushHe = QBrush(QColor(0, 0, 255, 127))
            else:
                brushN2 = QBrush(QColor(0,255, 255, 127))
                brushHe = QBrush(QColor(255, 0, 255, 127))

            qp.setBrush(brushN2)
            qp.drawRect(x1, 20, 19, barN2)
            qp.setBrush(brushHe)
            qp.drawRect(x1, 20+barN2, 19, barHe)

            # draw the Buhlmann tolerated ambient pressure (GF=100)
            if ambTolP >= ppTot:
                qp.setPen(QPen(Qt.darkRed, 2, Qt.SolidLine))
            else:
                qp.setPen(QPen(Qt.red, 5, Qt.SolidLine))
            y = ambTolP * 50.0 + 20.0
            qp.drawLine(x1, y, x1+20, y)
            #qp.drawText(x1, y+10, '{:.1f} m'.format(ambTolDepth))
            qp.drawText(x1, y + 10, '{:.0f}%'.format(satPct))

            # draw gradient factor limits, low and high lines
            yLow  = gfLowP * 50.0 +20.0
            yHigh = gfHighP * 50.0 +20.0
            qp.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine))
            qp.drawLine(x1, yLow, x1 + 10, yLow)
            qp.setPen(QPen(Qt.darkGreen, 1, Qt.SolidLine))
            qp.drawLine(x1, yHigh, x1 + 10, yHigh)
            # draw actually used GF, green if OK, red if violating it
            yGF = gfNowP * 50.0 +20.0
            if gfNowP >=  ppTot:
                # safe situation
                qp.setPen(QPen(Qt.green, 3, Qt.SolidLine))
            else :
                qp.setPen(QPen(Qt.red, 5, Qt.SolidLine))
            qp.drawLine(x1+10, yGF, x1 + 20, yGF)

        # draw the current depth = ambient pressure line
        y = ambP * 50.0 + 20.0
        qp.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        qp.drawLine(0, y, self.plot_width, y)
        qp.drawText(500, y-3, '{:.1f} bar {:.1f} m'.format(ambP, depth))