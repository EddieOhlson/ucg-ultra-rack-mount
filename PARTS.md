# Parts and Where to Buy

Amazon links for everything this mount needs. Prices and stock weren't checked; any equivalent part works if it meets the size notes.

## Electronics

| Qty | Part | Size notes | Link |
|---|---|---|---|
| 1 | 5015 USB blower fan, 5 V (recommended) | 50 × 50 × 15 mm | [WINSINN 5015 USB blower, 4-pack](https://www.amazon.com/WINSINN-50x15mm-Bearing-Turbine-Brushless/dp/B087PJ67YC) |
| — | Quieter alternative | Has 3-speed control | [Rpowevax 5015 USB blower, 2-pack](https://www.amazon.com/Rpowevax-Brushless-Cooling-Projects-Portable/dp/B0HB63HL8J) |
| 5 | Slim Cat6 patch cables, 1 ft | 28 AWG slim | [MICRO CONNECTORS slim Cat6 1 ft, 5-pack](https://www.amazon.com/clp/B07H2YSN4K) |
| 5 | Cat6 keystone jacks | Standard keystone | (your own) |
| 1 | USB-A power source for the fan | USB power strip or 5 V charger | Any |
| 1 | 16 mm latching push button with 5 V LED (fan on/off) | 16 mm panel hole, **latching / self-locking**, LED rated 5 V (3–6 V) | [16 mm metal push button, self-locking, blue LED, 5 V, with plug](https://www.amazon.com/Button-Waterproof-Self-Locking-Momentary-self-Reset/dp/B0DK3TM64L) |
| 1 pair | USB-A male + female screw-terminal adapters | Lets you wire the switch in without soldering | [USB-A male & female to 4-pin screw terminal, 1 pair](https://www.amazon.com/Terminal-Solderless-Connector-Converter-Charging/dp/B0DZVVZ2YJ) |

## Hardware

| Qty | Part | Size notes | Link |
|---|---|---|---|
| 8 | M3 heat-set inserts | ~4 mm long, 4.6–5 mm OD (hole is 4.1 mm) | [M3 × 4 × 5 mm brass inserts, 100 pcs](https://www.amazon.com/Threaded-Inserts-Printing-Embedment-Automotive/dp/B0FDKYTMZ8) |
| 8 | M3 × 8 mm countersunk screws | DIN 7991 flat head | [uxcell M3 × 8 countersunk, 100 pcs](https://www.amazon.com/uxcell-Metric-Socket-Countersunk-100PCS/dp/B018RSXQ02) |
| 4 | M6 flat washers | 18 mm OD spreads load on the PETG | [Favordrory M6 × 18 mm stainless, 100 pcs](https://www.amazon.com/Favordrory-Flat-Washer-Stainless-Steel/dp/B07L3SXM6K) |
| 4 | M6 cage nuts and screws | — | Included with the rack |

## Ties and straps (any brand; Harbor Freight is fine)

| Qty | Part | Size notes |
|---|---|---|
| 1 | Zip tie for the fan | 200 mm or longer |
| 7 | Small zip ties for the cable anchors | 4.8 mm wide or narrower |
| 1 | Hook-and-loop strap for the gateway | 20 mm wide or less (VELCRO One-Wrap 1/2" works), ~45 cm long |

## Printing

| Qty | Part | Notes |
|---|---|---|
| ~300 g | PETG filament | One 1 kg spool is plenty |
| 1 | Soldering iron with a heat-set insert tip | Set to ~220–230 °C for PETG |

## Wiring the fan switch

USB power → **male** screw-terminal adapter → switch → **female** screw-terminal adapter → fan.

| From | To |
|---|---|
| Male adapter **VBUS (+5 V, red)** | Switch common terminal |
| Switch normally-open (NO) terminal | Female adapter **VBUS** and LED **+** |
| Male adapter **GND (black)** | Female adapter **GND** and LED **−** |
| D+ / D− | Leave unconnected |

The LED is wired after the switch, so it lights only when the fan is on. When buying, pick the **latching (self-locking)** version with the **5 V** LED. The 12 V and 220 V versions won't light from USB, and the momentary version only runs the fan while you hold the button. Check each listing's options before you buy.

If you use inserts with a different outer diameter, change `INS_R` in `ucg_rack.py` and re-run it to regenerate the splice bracket.
