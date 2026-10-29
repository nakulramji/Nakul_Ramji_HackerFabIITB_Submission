# Video script (target 7–8 min; hard limit 10)

**0:00–0:45 Problem.** Imported hot plates cost over ₹1 lakh. Specs: 4", RT–400 °C, <5 °C error, <0.5 °C repeatability, ±0.5 °C uniformity, ±10 µm flat. Show the table in README section 3.

**0:45–2:15 Core idea.** Show fig1 (left vs right). Plate loses heat at the edge → cold rim. Two fixes: oversize plate + a rim band heater. Say what each does, and why aluminium.

**2:15–3:30 The design.** Walk through drawing1 (top view + section) and drawing2 (assembly). Mention where each heater and sensor is and why the sensor bores avoid the cartridge bores.

**3:30–4:45 Simulation.** Show fig2 (span vs setpoint). Say what is modelled and what is not. One sentence on the mesh check.

**4:45–6:00 Repeatability: tool + process.** Show fig4. Tool: PID, burst-fire SSR, RTD interface, fixed insulation. Process: fixed soak/load procedure, settle criterion, same start state. Say the model covers only the controller.

**6:00–7:15 Honest risks.** The wafer gap (1.9 K per 10 µm at 400 °C), aluminium warping (pre-ageing), cooling time.

**7:15–8:00 Next steps.** Build order, test plan T1–T6, what I would learn at HackerFab. Close.

Tips: share your screen on the README, read numbers from the table, and be ready to say "I have not tested this yet".
