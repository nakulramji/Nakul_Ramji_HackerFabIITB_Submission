import json, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from hotplate_sim import *
from design_final import R,t,zdepth,LAY,DX
pl=Plate(R=R,t=t,dx=DX)

def field(Tset,f):
    P,r,s=pl.power_for_setpoint(Tset,LAY,rim_frac=f,z_depth=zdepth)
    return P,r,s

# Figure 1: top-surface deviation maps at 400 C, with and without rim heater
fig,axs=plt.subplots(1,2,figsize=(11,4.8))
vals=[]
for ax,(f,title) in zip(axs,((0.0,"Cartridges only (single zone)"),(0.5,"Cartridges + rim band heater (dual zone)"))):
    P,r,s=field(400,f)
    F=pl.top_field(r["T"])-s["mean"]
    ex=[-R*1000,R*1000,-R*1000,R*1000]
    im=ax.imshow(F.T,origin="lower",extent=ex,cmap="coolwarm",vmin=-1.2,vmax=1.2)
    ax.add_patch(Circle((0,0),50,fill=False,lw=2,ec="k"))
    ax.set_title(f"{title}\n100 mm zone span = {s['span']:.2f} K",fontsize=10)
    ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)")
    ax.text(0,-72,"black circle = 4-inch wafer",ha="center",fontsize=8)
fig.colorbar(im,ax=axs,label="top-surface temperature minus wafer-zone mean (K)",shrink=0.85)
fig.suptitle("Simulated top-surface temperature at 400 C setpoint (steady state)",fontsize=11)
fig.savefig("../figures/fig1_uniformity_map_400C.png",dpi=160,bbox_inches="tight"); plt.close(fig)

# Figure 2: span vs setpoint, with and without rim zone
sp={}
for f in (0.0,0.5):
    sp[f]=[]
    for T in (90,150,250,400):
        P,r,s=field(T,f); sp[f].append(s["span"])
fig,ax=plt.subplots(figsize=(6.4,4.2))
x=np.arange(4); w=0.36
ax.bar(x-w/2,sp[0.0],w,label="cartridges only",color="#c0504d")
ax.bar(x+w/2,sp[0.5],w,label="cartridges + rim band (50 % of power)",color="#4f81bd")
ax.axhline(1.0,color="k",ls="--"); ax.text(3.45,1.02,"spec limit: 1.0 K span (+-0.5 K)",ha="right",fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(["90","150","250","400"]); ax.set_xlabel("setpoint (C)")
ax.set_ylabel("max - min over 100 mm wafer zone (K)"); ax.legend(fontsize=8,loc="upper left"); ax.set_title("Simulated uniformity vs setpoint",fontsize=10)
fig.savefig("../figures/fig2_span_vs_setpoint.png",dpi=160,bbox_inches="tight"); plt.close(fig)
json.dump({str(k):v for k,v in sp.items()},open("span_vs_setpoint.json","w"))

# Figure 3: vertical section at 400 C (dual zone)
P,r,s=field(400,0.5)
S=pl.section_field(r["T"])-s["mean"]
fig,ax=plt.subplots(figsize=(7,2.8))
im=ax.imshow(S.T,origin="upper",extent=[-R*1000,R*1000,t*1000,0],cmap="coolwarm",vmin=-6,vmax=6,aspect="equal")
ax.set_xlabel("x (mm)"); ax.set_ylabel("depth below top surface (mm)")
ax.set_title("Cross-section temperature (dual zone, 400 C): heater plane is warmer, top is flat",fontsize=9)
fig.colorbar(im,label="K relative to wafer-zone mean",shrink=0.9)
fig.savefig("../figures/fig3_cross_section_400C.png",dpi=160,bbox_inches="tight"); plt.close(fig)
print("spans",sp)
