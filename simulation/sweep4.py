import itertools
from hotplate_sim import *
def span(pl, layout, Tset=400, **kw):
    P,r,s=pl.power_for_setpoint(Tset,layout,**kw)
    return P,s
def row(y,L,w=1): return (y,L,w)
print("=== R=75 (150 mm), t=25, realistic heated lengths (metres)")
pl=Plate(R=0.075,t=0.025,dx=0.005)
best=None
for yo,yi,Lo,Li,wo in itertools.product((0.045,0.05,0.055),(0.0,0.017,0.025),(0.08,0.10),(0.10,0.13),(1.0,1.3,1.6)):
    if yi==0.0:
        lay=[row(-yo,Lo,wo),row(0,Li,1),row(yo,Lo,wo)]
    else:
        lay=[row(-yo,Lo,wo),row(-yi,Li),row(yi,Li),row(yo,Lo,wo)]
    P,s=span(pl,lay,z_depth=0.017)
    tag=f"yo={yo*1000:.0f} yi={yi*1000:.0f} Lo={Lo*1000:.0f} Li={Li*1000:.0f} wo={wo}"
    if best is None or s['span']<best[0]: best=(s['span'],tag,P,s)
    print(f"{tag:48s} P={P:5.1f} span={s['span']:.2f} min={s['tmin']-400:+.2f} max={s['tmax']-400:+.2f}",flush=True)
print("BEST",best)
