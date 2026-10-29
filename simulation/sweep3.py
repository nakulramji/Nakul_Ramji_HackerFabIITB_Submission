import time
from hotplate_sim import *
def run(name, pl, layout, Tset=400, **kw):
    P,r,s=pl.power_for_setpoint(Tset,layout,**kw)
    print(f"{name:62s} P={P:6.1f}W span={s['span']:.2f}K min={s['tmin']-Tset:+.2f} max={s['tmax']-Tset:+.2f}", flush=True)
    return P,r,s
pl=Plate(R=0.075,t=0.025,dx=0.005)
def lay(yo=0.05,yi=0.017,Lo=100,Li=110,wo=(1,1),wi=(1,1)):
    return [(-yo,Lo,wo[0]),(-yi,Li,wi[0]),(yi,Li,wi[1]),(yo,Lo,wo[1])]
kw=dict(z_depth=0.017)
print("--- cartridge heated lengths (realistic: outer 80 mm, inner 100 mm)")
run("nominal Lo=100 Li=110", pl, lay(), **kw)
run("Lo=80  Li=100", pl, lay(Lo=80,Li=100), **kw)
run("Lo=60  Li=100", pl, lay(Lo=60,Li=100), **kw)
print("--- outer row position")
for yo in (0.045,0.05,0.055,0.06):
    run(f"yo={yo*1000:.0f} mm yi=17 Lo=80 Li=100", pl, lay(yo=yo,Lo=80,Li=100), **kw)
print("--- heater power tolerance (one heater 10% weak / strong)")
base=dict(Lo=80,Li=100)
run("one outer heater -10%", pl, lay(wo=(0.9,1.0),**base), **kw)
run("one outer -10%, other +10%", pl, lay(wo=(0.9,1.1),**base), **kw)
run("inner pair -10%", pl, lay(wi=(0.9,0.9),**base), **kw)
run("outer pair -10% (inner nominal)", pl, lay(wo=(0.9,0.9),**base), **kw)
run("outer pair +10%", pl, lay(wo=(1.1,1.1),**base), **kw)
print("--- environment sensitivity")
run("cleanroom airflow hc_top=20", pl, lay(**base), z_depth=0.017, hc_top=20)
run("eps_top=0.05 (polished)", pl, lay(**base), z_depth=0.017, eps_top=0.05)
run("eps_top=0.6 (oxidised/anodised)", pl, lay(**base), z_depth=0.017, eps_top=0.6)
run("bare sides h_side=20", pl, lay(**base), z_depth=0.017, h_side=20)
run("bottom h=12 (weaker insulation)", pl, lay(**base), z_depth=0.017, h_bot=12)
print("--- other setpoints")
for T in (90,150,250):
    run(f"setpoint {T}", pl, lay(**base), Tset=T, **kw)
print("--- thickness")
for t,z in ((0.02,0.014),(0.03,0.02)):
    run(f"t={t*1000:.0f}", Plate(R=0.075,t=t,dx=0.005), lay(**base), z_depth=z)
print("--- plate diameter")
run("R=65 (130 mm)", Plate(R=0.065,t=0.025,dx=0.005), [(-0.045,70,1),(-0.015,90,1),(0.015,90,1),(0.045,70,1)], z_depth=0.017)
run("R=85 (170 mm)", Plate(R=0.085,t=0.025,dx=0.005), [(-0.055,90,1),(-0.017,120,1),(0.017,120,1),(0.055,90,1)], z_depth=0.017)
