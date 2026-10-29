import json
from hotplate_sim import *
from design_final import R,t,zdepth,LAY,DX,point_temp
pl=Plate(R=R,t=t,dx=DX)
def case(name,Tset=400,f=0.5,lay=LAY,**kw):
    P,r,s=pl.power_for_setpoint(Tset,lay,rim_frac=f,z_depth=zdepth,**kw)
    print(f"{name:58s} P={P:5.0f}W span={s['span']:.3f}K min={s['tmin']-Tset:+.2f} max={s['tmax']-Tset:+.2f}",flush=True)
    return dict(name=name,P=P,span=s['span'],mn=s['tmin']-Tset,mx=s['tmax']-Tset)
out=[]
print("== nominal, fixed split f=0.5 (open loop, no zone trim)")
out.append(case("nominal 400C f=0.5"))
print("== zone split error (what happens if band/cartridge ratio is off)")
for f in (0.35,0.40,0.60,0.65):
    out.append(case(f"split error: rim fraction {f}",f=f))
print("== cartridge power tolerance (+-10 % on side rows)")
out.append(case("side rows -10%", lay=[(-0.035,0.10,0.9),(0.0,0.12,1),(0.035,0.10,0.9)]))
out.append(case("one side row -10%", lay=[(-0.035,0.10,0.9),(0.0,0.12,1),(0.035,0.10,1.0)]))
out.append(case("one side row -10%, other +10%", lay=[(-0.035,0.10,0.9),(0.0,0.12,1),(0.035,0.10,1.1)]))
print("== environment")
out.append(case("cleanroom airflow (hc_top 20)", hc_top=20))
out.append(case("emissivity 0.6 (oxidised)", eps_top=0.6))
out.append(case("emissivity 0.05 (polished)", eps_top=0.05))
out.append(case("weak bottom insulation (h_bot 12)", h_bot=12))
out.append(case("no side insulation (h_side 20), band still on", h_side=20))
json.dump(out,open("robustness.json","w"),indent=1)
