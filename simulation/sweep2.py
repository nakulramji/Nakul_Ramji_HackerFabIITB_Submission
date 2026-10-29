import time
from hotplate_sim import *
def run(name, R=0.075, t=0.025, dx=0.005, layout=None, Tset=400, **kw):
    pl=Plate(R=R,t=t,dx=dx)
    P,r,s=pl.power_for_setpoint(Tset,layout,**kw)
    print(f"{name:60s} P={P:6.1f}W span={s['span']:.2f}K min={s['tmin']-Tset:+.2f} max={s['tmax']-Tset:+.2f}", flush=True)
    return P,r,s
def comb(ys, Ls, ws=None):
    ws = ws or [1]*len(ys)
    return [(y,L,w) for y,L,w in zip(ys,Ls,ws)]
# longer heaters towards the rim (x direction), stronger outer rows
for t,z in ((0.025,0.017),(0.030,0.022)):
    for Lin in (100,120,140):
        for wout in (1.0,1.5):
            lay=comb([-0.05,-0.017,0.017,0.05],[100,Lin,Lin,100],[wout,1,1,wout])
            run(f"t={t*1000:.0f} y=+-50/17 Lin={Lin} wout={wout}", t=t, layout=lay, z_depth=z)
# 6 heaters
lay6=comb([-0.055,-0.033,-0.011,0.011,0.033,0.055],[110,130,140,140,130,110],[1.3,1,1,1,1,1.3])
run("t=30 six heaters", t=0.03, layout=lay6, z_depth=0.022)
lay6b=comb([-0.060,-0.036,-0.012,0.012,0.036,0.060],[100,125,140,140,125,100],[1.6,1.1,1,1,1.1,1.6])
run("t=30 six heaters stronger outer", t=0.03, layout=lay6b, z_depth=0.022)
