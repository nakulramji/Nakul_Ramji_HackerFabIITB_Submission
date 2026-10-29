# Test plan (how each spec will be demonstrated)

The simulations in `../simulation` and `../control` are predictions. These tests decide whether the build meets the spec.

## T1. Flatness (spec 5, ±10 µm)
- Place the plate on a granite surface plate at room temperature. Use a dial indicator or comparator (1 µm resolution) on a 10 mm grid across the Ø100 zone. Record the heights as `x,y,z`.
- Repeat the measurement hot if possible (e.g. 150 °C) by indicating through a window, or accept the calculation: bow in steady state is below 1 µm (estimate in `../simulation/transient_estimates.json`).
- Pass: all points within ±10 µm.

## T2. Sensor inter-calibration (needed before T3–T5)
- Put all thermocouples (and PT100s) in an isothermal block/oil bath or hold them in a stack of aluminium at each setpoint (90, 150, 250, 400 °C) next to a reference thermometer.
- Record each sensor's offset from the reference at each setpoint. These offsets are subtracted from later readings. This is how a relative uniformity of ±0.5 °C can be measured with ordinary thermocouples.

## T3. Set-vs-actual error (spec 3a, < 5 °C)
- Place the 9-thermocouple wafer on the plate. For setpoints 50, 90, 150, 250, 400 °C: wait for the settle criterion (|dT/dt| < 0.05 K/min for 5 min), record the wafer mean.
- `python3 ../analysis/analyse_runs.py accuracy cal.csv` gives the error and the offset to enter with the `O` command.
- Pass: |error| < 5 °C after the offsets are loaded.

## T4. Run-to-run repeatability (spec 3b, < 0.5 °C)
- Procedure (fixed, written on the unit): start from a plate at ambient, send `S <T>` + `R`, wait 45 min at 90–150 °C (60 min at 400 °C), load the wafer, wait 5 min, then record 2 min of data. Cool, repeat. 10 runs per setpoint, on different days if possible.
- `python3 ../analysis/analyse_runs.py repeat runs.csv`
- Pass: max-min over the 10 runs < 0.5 °C.
- Also run 5 "warm start" runs (restarted at 60 °C) to check the procedure is not sensitive to starting state.

## T5. Uniformity (spec 4, ±0.5 °C)
- 9 points: centre, 4 at r = 30 mm, 4 at r = 45 mm on a wafer with thin thermocouples glued with high-temperature adhesive tape.
- Run at 90, 150, 250, 400 °C after settling. `python3 ../analysis/analyse_runs.py uniformity map.csv --set 150`
- Pass: max-min ≤ 1.0 °C.
- If it fails only at 400 °C, vary the rim fraction (command `O`/firmware constant) and check the wafer-gap effect (see README, "main risk").

## T6. Safety checks
- E-stop opens the contactor. Disconnect S1 while running: system must go to FAULT within ~2 s. Verify the thermal cutout trip temperature on the bench with a separate thermometer before first run at 400 °C.
