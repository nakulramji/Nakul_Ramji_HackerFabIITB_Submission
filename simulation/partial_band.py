import json
from hotplate_sim import *
from design_final import R,t,zdepth,LAY
pl=Plate(R=R,t=t,dx=0.005)
res={}
for layers,name in ((6,"full-height band (30 mm)"),(3,"top-15 mm band (as built)")):
    for Tset in (90,150,400):
        row=[]
        for f in (0.3,0.4,0.5,0.6,0.7):
            P,r,s=pl.power_for_setpoint(Tset,LAY,rim_frac=f,rim_layers=layers,z_depth=zdepth)
            row.append((f,round(s['span'],3)))
        best=min(row,key=lambda x:x[1])
        res[f"{name}|{Tset}"]=dict(sweep=row,best=best)
        print(f"{name:28s} T={Tset}: span vs rim fraction {row}  best={best}",flush=True)
json.dump(res,open("partial_band.json","w"),indent=1)
