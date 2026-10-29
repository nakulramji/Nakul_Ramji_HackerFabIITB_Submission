import itertools, time
from control_sim import *
t0=time.time()
best=[]
for kp,ki,kd in itertools.product((20,40,80),(0.02,0.06,0.15),(100,300,900)):
    ms=[]
    for Tset in (90,400):
        lg=run(Tset,kp=kp,ki=ki,kd=kd,seed=2)
        ms.append(metrics(lg,Tset))
    score=max(m['overshoot'] for m in ms)+ (0 if all(m['settle_s'] for m in ms) else 50)+max(m['ripple'] for m in ms)
    best.append((score,kp,ki,kd,[(round(m['overshoot'],2),m['settle_s'],round(m['ripple'],2)) for m in ms]))
    if time.time()-t0>240: break
best.sort(key=lambda x:x[0])
for b in best[:6]: print(b)
print(len(best),time.time()-t0)
