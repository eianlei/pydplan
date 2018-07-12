#
# (c) 2018 Ian Leiman, ian.leiman@gmail.com
# pydplan_table
# part of PYDPLAN, a Python Dive Planner with PyQt5 GUI
# table tools
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget
from PyQt5.QtCore import Qt
#from pydplan.pydplan_classes import DivePlan
from pydplan_profiletools import DiveProfilePoint

def tableUpdate(tableW: QTableWidget, modelRun: list):

    rows = len(modelRun)
    columns = 40
    tableW.setRowCount(rows)
    tableW.setColumnCount(columns)
    tableW.setAlternatingRowColors(True)

    for tc in range(0, modelRun[0].COMPS):
        tableW.setHorizontalHeaderItem(tc*2, QTableWidgetItem('{}:N2'.format(tc)))
        tableW.setHorizontalHeaderItem((tc*2)+1, QTableWidgetItem('{}:He'.format(tc)))

    for row, modelInst in enumerate( modelRun):
        item = str(modelInst.metadata)
        col = 0
        #tableW.setItem(row, col, QTableWidgetItem(item))
        #col += 1
        for tc in range(0, modelInst.COMPS):
            tableW.setItem(row, col, QTableWidgetItem('{:.4f}'.format(modelInst.tissues[tc].pp_n2) ))
            col += 1
            tableW.setItem(row, col, QTableWidgetItem('{:.4f}'.format( modelInst.tissues[tc].pp_he )))
            col += 1

    tableW.resizeColumnsToContents()
    tableW.resizeRowsToContents()
    tableW.show()

def tableUpdate2(tableW: QTableWidget, modelRun: list, profile: list):

    rows = len(modelRun)
    columns = 40
    tableW.setRowCount(rows)
    tableW.setColumnCount(columns)
    tableW.setAlternatingRowColors(True)


    tableW.setHorizontalHeaderItem(0, QTableWidgetItem('pp_N2'))
    tableW.setHorizontalHeaderItem(1, QTableWidgetItem('pp_He'))
    tableW.setHorizontalHeaderItem(2, QTableWidgetItem('pp_tot'))
    tableW.setHorizontalHeaderItem(3, QTableWidgetItem('a_he_n2'))
    tableW.setHorizontalHeaderItem(4, QTableWidgetItem('b_he_n2'))
    tableW.setHorizontalHeaderItem(5, QTableWidgetItem('mv'))

    for row, modelInst in enumerate( modelRun):
        item = str(modelInst.metadata)
        col = 0
        tc = modelInst.tissues[0]

        tableW.setItem(row, col, QTableWidgetItem('{:.4f}'.format(tc.pp_n2) ))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{:.4f}'.format(tc.pp_he )))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{:.4f}'.format(tc.pp_he + tc.pp_n2)))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{:.4f}'.format( tc.a_he_n2 )))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{:.4f}'.format( tc.b_he_n2 )))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{:.4f}'.format( tc.mv )))
        col += 1


    tableW.resizeColumnsToContents()
    tableW.resizeRowsToContents()
    tableW.show()

def tableUpdate3(tableW: QTableWidget, profile: list):
    """
    print a table of the dive profile to the give QTableWidget
    :param tableW:
    :type tableW:
    :param profile:
    :type profile:
    :return:
    :rtype:
    """
    rows = len(profile)
    columns = 28
    tableW.setRowCount(rows)
    tableW.setColumnCount(columns)
    tableW.setAlternatingRowColors(True)

    col_hdr = [
        ('time', 'runtime in min:sec' ),
        ('depth', 'current dive depth in meters'),
        ('phase','current dive phase'),
        ('T', 'currently used scuba tank ID'),
        ('o2/he', 'Oxygen/Helium % in current tank'),
        #('he', 'Helium % in current tank'),
        ('bar', 'Tank pressure in bar'),
        ('ppO2', 'Oxygen partial pressure in bar'),
        ('GF', 'Gradient Factor used'),
        ('C:3m', 'GF Ceiling depth at 3m increment'),
        ('CEIL', 'GF Ceiling depth in meters, no rounding'),
        ('margin', 'Ceiling margin, meters from current depth'),
        ('lead', 'leading/ceiling tissue compartment number'),

        ]
    # table column headers
    c = 0
    for hrdTxt, toolTipTxt in col_hdr:
        tableW.setHorizontalHeaderItem(c, QTableWidgetItem(hrdTxt))
        tableW.horizontalHeaderItem(c).setToolTip(toolTipTxt)
        c += 1
    for tc in range (16):
        tableW.setHorizontalHeaderItem(c, QTableWidgetItem('tc#{}'.format(tc)))
        tableW.horizontalHeaderItem(c).setToolTip('ceiling in meters for tissue compartment number {}'.format(tc))
        c += 1
    # table rows
    point : DiveProfilePoint
    for row, point  in enumerate( profile):
        col = 0
        min, sec = divmod(point.time, 60)
        tableW.setItem(row, col, QTableWidgetItem('{:02.0f}:{:02.0f}'.format(min, sec)))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{:>5.1f}'.format(point.depth)))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{}'.format(point.divephase.name)))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{:s}'.format(point.tank.name)))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{:.0f}/{:.0f}'.format(point.tank.o2, point.tank.he)))
        #col += 1
        #tableW.setItem(row, col, QTableWidgetItem('{:.0f}'.format(point.tank.he)))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{:>3.0f}'.format(point.currentTankPressure)))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{:>4.2f}'.format(point.ppOxygen)))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{:.2f}'.format(point.gfNow)))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{}'.format(point.modelpoint.leadCeilingStop)))
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{:.1f}'.format(point.modelpoint.leadCeilingMeters)))
        col += 1
        margin_now = point.depth - point.modelpoint.leadCeilingMeters
        tableW.setItem(row, col, QTableWidgetItem('{:+.1f}'.format(margin_now)))
        tableW.item(row, col).setTextAlignment(Qt.AlignRight)
        if margin_now < 0:
            tableW.item(row, col).setBackground(Qt.red)
        col += 1
        tableW.setItem(row, col, QTableWidgetItem('{}'.format(point.modelpoint.leadTissue)))
        col += 1

        for ceiling in point.modelpoint.ceilings:
            tableW.setItem(row, col, QTableWidgetItem('{:.1f}'.format(ceiling)))
            col += 1

    tableW.resizeColumnsToContents()
    tableW.resizeRowsToContents()
    #tableW.show()