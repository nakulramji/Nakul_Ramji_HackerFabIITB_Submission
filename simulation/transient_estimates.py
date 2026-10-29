"""Lumped (single-node) estimates of ramp time, cooling time, thermal bow, ripple. Uses steady-state losses from the 3D model."""
import numpy as np, json
rho=2700.0; R=0.080; t=0.030
m=np.pi*R**2*t*rho                      # plate mass, kg
def cp(T): return 880.0+0.45*(T-25.0)   # J/kg.K, rough 6061 fit (880 @25C -> ~1050 @400C)
Tpts=np.array([25,90,150,250,400.0]); Lpts=np.array([0,24,47,90,169.0])   # W, from 3D model (open-air, insulated sides/bottom)
def loss(T): return np.interp(T,Tpts,Lpts)
def ramp(Tset,P=800.0,dt=1.0):
    T=25.0; time=0
    while T<Tset-2 and time<7200:
        T+=(P-loss(T))/(m*cp(T))*dt; time+=dt
    return time
def cool(T0,T1):
    T=T0; time=0
    while T>T1 and time<40000:
        T-=loss(T)/(m*cp(T))*1.0; time+=1
    return time
out={"mass_kg":m,"ramp_800W_s":{str(T):ramp(T) for T in (90,150,250,400)},
     "ramp_400W_s":{str(T):ramp(T,400) for T in (90,150,250,400)},
     "cool_400_to_100_s":cool(400,100),"cool_150_to_50_s":cool(150,50)}
# thermal bow during full-power ramp (free plate, linear gradient across thickness)
k=170.0; alpha=23.6e-6; A=np.pi*R**2
q=800.0/A*0.5            # assume half of heat flows upward during a ramp
dTz=q*0.021/k            # heater plane -> top, 21 mm
kappa=alpha*dTz/t
out["bow_um_ramp"]=kappa*0.1**2/8*1e6
out["dTz_ramp_K"]=dTz
# steady-state at 400C
q_ss=169.0/A*0.55; dTz_ss=q_ss*0.021/k
out["bow_um_steady400"]=alpha*dTz_ss/t*0.1**2/8*1e6
# radial thermal expansion at 400C
out["growth_mm_dia_400"]=alpha*375*160
# time constant for cooling at 400
out["tau_400_min"]=m*cp(300)/(169/375)/60
# wafer-plate air gap temperature drop (400 C and 150 C): q/(k_air/g)
for T,qw,kair in ((400,9300.0,0.050),(150,1700.0,0.034)):
    out[f"gap_drop_K_per_10um_{T}"]=qw*10e-6/kair
# SSR ripple at top surface (window 1 s, 169 W avg of 800 W)
alpha_d=k/(rho*900.0); omega=2*np.pi/1.0
decay=np.exp(-np.sqrt(omega/(2*alpha_d))*0.021)
out["ripple_attenuation_top"]=decay
json.dump(out,open("transient_estimates.json","w"),indent=1)
print(json.dumps(out,indent=1))
