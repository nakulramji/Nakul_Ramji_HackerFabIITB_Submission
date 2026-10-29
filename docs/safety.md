# Safety design

| Hazard | Layer 1 | Layer 2 |
|---|---|---|
| Runaway heating (SSR welded on) | Manual-reset thermal cutout (≈430 °C) in the contactor coil path: opens the contactor and cuts both heaters | Software trip at 415 °C, SSRs forced off, buzzer |
| Open or shorted sensor | MAX31865 fault flags; rate-of-change check (>6 K/s rejected) → fault state | Hardware cutout still protects |
| Electric shock | Earthed plate, shell and box; RCD 30 mA; MCB 6 A | Heater leads in glands, nothing live outside the box |
| Burns | Warning label "HOT UP TO 400 °C"; top face is the only exposed hot surface | Unit stays hot ~1.7 h after turn-off (simulated cooling); use the log to see temperature |
| Fibre and particle release | Insulation sealed inside the SS shell | Use low-biopersistence wool, wear gloves and mask when cutting |
| Fire | No flammable materials near the plate; do not leave running unattended during first tests | Keep a CO₂ extinguisher near |

**Important:** the software limit is a convenience. The hardware cutout is the safety system, and its trip point must be verified with an independent thermometer before first use at 400 °C. A qualified electrician should inspect the mains wiring before first power-up.
