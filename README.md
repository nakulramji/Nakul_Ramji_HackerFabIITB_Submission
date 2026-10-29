# Semiconductor-grade hot plate (Option B): HackerFab IITB submission

**Nakul Ramji** | IIT Bombay, B.Tech Metallurgical Engineering and Materials Science
Video walkthrough: **(https://youtu.be/2CIGI8Oh1XU)**
Part 1: [`Motivation.pdf`](Motivation.pdf)

> **Status: this is a design, not a built unit.** Everything below is from calculation and simulation. I list what is predicted, what is not modelled, and how I would test each spec (`docs/test_plan.md`).

## 1. The problem in one idea
A hot plate loses heat from its top, bottom and **edge**. At 400 °C the edge loses the most, so the rim runs cold and the centre runs hot. My whole design is about making that edge loss harmless to a 100 mm wafer sitting in the middle.

## 2. Design at a glance
- **Plate:** 6061-T651 aluminium, Ø160 x 30 mm (1.63 kg). Larger than the wafer so the wafer sits away from the cold rim. Aluminium spreads heat sideways quickly (k ≈ 170 W/m·K) and is easy to machine and grind flat.
- **Zone A:** 3 cartridge heaters (150 W each, Ø10 mm) in bores at y = -35, 0, +35 mm, 21 mm below the top face.
- **Zone B:** a 350 W mica band heater on the top 15 mm of the rim. It replaces the heat the edge loses, so the edge stops being cold.
- **Sensors:** 2 PT100s (3 mm below the top face) read through MAX31865 boards; a third bore is spare.
- **Control:** Arduino + two SSRs in burst-fire mode (1 s window, 1 % resolution), PID on the centre sensor, slow trim of the zone split using the rim sensor.
- **Insulation:** 25 mm calcium-silicate board below, wrap on the side, all sealed inside a stainless tray so no fibres reach the cleanroom.
- **Safety:** independent manual-reset thermal cutout (~430 °C) in the contactor coil path, plus a software trip at 415 °C.
- Drawings: `drawings/drawing1_plate.png`, `drawing2_assembly.png`, `drawing3_wiring.png`. BOM: `bom/BOM.csv` (**≈ ₹57,000 estimated**, my own rough estimates and not vendor quotes). Assembly: `docs/assembly.md`.

## 3. How I worked towards each spec

| Spec | Approach | Predicted result | Confidence |
|---|---|---|---|
| 1. 4" wafer | Ø100 mm uniform zone inside a Ø160 mm plate | Zone is well inside the plate | High |
| 2. Room temp to 400 °C | 800 W installed; steady loss at 400 °C is only ≈ 169 W | Open-loop ramp ≈ 2 / 4 / 7.5 / 14 min to 90 / 150 / 250 / 400 °C. **Cooling is passive** (≈ 1.7 h from 400 °C to 100 °C) | Medium |
| 3a. Set vs actual < 5 °C | PT100 + in-situ offset calibration against thermocouples on a real wafer (T2, T3) | Class A PT100 tolerance alone is ±0.95 °C at 400 °C; offsets remove the rest | Medium |
| 3b. Run-to-run < 0.5 °C | **Tool:** tuned PID, burst-fire SSR, 15-bit RTD interface, fixed insulation. **Process:** fixed soak and load procedure, settle criterion, same starting state, logging (T4) | Controller model: spread over 30 randomised runs 0.02 K (90, 150 °C) and 0.06 K (400 °C) | Medium. Model covers the controller only, not sensor drift or wafer seating |
| 4. Uniformity ±0.5 °C | Oversize plate, side-row layout, rim band heater, thicker plate | 3D model, span over the 100 mm zone: **0.015 / 0.03 / 0.05 / 0.13 K** at 90 / 150 / 250 / 400 °C. Cartridges only: 0.12 / 0.24 / 0.45 / 0.83 K. Spec limit is 1.0 K | See "main risk" |
| 5. Flat ±10 µm | Pre-age plate, surface-grind the top face, verify on a surface plate (T1) | Thermal bow ≈ 0.6 µm steady, ≈ 2.4 µm in a fast ramp | Medium. Depends on the shop |

## 4. What the simulations are (and are not)
- `simulation/hotplate_sim.py`: 3D steady-state finite-volume model of the plate with convection, radiation, side and bottom losses. Mesh check at 5, 3.3 and 2.5 mm: span at 400 °C ranges 0.11–0.17 K, at 150 °C 0.03–0.05 K (`simulation/mesh_check.json`).
- Robustness checks (`simulation/robustness.json`, run with a full-height band model): rim share ±0.1 off optimum, one cartridge 10 % weak, extra airflow, polished vs oxidised top, weak bottom insulation. All stay below 0.5 K span in the model. Removing side insulation entirely raises 400 °C span to 0.47 K.
- `control/control_sim.py`: closed-loop run on a two-node lumped model with sensor noise 0.03 K (my assumption), randomised ambient (21 ± 1.5 °C), mains (±8 %) and start state. Settling to ±0.2 K takes 2.5 min at 90 °C and ≈ 34 min at 400 °C; overshoot < 0.2 K; ripple ≈ 0.1 K.
- **Not modelled:** the wafer and the air gap under it, contact resistance of the cartridges in their bores, the real rim band shape and its lead gap, temperature-dependent conductivity, real sensor noise and drift. Heat-transfer coefficients are textbook values I assumed, not measurements.

## 5. Main risk: the wafer-to-plate gap at high temperature
My plate model predicts the *plate* top surface. What the spec measures is the *wafer*. At 400 °C about 10 kW/m² flows up through the wafer, so each 10 µm of air gap under the wafer costs roughly **1.9 K** (order-of-magnitude estimate in `simulation/transient_estimates.py`). At 150 °C it is about 0.5 K per 10 µm. So:
- A top face that is flat to the full ±10 µm could by itself break the ±0.5 °C uniformity at 400 °C if the wafer rocks on a high spot.
- Therefore I ask the machinist for ±5 µm, I measure the surface (T1), and I test uniformity with a real wafer (T5).
- If this is not enough at 400 °C, my fallback is a thin, flat sacrificial Al or Si carrier or a vacuum chuck. I would rather report that honestly than claim 400 °C works.
- For typical lithography bakes (90–150 °C) the effect is below 0.5 K per 10 µm, and the design has a comfortable margin.

## 6. Other challenges and trade-offs
- **Aluminium at 400 °C:** 6061-T6 loses strength and relaxes stress above about 200 °C, so a flat plate can warp over cycles. Hence the 3 pre-ageing cycles before the final grind, and no bolted constraint on the plate. An alternative is a stainless or copper plate, but copper is heavy and contaminates silicon, and stainless spreads heat poorly.
- **Cleanroom compatibility:** no exposed fibres, no paint, no anodised top face; thermal paste lives in blind bores. The first bake-out must be done outside the cleanroom.
- **Band heater geometry:** the cartridges enter from the -x side, so the band covers only the top 15 mm to stay clear of the bore entries. I re-ran the model for that case (span at 400 °C 0.13 K vs 0.11 K for a full-height band; `simulation/partial_band.json`).
- **Sensor placement:** the sensor bores must avoid the cartridge bores (an early sketch had a collision; fixed in the final drawing).
- **Cooling:** natural cooling is slow. A fan-assisted underside or a metal heat sink block could be added without changing the top surface.
- **Cost:** the Indian-made target is below ₹1 lakh. My estimate for the core build is ≈ ₹57,000 plus ≈ ₹17,000 for the validation kit (which could be borrowed).

## 7. Repository map
```
Motivation.pdf            Part 1
README.md                 this file
bom/                      BOM.csv, validation_kit.csv (estimated prices)
drawings/                 plate drawing, assembly section, wiring (PNG + script)
docs/                     assembly.md, safety.md, test_plan.md, video_script.md
simulation/               3D thermal model + all sweeps and result JSONs
control/                  closed-loop and repeatability simulations
firmware/                 Arduino controller
analysis/                 script for the test data (demo CSVs are FAKE, labelled)
figures/                  plots used in this README
```
Figures: `figures/fig1_uniformity_map_400C.png`, `fig2_span_vs_setpoint.png`, `fig3_cross_section_400C.png`, `fig4_control_runs.png`.


