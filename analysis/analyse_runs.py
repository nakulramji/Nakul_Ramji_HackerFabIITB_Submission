"""
Analysis for the physical test campaign (docs/test_plan.md).
  uniformity : python analyse_runs.py uniformity map.csv --set 150
      map.csv columns: x_mm,y_mm,T_C   (>= 9 points; already corrected for the isothermal inter-calibration offsets)
  repeat     : python analyse_runs.py repeat runs.csv --set 150
      runs.csv columns: run,T_C   (one steady-state mean wafer temperature per run, >= 10 runs)
  accuracy   : python analyse_runs.py accuracy cal.csv
      cal.csv columns: setpoint_C,T_true_C   -> set-vs-actual error and the offset table to load into the controller
Verdicts use the exact criteria from the task: <5 C set-vs-actual, <0.5 C run-to-run, +-0.5 C uniformity (span <= 1.0 C).
"""
import argparse, csv, math, statistics as st

def load(path):
    with open(path) as f: return list(csv.DictReader(f))

def uniformity(rows, Tset):
    T=[float(r["T_C"]) for r in rows]
    pts=[(float(r["x_mm"]),float(r["y_mm"]),float(r["T_C"])) for r in rows]
    mid=(max(T)+min(T))/2; span=max(T)-min(T)
    print(f"points={len(T)}  mean={st.mean(T):.2f}  min={min(T):.2f}  max={max(T):.2f}  span={span:.2f} C  (+-{span/2:.2f} about midrange)")
    worst=max(pts,key=lambda p:p[2]); cold=min(pts,key=lambda p:p[2])
    print(f"hottest at ({worst[0]:.0f},{worst[1]:.0f}) mm, coldest at ({cold[0]:.0f},{cold[1]:.0f}) mm")
    print("PASS" if span<=1.0 else "FAIL", "- spec: span <= 1.0 C over the 100 mm wafer")

def repeat(rows, Tset):
    T=[float(r["T_C"]) for r in rows]
    sp=max(T)-min(T); sd=st.pstdev(T) if len(T)>1 else float('nan')
    print(f"runs={len(T)} mean={st.mean(T):.3f} sd={sd:.3f} max-min={sp:.3f} C")
    print("PASS" if sp<0.5 else "FAIL", "- spec: run-to-run difference < 0.5 C (here: max-min over all runs)")

def accuracy(rows):
    errs=[]
    print("setpoint  actual   error")
    for r in rows:
        s=float(r["setpoint_C"]); a=float(r["T_true_C"]); errs.append(a-s)
        print(f"{s:8.1f} {a:8.2f} {a-s:+7.2f}")
    print("PASS" if max(abs(e) for e in errs)<5 else "FAIL", "- spec: |set - actual| < 5 C at every tested setpoint")
    print("offset to enter (O command), per setpoint, = -error")

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("mode",choices=["uniformity","repeat","accuracy"]); ap.add_argument("csv"); ap.add_argument("--set",type=float,default=0)
    a=ap.parse_args(); rows=load(a.csv)
    {"uniformity":lambda:uniformity(rows,a.set),"repeat":lambda:repeat(rows,a.set),"accuracy":lambda:accuracy(rows)}[a.mode]()
