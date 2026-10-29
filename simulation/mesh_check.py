import json
from hotplate_sim import *
from design_final import R,t,zdepth,LAY
out={}
for dx in (0.005,0.0033333333,0.0025):
    pl=Plate(R=R,t=t,dx=dx)
    for Tset,P in ((400,169.0),(150,47.0)):
        r=pl.solve(P*0.5,LAY,z_depth=zdepth,P_rim=P*0.5)
        s=pl.wafer_stats(r["T"])
        out[f"dx{dx*1000:.2f}mm_{Tset}"]=dict(mean=s['mean'],span=s['span'])
        print(f"dx={dx*1000:.2f} mm  P={P} W: wafer-zone mean={s['mean']:.1f} C span={s['span']:.3f} K",flush=True)
json.dump(out,open("mesh_check.json","w"),indent=1)
