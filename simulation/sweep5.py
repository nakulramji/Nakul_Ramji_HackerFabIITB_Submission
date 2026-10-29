import itertools
from hotplate_sim import *
def row(y,L,w=1): return (y,L,w)
for R in (0.080,0.085):
    pl=Plate(R=R,t=0.025,dx=0.005)
    res=[]
    for yo,yi,Lo,Li,wo in itertools.product((0.050,0.055),(0.015,0.018,0.021),(0.09,0.10),(0.12,0.125),(0.8,1.0,1.2)):
        lay=[row(-yo,Lo,wo),row(-yi,Li),row(yi,Li),row(yo,Lo,wo)]
        P,r,s=pl.power_for_setpoint(400,lay,z_depth=0.017)
        res.append((s['span'],yo,yi,Lo,Li,wo,P,s['tmin']-400,s['tmax']-400))
    res.sort()
    print(f"=== R={R*1000:.0f} mm  top 6 layouts")
    for t in res[:6]:
        print(f"span={t[0]:.2f}K yo={t[1]*1000:.0f} yi={t[2]*1000:.0f} Lo={t[3]*1000:.0f} Li={t[4]*1000:.0f} wo={t[5]} P={t[6]:.0f}W min={t[7]:+.2f} max={t[8]:+.2f}",flush=True)
