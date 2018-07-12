#
# (c) 2018 Ian Leiman, ian.leiman@gmail.com
# pydplan_plot
# part of PYDPLAN, a Python Dive Planner with PyQt5 GUI
# plotting tools

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPainterPath, QLinearGradient, QBrush, QPen, QColor
from PyQt5.QtWidgets import QWidget

from pydplan.pydplan_buhlmann import ModelPoint
#from pydplan.pydplan_classes import DivePlan
#from pydplan.pydplan_profiletools import DiveProfilePoint

colors = [Qt.black, Qt.gray, Qt.lightGray, Qt.darkGray,
          Qt.red, Qt.darkYellow, Qt.green, Qt.darkGreen,
          Qt.blue, Qt.darkBlue, Qt.cyan, Qt.darkCyan,
          Qt.darkMagenta, Qt.magenta, Qt.yellow, Qt.darkRed]

class PlotBelowWidget(QWidget):
    def __init__(self, plan=None):
        super().__init__()
        self.plan  = plan
        self.maxPressure = 3.0
        self.initUI()

    def initUI(self):
        self.qp = QPainter()
        self.show()

    def paintEvent(self, e):
        size = self.size()
        self.plot_width = size.width() -50
        self.plot_height = size.height() -5

        self.qp.begin(self)
        self.drawPP(self.qp)
        self.drawPressureGrid(self.qp)

        self.qp.end()

    def drawPP(self,qp):
        qp.drawText(5, self.plot_height+5 , 'PARTIAL PRESSURES O2, He, N2')
        if not self.plan.profileSampled :
            return
        profile = self.plan.profileSampled
        self.totalTime = self.plan.profileSampled[-1].time
        self.maxPressure = self.plan.maxPPanyGas

        # draw the ppo2
        x1, y1 = (0, self.plot_height )
        qp.setPen(QPen(Qt.darkGreen, 2, Qt.SolidLine))
        for point in  profile:
            x = (point.time / self.totalTime) * self.plot_width
            y = (1 - point.ppOxygen / self.maxPressure) * self.plot_height
            qp.drawLine(x1, y1, x, y)
            x1, y1 = x, y
        qp.drawText(x - 20, y, 'ppO2')
        # draw the ppHe
        x1, y1 = (0, self.plot_height )
        qp.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
        for point in  profile:
            x = (point.time / self.totalTime) * self.plot_width
            y = (1 - point.ppHelium / self.maxPressure) * self.plot_height
            qp.drawLine(x1, y1, x, y)
            x1, y1 = x, y
        qp.drawText(x - 20, y, 'ppHe')
        # draw the ppN2
        x1, y1 = (0, self.plot_height )
        qp.setPen(QPen(Qt.darkYellow, 1, Qt.SolidLine))
        for point in  profile:
            x = (point.time / self.totalTime) * self.plot_width
            y = (1 - point.ppNitrogen / self.maxPressure) * self.plot_height
            qp.drawLine(x1, y1, x, y)
            x1, y1 = x, y
        qp.drawText(x - 20, y-10, 'ppN2')

        # draw ppo2=1.6 limit (common deco gas limit, bottom gas limit usually 1.4
        y = (1.0 - 1.60 / self.maxPressure) * self.plot_height
        qp.setPen(QPen(Qt.darkGreen, 1, Qt.DashLine))
        qp.drawLine(0, y, self.plot_width, y)
        qp.drawText(self.plot_width/2, y + 10, 'ppO2=1.6 limit')

        # draw ppN2 = 3.16, END=30m, the GUE limit, note DAN limit is 3.95
        y = (1.0 - 3.16 / self.maxPressure) * self.plot_height
        qp.setPen(QPen(Qt.darkYellow, 1, Qt.DashLine))
        qp.drawLine(0, y, self.plot_width, y)
        qp.drawText(self.plot_width/2, y + 10, 'ppN2=3.16 limit (END=30m)')

    def drawPressureGrid(self, qp):
        qp.setPen(QPen(Qt.gray, 1, Qt.DotLine))
        # pressure lines at maxPressure/6 bar intervals
        for gline in range(7) :
            y = (1 - (gline/6.0 )) * self.plot_height
            qp.drawLine(0, y, self.plot_width, y)
            ltext = '{:.1f} bar'.format(gline * self.maxPressure/6.0)
            qp.drawText(self.plot_width + 5, y + 10, ltext)
        # ticks at 1 meter intervals
        #for dd in range(0, int(self.depthMax), 1):
        #    y = int((dd / self.depthMax) * self.plot_height)
         #   qp.drawLine(self.plot_width - 5, y, self.plot_width + 4, y)

##################################################################################
class PlotPlanWidget(QWidget):
    def __init__(self, plan=None):
        super().__init__()
        self.plan = plan
        self.profileSampled = None
        self.TC = None
        self.maxTC = None
        self.initUI()
        self.ceilingPlotX = []
        self.ceilingPlotY = [[]]
    # initialize the window
    def initUI(self):
        self.qp = QPainter()
        self.show()

    # set the vectorised format of profile
    def setPlan(self, plan):
        self.plan = plan

    # when any event occurs, like resize, we also redraw the plot
    def paintEvent(self, e):
        #qp = QPainter()
        self.qp.begin(self)
        self.drawSize(self.qp)
        self.drawDepth(self.qp)
        self.drawDepthGrid(self.qp)
        self.drawTimeGrid(self.qp)
        self.drawCeilings(self.qp)
        self.drawCeilingMargin(self.qp)
        self.drawTanks(self.qp)
        self.drawTankPressure(self.qp)
        #self.drawTC(self.qp)
        self.qp.end()

    # redraw the depth profile plot

    def drawSize(self, qp):
        size = self.size()
        self.plot_width = size.width() -50
        self.plot_height = size.height() -20

    def drawDepth(self, qp):

        # Fill plot bg area
        bgPath = QPainterPath()
        bgPath.moveTo(self.plot_width, self.plot_height)
        bgPath.lineTo(0.0, self.plot_height)
        bgPath.lineTo(0.0, 0.0)
        bgPath.lineTo(self.plot_width, 0.0)
        bgPath.closeSubpath()
        gradient = QLinearGradient(0, 0, 0, 100)
        gradient.setColorAt(0.0, Qt.white)
        gradient.setColorAt(1.0, Qt.white)
        qp.setBrush(QBrush(gradient))
        qp.drawPath(bgPath)
        qp.drawText(50, 50, 'placeholder for the profile plot widget')

        if not self.plan.profileSampled :
            return

        self.totalTime = self.plan.profileSampled[-1].time
        self.depthMax = self.plan.maxDepth

        # now we plot the DEPTH profile
        depthPath = QPainterPath()
        depthPath.moveTo(0.0, 0.0)
        #point: DiveProfilePoint
        for n, point in enumerate( self.plan.profileSampled):
            x = (point.time / self.totalTime ) * self.plot_width
            y = (point.depth  / self.depthMax) * self.plot_height
            depthPath.lineTo(x, y)

        depthPath.lineTo(self.plot_width, 0.0)
        depthPath.lineTo(0.0, 0.0)
        depthPath.closeSubpath()
        gradient = QLinearGradient(0, 0, 0, 100)
        gradient.setColorAt(0.0, Qt.cyan)
        gradient.setColorAt(1.0, Qt.blue)
        qp.setBrush(QBrush(gradient))
        qp.drawPath(depthPath)

    # redraw the ceiling depths
    def drawCeilings(self, qp):

        if not self.plan.profileSampled :
            return
        profileSampled = self.plan.profileSampled
        self.ceilingPlotX = [0 for y in range(len(profileSampled)) ]
        self.ceilingPlotY = [[0 for x in range(len(profileSampled))] for y in range(ModelPoint.COMPS)]

        # draw the point.ceiling_use_3m line in green
        x1, y1 = (0, 0)
        pen = QPen(Qt.green, 2, Qt.SolidLine)
        qp.setPen(pen)
        for n, point in enumerate(profileSampled):
            x = (point.time / self.totalTime) * self.plot_width
            self.ceilingPlotX[n] = x
            y = point.modelpoint.leadCeilingStop / self.depthMax * self.plot_height
            qp.drawLine(x1, y1, x, y)
            x1, y1 = x, y
            #at the same go we compute the ceiling plots (x,y) for individual tissue compartments
            for tc in range(ModelPoint.COMPS):
                if not point.modelpoint.ceilings:
                    yCeiling = 0.0
                elif point.modelpoint.ceilings[tc] > 0.0:
                    yCeiling = (point.modelpoint.ceilings[tc] / self.depthMax) * self.plot_height
                else:
                    yCeiling = 0.0
                self.ceilingPlotY[tc][n] = yCeiling

        # draw the running average depth
        x1, y1 = (0, 0)
        qp.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
        for point in  profileSampled:
            x = (point.time / self.totalTime) * self.plot_width
            y = point.depthRunAvg / self.depthMax * self.plot_height
            qp.drawLine(x1, y1, x, y)
            x1, y1 = x, y
        qp.drawText(x + 10, y, 'AVG')

        # now draw the tissue compartment ceilings one by one
        for tc in range(ModelPoint.COMPS):
            color = QColor(tc*15, 255-(tc*15), tc*15)
            pen = QPen(color, 1, Qt.SolidLine)
            qp.setPen(pen)
            x1, y1 = (0, 0)
            for n in range(len(self.ceilingPlotX)):
                x = self.ceilingPlotX[n]
                y = self.ceilingPlotY[tc][n]
                qp.drawLine(x1, y1, x, y)
                x1 = x
                y1 = y

    # redraw the ceiling margin
    def drawCeilingMargin(self, qp):

        if not self.plan.profileSampled :
            return
        profileSampled = self.plan.profileSampled
        x1, y1 = (0, 0)
        x2 = 0
        mError = False
        status = 'ok'
        zeroLevel = self.plot_height * 0.75
        for point in  profileSampled:
            margin = point.depth - point.ceiling_now
            if margin < 0:
                qp.setPen(QPen(Qt.red,2, Qt.SolidLine))
                mError = True
                status = 'ERROR!'
            else:
                qp.setPen(QPen(Qt.darkGreen, 1, Qt.SolidLine))
            x = (point.time / self.totalTime) * self.plot_width
            y = zeroLevel - (margin / self.depthMax * self.plot_height * 0.5)

            if point.time >= self.plan.ascentBegins:
                qp.drawLine(x1, y1, x, y)
            else:
                x2 = x
            x1, y1 = x, y
        qp.setPen(QPen(Qt.black, 1, Qt.DashLine))
        qp.drawLine(x2, zeroLevel, self.plot_width, zeroLevel)
        if mError:
            qp.setPen(QPen(Qt.red, 1, Qt.DashLine))
        qp.drawText(x2+20, zeroLevel-1, 'ceiling margin {}'.format(status))

    # redraw the TC curves plot
    def drawTC(self, qp):

        if not self.TC :
            return

        size = self.size()
        plot_width = size.width() -50
        plot_height = size.height() -20
        samples = len(self.TC[0])
        maxPressure = max(self.maxTC) # biggest value we will plot
        step = plot_width / samples


        for tc in range(len(self.TC)):
            color = QColor(255-(tc*15), tc*15, tc*15)
            pen = QPen(color, 1, Qt.SolidLine)
            qp.setPen(pen)
            x1, y1 = (0, 0)
            for index in range(samples):
                x = index * step
                y = (self.TC[tc][index] / maxPressure) * plot_height
                qp.drawLine(x1, y1, x, y)
                x1 = x
                y1 = y

    def drawDepthGrid(self, qp):
        qp.setPen(Qt.darkRed)
        # depth lines at 5 meter intervals
        for dd in range(0, int(self.depthMax), 5):
            y = int((dd / self.depthMax) * self.plot_height)
            qp.drawLine(0, y, self.plot_width, y)
            ltext = '{:d} m'.format(dd)
            qp.drawText(self.plot_width + 5, y + 5, ltext)
        # ticks at 1 meter intervals
        for dd in range(0, int(self.depthMax), 1):
            y = int((dd / self.depthMax) * self.plot_height)
            qp.drawLine(self.plot_width - 5, y, self.plot_width + 4, y)

    def drawTimeGrid(self, qp):
        # time lines at 5 minute intervals
        qp.setPen(Qt.darkGreen)
        for tt in range(0, int(self.totalTime), 5 * 60):
            x = int((tt / self.totalTime) * self.plot_width)
            qp.drawLine(x, 0, x, self.plot_height)
            ltext = '{:d}'.format(tt // 60)
            qp.drawText(x, self.plot_height + 10, ltext)
        # time ticks at 1 minute intervals
        qp.setPen(Qt.darkGreen)
        for tt in range(0, int(self.totalTime), 60):
            x = int((tt / self.totalTime) * self.plot_width)
            qp.drawLine(x, self.plot_height - 5, x, self.plot_height + 5)

        pass

    def drawTanks(self, qp):

        for tankKey in self.plan.tankList.keys():
            qp.setPen(Qt.black)
            tank = self.plan.tankList[tankKey]
            if tank.use == False:
                continue
            x1 = tank.useFromTime / self.totalTime *self.plot_width
            x2 = tank.useUntilTime / self.totalTime *self.plot_width
            yTxt = tank.changeDepth / self.depthMax * self.plot_height
            bgPath = QPainterPath()
            bgPath.moveTo(x1, self.plot_height+10)
            bgPath.lineTo(x1, self.plot_height+20)
            bgPath.lineTo(x2, self.plot_height+20)
            bgPath.lineTo(x2, self.plot_height+10)
            bgPath.closeSubpath()
            gradient = QLinearGradient(0, 0, 0, 100)
            gradient.setColorAt(0.0, tank.color)
            gradient.setColorAt(1.0, tank.color)
            qp.setBrush(QBrush(gradient))
            qp.drawPath(bgPath)
            text = '{} ({}/{})'.format(tank.name, tank.o2, tank.he)
            text2 = '{:.0f} m {:.0f} min'.format(tank.changeDepth, tank.useFromTime/60.0)
            qp.drawText(x1+3, self.plot_height+20, text)
            qp.drawText(x1+3, yTxt + 10, text)
            qp.drawText(x1+3, yTxt + 20, text2)

            qp.setPen(QPen(Qt.black, 1, Qt.DotLine))
            if x1 != 0 :
                qp.drawLine(x1, self.plot_height, x1, yTxt)
                qp.drawLine(x1, yTxt, self.plot_width, yTxt)

    def drawTankPressure(self, qp):

        # draw the tank pressure
        previousTank = None
        lastPressure = None
        x1 = 0
        y1 = (1.0 - self.plan.profileSampled[0].currentTankPressure / 300.0) * self.plot_height

        for point in  self.plan.profileSampled:
            thisTank = point.tank
            x = (point.time / self.totalTime) * self.plot_width
            y = (1.0 - point.currentTankPressure / 300.0) * self.plot_height
            if thisTank != previousTank:
                if lastPressure :
                    qp.drawText(x -5,y1, '{:.0f}'.format(lastPressure))
                qp.setPen(QPen(thisTank.color, 2, Qt.SolidLine))
                qp.drawText(x + 2, y, '{:.0f}'.format(point.currentTankPressure))
                y1 = y

            qp.drawLine(x1, y1, x, y)
            x1, y1 = x, y
            previousTank = thisTank
            lastPressure = point.currentTankPressure
        qp.drawText(x + 10, y, '{:.0f}'.format(lastPressure))

##############################################################################################
class PlotTissuesWidget(QWidget):
    def __init__(self, plan=None):
        super().__init__()
        self.plan = plan
        self.initUI()

    # initialize the window
    def initUI(self):
        self.qp = QPainter()
        self.show()

    def setPlan(self, plan):
        self.plan = plan

    # when any event occurs, like resize, we also redraw the plot
    def paintEvent(self, e):
        self.qp.begin(self)
        self.drawSize(self.qp)
        self.drawDepthGrey(self.qp)
        self.drawTC(self.qp)
        self.qp.end()

    def drawSize(self, qp):
        size = self.size()
        self.plot_width = size.width() -50
        self.plot_height = size.height() -20

    def drawTC(self, qp):
        if not self.plan.model :
            return

        # now draw the tissue compartment pressures one by one for N2
        maxN2press = self.plan.maxTCnitrogen
        zeroLevel = self.plot_height / 2.0 + 10
        for tc in range(ModelPoint.COMPS):
            color = colors[tc]
            #color = QColor(tc*15, 15+(tc*15), 255-tc*15)
            qp.setPen(QPen(color, 1, Qt.SolidLine))

            x1, y1 = (0, 0)
            for n, mPoint in enumerate( self.plan.model ):
                x = (n / len(self.plan.model)) * self.plot_width
                pressure = mPoint.tissues[tc].nitrogenPressure
                y =  zeroLevel - ( (pressure / maxN2press) * (self.plot_height /2.0))
                qp.drawLine(x1, y1, x, y)
                x1 = x
                y1 = y

        qp.setPen(QPen(Qt.black, 1, Qt.DashLine))
        qp.drawText(10, 10, 'Nitrogen tissue compartment pressures')

        # draw gridlines
        pLine= 0.0
        while pLine < maxN2press:
            lineLevel = zeroLevel - (self.plot_height/2.0 * (pLine / maxN2press))
            qp.drawLine(0, lineLevel, self.plot_width, lineLevel)
            qp.drawText(self.plot_width + 5, lineLevel, '{:.1f}'.format(pLine))
            pLine += 0.5
        # draw ticks
        qp.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine))
        dd = 0.0
        while dd < maxN2press:
            y = zeroLevel - (self.plot_height/2.0 * (dd / maxN2press))
            qp.drawLine(self.plot_width - 5, y, self.plot_width + 4, y)
            dd += 0.1

        # Helium TC's next
        heScale = 2.2
        maxHEpress = self.plan.maxTChelium
        if maxHEpress == 0:
            qp.drawText(10, self.plot_height, 'NO HELIUM USED')
            return # there is no helium
        zeroLevel = self.plot_height
        for tc in range(ModelPoint.COMPS):
            color = colors[tc]
            #color = QColor(255-(tc*10), tc*10, tc*10)
            qp.setPen(QPen(color, 1, Qt.SolidLine))
            x1, y1 = (0, 0)
            for n, mPoint in enumerate( self.plan.model ):
                x = (n / len(self.plan.model)) * self.plot_width
                pressure = mPoint.tissues[tc].heliumPressure
                y =  zeroLevel - ( (pressure / maxHEpress) * (self.plot_height/heScale))
                qp.drawLine(x1, y1, x, y)
                x1 = x
                y1 = y

        qp.setPen(QPen(Qt.darkGreen, 1, Qt.DashLine))
        qp.drawLine(0, zeroLevel, self.plot_width, zeroLevel)
        qp.drawText(0, zeroLevel+10, 'Helium tissue compartment pressures')

        # draw gridlines
        pLine= 0.0
        while pLine < maxHEpress:
            lineLevel = zeroLevel - (self.plot_height/heScale * (pLine / maxHEpress))
            qp.drawLine(0, lineLevel, self.plot_width, lineLevel)
            qp.drawText(self.plot_width + 10, lineLevel, '{:.1f}'.format(pLine))
            pLine += 0.5
        # draw ticks
        qp.setPen(QPen(Qt.darkGreen, 1, Qt.SolidLine))
        dd = 0.0
        while dd < maxHEpress:
            y = zeroLevel - (self.plot_height/heScale * (dd / maxHEpress))
            qp.drawLine(self.plot_width +5, y, self.plot_width + 9, y)
            dd += 0.1


    def drawPressureGrid(self, qp, max, zeroLevel):
        qp.setPen(Qt.darkRed)
        # pressure lines
        for pLevel in range(max):
            y = int((pLevel / self.depthMax) * self.plot_height)
            qp.drawLine(0, y, self.plot_width, y)
            ltext = '{:d} m'.format(pLevel)
            qp.drawText(self.plot_width + 10, y + 5, ltext)
        # ticks at 1 meter intervals
        for dd in range(0, int(self.depthMax), 1):
            y = int((dd / self.depthMax) * self.plot_height)
            qp.drawLine(self.plot_width + 4, y, self.plot_width + 9, y)

    def drawDepthGrey(self, qp):

        if not self.plan.profileSampled :
            return

        self.totalTime = self.plan.profileSampled[-1].time
        self.depthMax = self.plan.maxDepth

        # now we plot the DEPTH profile
        depthPath = QPainterPath()
        depthPath.moveTo(0.0, 0.0)
        for n, point in enumerate( self.plan.profileSampled):
            x = (point.time / self.totalTime ) * self.plot_width
            y = (point.depth  / self.depthMax) * self.plot_height
            depthPath.lineTo(x, y)

        depthPath.lineTo(self.plot_width, 0.0)
        depthPath.lineTo(0.0, 0.0)
        depthPath.closeSubpath()
        qp.setBrush(QColor(240,240,240))
        qp.drawPath(depthPath)

class PlotPressureGraphWidget(QWidget):
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
        self.drawPG(self.qp, self.plan.PGplot)
        self.drawMvalueLines(self.qp, self.plan.PGplot, self.plan.GFhigh, self.plan.GFlow)
        #self.drawMV(self.qp)
        self.qp.end()

    def drawSize(self, qp):
        size = self.size()
        self.plot_width = size.width()
        self.plot_height = size.height()

    def drawPG(self, qp, plot ='Total'):
        if not self.plan.model :
            return

        scaler = 5.0
        offset = -1.0
        qp.setPen(QPen(Qt.darkCyan, 2, Qt.DashLine))
        qp.drawLine(0, self.plot_height , self.plot_width, 0)
        # do x y plot on ambient vs tissue pressures
        for tc in range(ModelPoint.COMPS):
            color = colors[tc]
            qp.setPen(QPen(color, 2, Qt.SolidLine))
            qp.drawText(5, 40 + tc * 10, 'TC {}'.format(tc))
            x1, y1 = (0, self.plot_height)

            for n, mPoint in enumerate( self.plan.model ):
                #x =  (((mPoint.ambient + offset) / scaler) * self.plot_width)
                x = scaleToX(mPoint.ambient, scaler, offset, self.plot_width)
                if plot=='Total':
                    qp.drawText(5, 10 , 'Nitrogen + Helium Pressure plot')
                    TCpressure = mPoint.tissues[tc].nitrogenPressure \
                                 + mPoint.tissues[tc].heliumPressure
                elif plot=='Nitrogen':
                    qp.drawText(5, 10 , 'Nitrogen Pressure plot')
                    TCpressure = mPoint.tissues[tc].nitrogenPressure
                elif plot == 'Helium':
                    qp.drawText(5, 10 , 'Helium Pressure plot')
                    TCpressure = mPoint.tissues[tc].heliumPressure
                else:
                    break
                #y =   self.plot_height - (((TCpressure +offset) / scaler) * self.plot_height)
                y = scaleToY(TCpressure, scaler, offset, self.plot_height)
                qp.drawLine(x1, y1, x, y)
                x1, y1 = x, y

    def drawMvalueLines(self, qp, plot ='Total', ghHigh = 1.0, gfLow = 1.0):
        scaler = 5.0
        offset = -1.0
        qp.drawText(5, 20, 'GF high = {}, GFlow = {}'.format(ghHigh, gfLow))
        for tc in range(ModelPoint.COMPS):
            color = colors[tc]
            qp.setPen(QPen(color, 1, Qt.SolidLine))
            if plot == 'Total':
                break
            elif plot=='Nitrogen':
                a = self.plan.modelUsed[tc].NitrogenA
                b = self.plan.modelUsed[tc].NitrogenB
            elif plot == 'Helium':
                a = self.plan.modelUsed[tc].HeliumA
                b = self.plan.modelUsed[tc].HeliumB
            x1 = 0
            y1 = scaleToY( 1.0/b +a , scaler, offset, self.plot_height)
            x2 = scaleToX( (6.0-a) *b, scaler, offset, self.plot_width)
            y2 = scaleToY( 6.0 , scaler, offset, self.plot_height)
            qp.drawLine(  x2, y2, x1, y1)



    def drawMV(self, qp):
        if not self.plan.model :
            return

        scaler = 5.0
        #qp.setPen(QPen(Qt.darkCyan, 2, Qt.DashLine))
        #qp.drawLine(0, self.plot_height , self.plot_width, 0)
        # do x y plot on ambient vs tissue pressures
        for tc in range(ModelPoint.COMPS):
            color = colors[tc]
            qp.setPen(QPen(color, 1, Qt.DotLine))
            x1, y1 = (0, self.plot_height)

            for n, mPoint in enumerate( self.plan.model ):
                x =  (((mPoint.ambient -0.5) / scaler) * self.plot_width)
                mValue = mPoint.tissues[tc].mv
                y =   self.plot_height - (((mValue-0.5) / scaler) * self.plot_height)
                qp.drawLine(x1, y1, x, y)
                x1 = x
                y1 = y

def scaleToX(input, scaler, offset, plot_width):
    return ((input + offset) / scaler) * plot_width

def scaleToY(input, scaler, offset, plot_height):
    return plot_height - (((input +offset) / scaler) * plot_height)