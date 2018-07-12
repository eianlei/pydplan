from pydplan.pydplan_buhlmann import *

bm = Buhlmann()

print('comp Half times   A      B       A      B')
print('# Nitrogen Helium Nitrogen       Helium')
for mod  in ['ZHL16a', 'ZHL16b', 'ZHL16c']:
    print('{} model constants'.format(mod))
    for comp in  bm.model[mod] :
        print('{:>2} {:>6.2f} {:>6.2f}  {:>6.4f} {:>6.4f}  {:>6.4f} {:>6.4f} | {:>6.4f} {:>6.4f} '\
              .format(comp.name,
                      comp.NitrogenHT, comp.HeliumHT,
                      comp.NitrogenA, comp.NitrogenB,
                      comp.HeliumA, comp.HeliumB,
                      comp.NitrogenK, comp.HeliumK))