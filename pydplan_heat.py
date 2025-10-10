# pydplan_heat.py
# (c) 2025 Ian Leiman, ian.leiman@gmail.com
# part of PYDPLAN, a Python Dive Planner with PyQt5 GUI
# heatmap plotting tools
""" this module provides a QWidget to plot the tissue compartment saturation heat map
    for the currently selected model point in the dive plan
    2025-10-10 fixed many qtplotting call args from float to int, py 3.14 no longer does that automatically
    """

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPainterPath, QLinearGradient, QBrush, QPalette, QPen, QColor
from PyQt5.QtWidgets import QWidget
from pydplan_buhlmann import ModelPoint
from pydplan_plot import colors
from pydplan_classes import DivePlan

class PlotHeatMapWidget(QWidget):
    """ plot the tissue compartment saturation heat map """
    def __init__(self, plan: DivePlan ):
        super().__init__()
        self.plan: DivePlan = plan
        self.initUI()

    def initUI(self):
        self.qp = QPainter()
        self.show()

    def setPlan(self, plan: DivePlan):
        self.plan: DivePlan = plan

    def paintEvent(self, e):
        self.qp.begin(self)
        self.drawSize(self.qp)
        self.drawHeatMap(self.qp)
        self.qp.end()

    def drawSize(self, qp):
        size = self.size()
        self.plot_width = size.width()
        self.plot_height = size.height()

    def drawHeatMap(self, qp, plot ='Total'):
        if not self.plan.model :
            return
        qp.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        qp.drawText(0, 10,'Heat map here')
        #xStep = self.plot_width / len(self.plan.model)
        #yStep = self.plot_height / Model.COMPS
        xStep: int = 5
        yStep: int = 10

        # iterate all compartments
        for tc in range(ModelPoint.COMPS):
            color = colors[tc]
            hColor = QColor(Qt.white)
            #color = QColor(tc*15, 15+(tc*15), 255-tc*15)
            qp.setPen(QPen(color, 1, Qt.SolidLine))
            zeroLevel = self.plot_height / 2.0

            # iterate all model points
            qp.setPen(QPen(Qt.white, 0, Qt.NoPen))
            for n, mPoint in enumerate( self.plan.model ):
                ambP = mPoint.ambient
                sTissue = mPoint.tissues[tc]
                ppN2 = sTissue.nitrogenPressure
                ppHe = sTissue.heliumPressure
                ppTot = ppN2 + ppHe

                ambTolP = sTissue.ambTolP

                if ppTot < ambP:
                    # tissue is on gassisng show blue, 100% is totally dark, less is lighter
                    delta: int = int(255 * (ambP - ppTot)/ambP)
                    hColor.setHsl(240, delta, delta)
                    brush = QBrush(hColor)
                else:
                    # tissue is supersaturated and offgassing, show green to red gradient
                    if ppTot < ambTolP:
                        # tissue is below limit, so not at red yet
                        delta = int(100 * (ambTolP - ppTot) / ppTot)
                        hColor.setHsl(120, delta, delta)
                        brush = QBrush(hColor)
                    else:
                        # exceeding limit, show red hot
                        delta = int(ppTot / ambTolP * 50 + 150)
                        hColor.setHsl(0, delta, 127)
                        brush = QBrush(hColor)
                x: int = int(n * xStep)
                y: int = int(tc* yStep)
                qp.setBrush(brush)
                qp.drawRect(x, y, xStep, yStep)

