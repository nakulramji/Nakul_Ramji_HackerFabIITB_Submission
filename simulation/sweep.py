import time
from hotplate_sim import *
def run(name, R=0.075, t=0.025, dx=0.005, layout=None, Tset=400, **kw):
    pl=Plate(R=R,t=t,dx=dx)
    P,r,s=pl.power_for_setpoint(Tset,layout,**kw)
    print(f"{name:55s} P={P:6.1f}W span={s['span']:.2f}K min={s['tmin']-Tset:+.2f} max={s['tmax']-Tset:+.2f} Qtop={r['Qtop']:.0f} Qs={r['Qside']:.0f} Qb={r['Qbot']:.0f}", flush=True)
    return P,r,s
L4=[(-0.045,0.10,1),(-0.015,0.10,1),(0.015,0.10,1),(0.045,0.10,1)]
L4w=[(-0.045,0.10,1.6),(-0.015,0.10,1),(0.015,0.10,1),(0.045,0.10,1.6)]
L5=[(-0.05,0.10,1),(-0.025,0.10,1),(0.0,0.10,1),(0.025,0.10,1),(0.05,0.10,1)]
L4wide=[(-0.060,0.08,1.5),(-0.020,0.10,1),(0.020,0.10,1),(0.060,0.08,1.5)]
t0=time.time()
run("A  R75 t25 4eq insulated", layout=L4, z_depth=0.017)
run("B  R75 t25 4 outer x1.6", layout=L4w, z_depth=0.017)
run("C  R75 t25 5eq", layout=L5, z_depth=0.017)
run("D  R75 t25 4 wide-outer x1.5", layout=L4wide, z_depth=0.017)
run("E  R75 t25 4eq BARE sides h=20", layout=L4, z_depth=0.017, h_side=20)
run("F  R75 t25 4eq cleanroom airflow hc_top=20", layout=L4, z_depth=0.017, hc_top=20)
run("G  R50 t25 4eq (plate = wafer size)", R=0.05, layout=[(-0.03,0.07,1),(0.0,0.08,1),(0.03,0.07,1)], z_depth=0.017)
run("H  R85 t25 4eq", R=0.085, layout=[(-0.055,0.10,1),(-0.02,0.12,1),(0.02,0.12,1),(0.055,0.10,1)], z_depth=0.017)
run("I  R75 t20 4eq z=12", t=0.02, layout=L4, z_depth=0.012)
run("J  R75 t30 4eq z=22", t=0.03, layout=L4, z_depth=0.022)
print("elapsed",time.time()-t0)
