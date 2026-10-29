import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch, Polygon

def dim(ax,p1,p2,text,off=(0,0),fs=8):
    ax.annotate("",xy=p1,xytext=p2,arrowprops=dict(arrowstyle="<->",lw=0.8))
    mx,my=(p1[0]+p2[0])/2+off[0],(p1[1]+p2[1])/2+off[1]
    ax.text(mx,my,text,ha="center",va="center",fontsize=fs,bbox=dict(fc="white",ec="none",pad=0.5))

# ---------- Drawing 1: plate, top view + side section ----------
fig=plt.figure(figsize=(13,6.4))
ax=fig.add_axes([0.03,0.08,0.45,0.82]); ax.set_aspect("equal"); ax.axis("off")
ax.add_patch(Circle((0,0),80,fill=False,lw=2))
ax.add_patch(Circle((0,0),50,fill=False,lw=1,ls="--",ec="tab:red")); ax.text(0,-53,"100 mm wafer zone",ha="center",fontsize=8,color="tab:red")
# cartridge holes (seen as dashed, they are below the surface)
for y,L,Hd in ((-35,100,127),(0,120,145),(35,100,127)):
    ch=np.sqrt(80**2-y**2)
    ax.add_patch(Rectangle((-ch,y-5),Hd,10,fill=False,ls="--",lw=0.9,ec="tab:blue"))
    ax.add_patch(Rectangle((-L/2,y-5),L,10,fill=True,fc="#ffd9a0",alpha=0.5,ec="none"))
    ax.text(-ch-3,y,f"y={y:+d}",ha="right",va="center",fontsize=7)
ax.text(-45,57,"3 x cartridge 150 W (dashed: bore, orange: heated length)",fontsize=7,color="tab:blue")
# sensor bores from the bottom
for (x,y,l) in ((0,17.5,"S1 (0,+17.5)"),(58,-17.5,"S2 (58,-17.5)")):
    ax.add_patch(Circle((x,y),1.6,fc="k")); ax.text(x+3,y+4,l,fontsize=8,fontweight="bold")
ax.add_patch(Circle((-60,25),1.6,fc="tab:green")); ax.text(-57,28,"S3 spare",fontsize=7)
# wafer locating pins
for a in (90,210,330):
    ax.add_patch(Circle((52.5*np.cos(np.radians(a)),52.5*np.sin(np.radians(a))),1.5,fc="tab:purple"))
ax.text(0,64,"3 locating pins Ø3 at r=52.5",ha="center",fontsize=7,color="tab:purple")
# mounting holes M5 on r=70 at 3 positions
for a in (60,180,300):
    ax.add_patch(Circle((70*np.cos(np.radians(a)),70*np.sin(np.radians(a))),2.6,fill=False,lw=1))
ax.text(70*np.cos(np.radians(60))+4,70*np.sin(np.radians(60))+3,"M5 x 10 deep (x3)",fontsize=7)
dim(ax,(-80,-70),(80,-70),"Ø160",off=(0,-6))
ax.set_xlim(-100,100); ax.set_ylim(-85,85)
ax.set_title("A. Top view (surface machined flat to ±10 µm, target ±5 µm)",fontsize=9)

ax2=fig.add_axes([0.52,0.30,0.45,0.55]); ax2.set_aspect("equal"); ax2.axis("off")
ax2.add_patch(Rectangle((-80,0),160,30,fc="#d9d9d9",ec="k",lw=2))
ax2.add_patch(Rectangle((-80,0),160,30,fill=False))
# cartridge bore (section through y=0)
ax2.add_patch(Rectangle((-80,4),145,10,fc="#ffd9a0",ec="tab:blue",lw=1)); ax2.text(0,9,"cartridge Ø10 bore, centre z = 9 mm above bottom",ha="center",va="center",fontsize=7)
# sensor bores from bottom
for x in (0,58):
    ax2.add_patch(Rectangle((x-1.6,0),3.2,27,fc="white",ec="k")); ax2.text(x,-4,"",ha="center",fontsize=6)
ax2.text(0,30.8,"S1/S2 bores Ø3.2 x 27 from bottom, between cartridge rows (not through them)",ha="center",fontsize=6.5)
# band heater on top 15 mm of rim
for x in (-83,80):
    ax2.add_patch(Rectangle((x,15),3,15,fc="tab:red",alpha=0.6,ec="k"))
ax2.text(92,22,"mica band heater\n350 W, top 15 mm",fontsize=7,va="center")
# insulation below and at side
ax2.add_patch(Rectangle((-83,-28),166,22,fc="#f5e6b3",ec="k",hatch="///")); ax2.text(0,-17,"bottom insulation board 25 mm (in sealed SS tray)",ha="center",fontsize=7)
for x in (-60,60):
    ax2.add_patch(Rectangle((x-4,-6),8,6,fc="tab:gray",ec="k")); 
ax2.text(0,-6.5,"",fontsize=6)
ax2.text(-75,-9.5,"3 x alumina standoff Ø8 x 6",fontsize=6.5)
dim(ax2,(-80,36),(80,36),"Ø160",off=(0,4)); dim(ax2,(100,0),(100,30),"30",off=(7,0))
dim(ax2,(-92,4),(-92,14),"",off=(0,0)); 
ax2.set_xlim(-110,125); ax2.set_ylim(-35,48)
ax2.set_title("B. Side section through y = 0 (not to scale in z)",fontsize=9)
fig.text(0.50,0.13,"Material: 6061-T651 Al, pre-aged (3 cycles 25→420→25 °C) BEFORE final grinding.\n"
 "Cartridge bores Ø10 H7, entered from -x: y=-35 and +35: 127 deep; y=0: 145 deep.\n"
 "Heated length 100 / 120 / 100 mm, centred on x = 0. Sensor bores leave 3 mm to the top.\n"
 "Top face ground, Ra ≤ 0.8 µm, flatness ±10 µm (aim ±5 µm). No anodising on top.",fontsize=7.5,va="top")
fig.savefig("drawing1_plate.png",dpi=170); plt.close(fig)

# ---------- Drawing 2: system assembly (exploded cross-section) ----------
fig,ax=plt.subplots(figsize=(11,7)); ax.axis("off"); ax.set_aspect("equal")
def box(x,y,w,h,txt,fc,fs=8,ec="k"):
    ax.add_patch(Rectangle((x,y),w,h,fc=fc,ec=ec,lw=1.2)); ax.text(x+w/2,y+h/2,txt,ha="center",va="center",fontsize=fs)
box(10,78,80,6,"Si wafer (Ø100 x 0.525), 3 locating pins","#c6d9f0")
box(5,62,90,14,"Al 6061-T651 plate Ø160 x 30\n3 cartridges (z=9) + PT100 S1/S2 3 mm below top","#d9d9d9")
box(2,64,3,10,"","#e06666",fs=6); box(95,64,3,10,"","#e06666",fs=6)
ax.text(100,69,"mica band\nheater (rim)",fontsize=7,va="center")
box(8,50,84,6,"3 alumina standoffs (4 pts of contact only)","#bdbdbd",fs=7)
box(5,36,90,12,"Insulation board 25 mm + side wrap 25 mm\n(AES/calcium-silicate, fully inside SS304 tray)","#f5e6b3")
box(0,28,100,6,"SS304 shell 1.5 mm: sealed, no fibres exposed, 4 x M6 feet","#9e9e9e",fs=7)
box(38,10,24,14,"heater leads +\nPT100 cables\nthrough SS gland","#fff2cc",fs=7)
ax.annotate("",xy=(50,26),xytext=(50,24),arrowprops=dict(arrowstyle="->"))
box(105,2,60,38,"Controller box (metal, EARTHED)\n- Arduino + 2x MAX31865\n- 2x SSR 25 A, heat-sunk\n- hardware over-temp\n  thermostat 430 °C\n  (manual reset) + contactor\n- MCB 6 A, RCD\n- front: display, E-stop","#e2efda",fs=7.5)
ax.annotate("",xy=(105,18),xytext=(62,16),arrowprops=dict(arrowstyle="->",lw=1.2))
ax.text(75,9,"≥ 1 m cable, kept away\nfrom the hot plate",fontsize=7)
ax.set_xlim(-8,175); ax.set_ylim(-4,90)
ax.set_title("Assembly (exploded section) and what goes where",fontsize=10)
fig.savefig("drawing2_assembly.png",dpi=170,bbox_inches="tight"); plt.close(fig)

# ---------- Drawing 3: wiring / block ----------
fig,ax=plt.subplots(figsize=(12,6.2)); ax.axis("off"); ax.set_xlim(0,120); ax.set_ylim(0,60)
def b(x,y,w,h,t,fc="#ffffff",fs=8): 
    ax.add_patch(Rectangle((x,y),w,h,fc=fc,ec="k",lw=1.2)); ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=fs)
def arr(p,q,t="",c="k",ls="-"): 
    ax.annotate("",xy=q,xytext=p,arrowprops=dict(arrowstyle="->",lw=1.3,color=c,ls=ls))
    if t: ax.text((p[0]+q[0])/2,(p[1]+q[1])/2+1.2,t,fontsize=7,ha="center",color=c)
b(2,40,16,12,"230 V AC\nmains\n(earth!)","#fde9d9")
b(24,40,14,12,"MCB 6 A\n+ RCD 30 mA","#fde9d9")
b(44,40,18,12,"Contactor\n(coil via safety\nchain)","#fde9d9")
b(68,46,18,10,"Thermostat 430 °C\nmanual reset\n(in coil path)","#f4cccc")
b(68,30,16,10,"SSR-A\n(cartridges\n3 x 150 W)","#fff2cc")
b(68,16,16,10,"SSR-B\n(rim band\n350 W)","#fff2cc")
b(96,30,20,10,"3 cartridge heaters\n(parallel)","#ffd9a0")
b(96,16,20,10,"mica band heater","#ffd9a0")
b(40,4,22,18,"Arduino\n+ 2x MAX31865\n(PT100 4/3-wire)\n+ 5 V PSU","#d9ead3")
b(96,2,20,10,"S1, S2, (S3) PT100\nin plate","#cfe2f3")
b(2,8,26,12,"PC / laptop\nUSB serial 115200\nlogging + CSV","#ead1dc")
for p,q in (((18,46),(24,46)),((38,46),(44,46)),((62,46),(68,42)),((62,44),(68,36)),((62,42),(68,22))): arr(p,q)
arr((84,35),(96,35),"230 V switched"); arr((84,21),(96,21),"230 V switched")
arr((50,22),(70,30),"3.3 V logic",c="tab:green"); arr((52,22),(70,18),"",c="tab:green")
arr((96,7),(62,10),"RTD signals",c="tab:blue")
arr((28,14),(40,14),"USB",c="tab:purple"); 
ax.text(2,2,"Safety chain: mains → MCB/RCD → contactor ← thermostat(430 °C, manual reset) ← E-stop. Software over-temp limit (415 °C) is a second, independent layer.",fontsize=8)
ax.set_title("Block / wiring diagram",fontsize=10)
fig.savefig("drawing3_wiring.png",dpi=170,bbox_inches="tight"); plt.close(fig)
print("ok")
