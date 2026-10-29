"""Final design evaluation: 3 cartridge rows + rim band heater, dual-zone control."""
import json, numpy as np
from hotplate_sim import *
R, t, zdepth = 0.080, 0.030, 0.021           # 160 mm dia, 30 mm thick, cartridges 9 mm above bottom
LAY = [(-0.035,0.10,1),(0.0,0.12,1),(0.035,0.10,1)]   # y position, heated length (m), relative power
DX = 0.005

def point_temp(pl, T, r_mm):
    """temperature at top surface on +x axis at radius r_mm (nearest cells)"""
    f = pl.top_field(T)
    iy = pl.n//2
    xi = np.argmin(np.abs(pl.xs - r_mm/1000.0))
    return float(0.5*(f[xi,iy]+f[xi,iy-1]))

def sweep(pl, Tset, fs, **kw):
    out=[]
    for f in fs:
        P,r,s = pl.power_for_setpoint(Tset, LAY, rim_frac=f, z_depth=zdepth, **kw)
        out.append(dict(f=f,P=P,span=s['span'],mn=s['tmin']-Tset,mx=s['tmax']-Tset,
                        Tc=point_temp(pl,r['T'],0)-Tset, T45=point_temp(pl,r['T'],45)-Tset,
                        Qtop=r['Qtop'],Qs=r['Qside'],Qb=r['Qbot']))
    return out
if __name__=="__main__":
    pl=Plate(R=R,t=t,dx=DX)
    results={}
    for Tset in (90,150,250,400):
        res=sweep(pl,Tset,[0.0,0.2,0.3,0.4,0.5,0.6,0.7,0.8])
        results[Tset]=res
        print(f"--- setpoint {Tset} C")
        for r in res:
            print(f"  rim frac {r['f']:.1f}: P={r['P']:.0f}W span={r['span']:.3f}K  centre={r['Tc']:+.2f} r45={r['T45']:+.2f}")
    json.dump(results,open("sweep_rimfrac.json","w"),indent=1)
