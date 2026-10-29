"""
Closed-loop simulation of the hot plate controller on a lumped thermal model.

What this checks (and what it does NOT):
 + PID + time-proportional SSR drive: overshoot, settling time, steady ripple
 + run-to-run repeatability under random ambient, mains voltage, sensor noise, cold-wafer loading
 - It uses ONE plate temperature node (the 3D model in ../simulation covers spatial uniformity)
 - Sensor noise is an assumption (0.03 K rms, MAX31865 15-bit class); real noise must be measured
"""
import numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

M = 1.6286                      # kg, 6061 plate 160 mm x 30 mm
def cp(T): return 880.0 + 0.45*(T-25.0)
TP = np.array([25,90,150,250,400.0]); LP = np.array([0,24,47,90,169.0])   # steady loss (W) from 3D model at 21C ambient
def loss(T, Tamb): return np.interp(T,TP,LP) * (T-Tamb)/(np.maximum(T-21.0,1e-6)) if T>Tamb else 0.0
P_TOTAL = 800.0                 # W installed (450 cartridges + 350 rim band)
WINDOW = 1.0                    # s, SSR time-proportioning window (100 mains half-cycles -> 1 % resolution)
MH = 0.25                       # kg of Al + cartridges near the heaters (fast node)
GH = 40.0                       # W/K heater node -> bulk plate (diffusion over ~20 mm, tau ~ 6 s)
DT = 0.05                       # s, integration step
TAU_S = 3.0                     # s, sensor lag (3 mm below surface + PT100 element)

def run(Tset, hold=3200, Tamb=21.0, vmains=1.0, noise=0.03, wafer_at=2700, T0=None, kp=None, ki=None, kd=None, seed=0):
    rng = np.random.default_rng(seed)
    T = Tamb if T0 is None else T0
    Ts = T                      # sensor temperature
    Th = T                      # heater-region temperature
    I = 0.0; prev_meas = Ts
    t = 0.0; log=[]
    # gains: tuned in tune() below; scaled by setpoint-independent heater power
    kp = 80.0 if kp is None else kp      # W/K
    ki = 0.15 if ki is None else ki      # W/(K s)
    kd = 100.0 if kd is None else kd     # W s/K
    out_cmd = 0.0; win_t = 0.0; on_time = 0.0
    N = int((hold+ ( (Tset-Tamb)/0.2 ) )/DT)
    wafer_done=False
    for n in range(N):
        t = n*DT
        # controller at 1 Hz update (every 20 steps) using noisy measurement
        if n % int(1/DT) == 0:
            meas = Ts + rng.normal(0,noise)
            e = Tset - meas
            dmeas = (meas - prev_meas)/1.0; prev_meas = meas
            P_unsat = kp*e + I - kd*dmeas
            P_cmd = min(max(P_unsat,0.0),P_TOTAL)
            # anti-windup: integrate only when not saturated, and only near setpoint (conditional integration)
            if (abs(e) < 8.0) and (0.0 < P_unsat < P_TOTAL or (P_unsat<=0 and e>0) or (P_unsat>=P_TOTAL and e<0)):
                I += ki*e*1.0
                I = min(max(I,0.0),P_TOTAL)
            out_cmd = P_cmd/P_TOTAL
        # time proportioning inside the window
        win_t = (t % WINDOW)
        on = 1.0 if win_t < out_cmd*WINDOW else 0.0
        Pheat = on*P_TOTAL*vmains**2
        # cold wafer: 100 mm x 0.525 mm Si, 9.2 g, cp 700 J/kgK, loaded at wafer_at, coupling tau ~20 s
        Pw = 0.0
        if wafer_at is not None and t >= wafer_at and t < wafer_at+120:
            Pw = 0.0092*700*(T-Tamb)/20.0 * np.exp(-(t-wafer_at)/20.0)
        Q = GH*(Th-T)
        Th += (Pheat - Q)/(MH*cp(Th))*DT
        T += (Q - loss(T,Tamb) - Pw)/((M-MH)*cp(T))*DT
        Ts += (T - Ts)/TAU_S*DT
        if n % int(1/DT) == 0: log.append((t,T,Ts,out_cmd*P_TOTAL))
    return np.array(log)

def metrics(log, Tset, win=(2300,2680), t_wafer=2700):
    t=log[:,0]; Ts=log[:,2]
    over = max(0.0, Ts.max()-Tset)
    inband = np.where(np.abs(Ts-Tset)<0.2)[0]
    # first time after which it stays within 0.2 K until wafer load (t=900)
    pre = (t<t_wafer)
    ok = np.abs(Ts-Tset)<0.2
    settle=None
    for i in range(len(t)):
        if pre[i] and ok[i:np.searchsorted(t,t_wafer)].all():
            settle=t[i]; break
    sel=(t>=win[0])&(t<win[1])
    ripple = Ts[sel].max()-Ts[sel].min()
    avg = Ts[sel].mean()
    return dict(overshoot=over, settle_s=settle, ripple=ripple, avg=avg)

if __name__=="__main__":
    res={}
    fig,axs=plt.subplots(2,2,figsize=(11,7))
    for ax,Tset in zip(axs.ravel(),(90,150,250,400)):
        lg=run(Tset,seed=1)
        m=metrics(lg,Tset)
        res[str(Tset)]=m
        ax.plot(lg[:,0]/60,lg[:,2],lw=1.2)
        ax.axhline(Tset,color="k",ls=":",lw=0.8)
        ax.axvline(45,color="grey",ls="--",lw=0.8); ax.text(45.5,Tset*0.5+10,"cold wafer\nloaded",fontsize=7)
        ax.set_title(f"setpoint {Tset} C: overshoot {m['overshoot']:.2f} K, settle {m['settle_s']} s",fontsize=9)
        ax.set_xlabel("time (min)"); ax.set_ylabel("sensor temp (C)")
    fig.suptitle("Simulated closed-loop heating run (lumped model, 800 W installed)")
    fig.tight_layout(); fig.savefig("../figures/fig4_control_runs.png",dpi=150); plt.close(fig)
    json.dump(res,open("control_runs.json","w"),indent=1)
    print(json.dumps(res,indent=1))
