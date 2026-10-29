# Assembly instructions

Order matters: the plate is pre-aged and flat-ground **before** anything is installed in it.

## 0. Before you start
- Read `safety.md`. Work with the unit unplugged. Heaters are 230 V.
- Check every received part against `../bom/BOM.csv`.

## 1. Plate preparation
1. Rough-turn the Ø165 x 35 blank to Ø161 x 31, leaving grinding allowance.
2. Drill and bore: 3 cartridge bores Ø10 H7 (y = -35, 0, +35 mm; centre 9 mm above the bottom face; depths 127 / 145 / 127 mm, entering from the -x side), 2 sensor bores Ø3.2 x 27 mm from the bottom face at (0, +17.5) and (58, -17.5) mm, a spare Ø3.2 x 27 at (-60, +25), 3 x M5 x 10 on r = 70 mm at 60°, 180°, 300°.
3. **Pre-age**: heat the bare plate in an oven or on a hot plate to 420 °C and cool back to room temperature, 3 times (slow ramps). This relieves stress so the plate does not warp later.
4. Finish-turn to Ø160 x 30 and **surface-grind the top face**. Ask for a flatness report (target ±5 µm, spec ±10 µm).
5. Press the three Ø3 locating pins into holes on r = 52.5 mm (90°, 210°, 330°), 1.2 mm proud.
6. Clean with IPA. Do not anodise the top face.

## 2. Heaters and sensors
1. Smear a thin film of high-temperature thermal paste on each cartridge heater and push it fully into its bore. Heated section must sit over x = -50…+50 mm (side rows) and x = -60…+60 mm (centre row).
2. Fit the cartridge retaining clips on the cold ends so they cannot slide out.
3. Put a drop of ceramic adhesive on each PT100 tip and push it to the bottom of its Ø3.2 bore (3 mm from the top face). Let it cure per the adhesive datasheet.
4. Wrap the mica band heater around the top 15 mm of the rim, tab at +x (away from the cartridge entries), tighten with the spring tensioner.
5. Mount the manual-reset thermal cutout on the side of the plate, 10 mm from the nearest heater bore.

## 3. Insulation and shell
1. Cut the calcium silicate board to the tray inside diameter, 25 mm thick. Cut the side wrap to fit around the rim and band.
2. Place the 3 alumina standoffs on the board; set the plate on them.
3. Close the stainless tray and lid. All cable exits go through SS glands. No insulation may be visible.

## 4. Controller box
1. Mount the Arduino, the 2 MAX31865 boards, 5 V PSU, 2 SSRs on heat sinks, contactor, MCB/RCD in the earthed metal box.
2. Wire per `../drawings/drawing3_wiring.png`. The contactor coil is wired through: E-stop → thermal cutout → coil. The SSRs are on the contactor's switched side.
3. Connect the PT100s to the MAX31865 boards (3-wire). Earth the plate, the shell and the box.
4. Flash `../firmware/hotplate_controller/hotplate_controller.ino`.

## 5. First power-up (no wafer)
1. Disconnect heaters. Power the electronics only. Check that S1, S2 read room temperature within ±1 °C and that the E-stop trips the contactor.
2. Reconnect heaters. Send `S 60`, `R`. Watch the log. Confirm the temperature rises smoothly, the duty cycles are sensible, and nothing smells burnt.
3. Run the **bake-out**: hold 150 °C for 1 h, then 300 °C for 1 h, then 400 °C for 30 min. This drives off oils from paste and insulation. Do this in a ventilated area, not the cleanroom.
4. Continue with `test_plan.md`.
