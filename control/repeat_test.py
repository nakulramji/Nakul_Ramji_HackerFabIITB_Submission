"""Run-to-run repeatability: 30 runs per setpoint, random ambient (21 +-1.5 C), mains (+-8 %), sensor noise seeds,
random start state (cold or warm-soaked at 60 C), same procedure. Metric = spread of mean sensor temp in the hold window
just before wafer load (what a process would 'see')."""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from control_sim import *
rng=np.random.default_rng(7)
out={}
for Tset in (90,150,400):
    means=[]; 
    for k in range(30):
        Tamb=21+rng.uniform(-1.5,1.5); v=1+rng.uniform(-0.08,0.08)
        T0=Tamb if k%2==0 else 60.0
        lg=run(Tset,Tamb=Tamb,vmains=v,T0=T0,seed=100+k)
        t=lg[:,0]; sel=(t>=2300)&(t<2680)
        means.append(lg[sel,2].mean())
    means=np.array(means)
    out[str(Tset)]=dict(mean=float(means.mean()),sd=float(means.std()),spread=float(means.max()-means.min()),
                        mean_err=float(means.mean()-Tset))
    print(Tset,out[str(Tset)],flush=True)
json.dump(out,open("repeatability.json","w"),indent=1)
