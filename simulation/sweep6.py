from hotplate_sim import *
def lay(wo=1.0,yo=0.05,yi=0.015,Lo=0.10,Li=0.125):
    return [(-yo,Lo,wo),(-yi,Li,1),(yi,Li,1),(yo,Lo,wo)]
print("=== thickness effect, R=85, heaters 9 mm above bottom, setpoint 400")
for t in (0.025,0.030,0.035,0.040):
    pl=Plate(R=0.085,t=t,dx=0.005)
    P,r,s=pl.power_for_setpoint(400,lay(),z_depth=t-0.009)
    print(f"t={t*1000:.0f}  P={P:.0f}W span={s['span']:.2f}K min={s['tmin']-400:+.2f} max={s['tmax']-400:+.2f}",flush=True)
print("=== outer/inner power ratio vs setpoint (t=30, R=85)")
pl=Plate(R=0.085,t=0.030,dx=0.005)
for Tset in (90,150,250,400):
    out=[]
    for wo in (0.6,0.8,1.0,1.2,1.4,1.7,2.0):
        P,r,s=pl.power_for_setpoint(Tset,lay(wo=wo),z_depth=0.021)
        out.append((s['span'],wo,P))
    out.sort()
    print(f"T={Tset}: best ratio wo={out[0][1]} span={out[0][0]:.3f}K P={out[0][2]:.0f}W | wo=1.0 span={[o for o in out if o[1]==1.0][0][0]:.3f}K",flush=True)
