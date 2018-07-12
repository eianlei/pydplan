from dipplanner.model.buhlmann.model import *
from dipplanner.tools import *
from dipplanner.settings import *




def printConstantsCode():
    for num, comp in enumerate(model.tissues):
            print(
"""     tcConstants(name='{}',
            NitrogenHT= {:.2f}, HeliumHT  = {:.2f},
            NitrogenA = {:.4f}, NitrogenB = {:.4f},
            HeliumA =   {:.4f} ,HeliumB   = {:.4f} ),"""\
.format(num+1,
            comp.h_n2, comp.h_he,
            comp.a_n2, comp.b_n2,
            comp.a_he, comp.b_he))


for cModel in ['ZHL16a', 'ZHL16b', 'ZHL16c']:

    model = Model()
    model.set_time_constants(deco_model=cModel, comp1='1b')
    print('  "{}" : ['.format(cModel))
    printConstantsCode()
    print('    ],')