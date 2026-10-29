from hotplate_sim import *
def L(ys,Ls): return [(y,l,1) for y,l in zip(ys,Ls)]
cfgs={
 "R80 t30: 4 rows (15,50)":      (0.080,0.030,0.021,L([-0.05,-0.015,0.015,0.05],[0.09,0.12,0.12,0.09])),
 "R80 t30: 3 rows (0,+-35)":     (0.080,0.030,0.021,L([-0.035,0.0,0.035],[0.11,0.13,0.11])),
 "R80 t30: 2 rows (+-25)":       (0.080,0.030,0.021,L([-0.025,0.025],[0.13,0.13])),
 "R80 t25: 3 rows (0,+-35)":     (0.080,0.025,0.016,L([-0.035,0.0,0.035],[0.11,0.13,0.11])),
}
for name,(R,t,z,lay) in cfgs.items():
    pl=Plate(R=R,t=t,dx=0.005)
    for Tset in (150,400):
        best=None
        for f in (0.0,0.05,0.10,0.15,0.20,0.25,0.30,0.40):
            P,r,s=pl.power_for_setpoint(Tset,lay,rim_frac=f,z_depth=z)
            if best is None or s['span']<best[0]: best=(s['span'],f,P,s['tmin']-Tset,s['tmax']-Tset)
        print(f"{name:28s} T={Tset}: best rim frac={best[1]:.2f} span={best[0]:.3f}K P={best[2]:.0f}W (min {best[3]:+.2f}, max {best[4]:+.2f})",flush=True)
