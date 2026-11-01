# Modular Version: UCG-Ultra + USW-Ultra

Two half-width modules that bolt together into one 1U, 19" panel:

- **UCG module (left):** UniFi UCG-Ultra with the diamond-mesh grille and display opening, a 5015 blower fan with an air channel under the gateway, a lit master power switch (PWR), and one uplink keystone (UP)
- **USW module (right):** UniFi USW-Ultra PoE switch, with its 8 ports facing forward through a window in the panel

![Front](docs/front.png)
![Sections](docs/sections.png)

## Files

| File | What it is |
|---|---|
| `stl/UCG_module.stl` | Left module: ear, fan bay, gateway tray, mesh, PWR switch, UP keystone |
| `stl/USW_module.stl` | Right module: ear, USW-Ultra tray with snap rails, port window |
| `stl/SPLICE.stl` | Bracket that joins the two modules |
| `modules.py` | Parametric source; re-run to regenerate the STLs into `out/` |

The STLs are already in print orientation: front face down, turned 45° to fit a 220 mm bed. Each module is 241 mm wide, so it still needs the 45° turn on a 220 mm bed.

## How the two connect

The UCG-Ultra's ports are on its back and the USW-Ultra's ports face the front, so the uplink goes through the **UP** keystone:

1. Run a short patch cable from a UCG-Ultra LAN port (at the back) to the back of the UP keystone.
2. Run a short front jumper from the UP keystone to any USW-Ultra port.

The WAN cable from your modem still plugs into the back of the UCG-Ultra.

## How the USW-Ultra is held

The switch drops into its tray from the top and snaps under small lips on both rails. Low stops at the back keep it from sliding rearward. To remove it, flex one rail outward slightly and lift.

## Power

- **PWR button:** switches the UCG-Ultra and the fan together, wired as in [../PARTS.md](../PARTS.md#wiring-the-master-switch).
- **USW-Ultra:** stays on its own power, either PoE++ into its PoE input port or its separate 54 V adapter. The button doesn't switch it.

## Parts (differences from the full version)

Everything in [../PARTS.md](../PARTS.md) applies, with these changes:

| Change | Part | Notes |
|---|---|---|
| Add | UniFi USW-Ultra | 203 × 76 × 33 mm |
| Add | USW-Ultra power | A PoE++ source or the USW-Ultra's 54 V adapter |
| Add | 1 × Cat6 keystone jack | For the UP keystone |
| Add | 1 × short patch cable at the back, 1 × short jumper at the front | UCG-Ultra → UP keystone → USW-Ultra |
| Remove | The 5 front keystones and their patch cables | The USW-Ultra's own ports face the front instead |
| Remove | The 7 patch-cable zip ties | Only the fan's zip tie is still needed |

Hardware is unchanged: 8 × M3 heat-set inserts, 8 × M3 × 8 countersunk screws, and M6 rack screws with washers.

## Printing and assembly

Print settings are the same as the full version: PETG, 4 walls, brim, textured plate, no supports.

1. Press the 8 heat-set inserts into the splice bracket.
2. Butt the two modules together and screw the bracket behind the seam.
3. Fit the PWR button and the UP keystone.
4. Fit the fan, which now sits further back so the button and keystone have room behind the panel.
5. Drop in the UCG-Ultra and strap it down.
6. Snap the USW-Ultra into its tray, ports facing the window.
7. Wire the uplink, the power button and the switch's power, then rack it.

## Check before printing

- **USW-Ultra port window:** it's sized to the switch's full 203 × 33 mm long face (196 × 27 mm opening), assuming the ports are on that face. Confirm on your unit before printing.
- **Rail clearance:** the USW tray reaches within 4 mm of the rack rail. That fits your CNAweb rack's 450 mm opening, but racks with intrusive rails may need checking.

## Customising

| Parameter | What it controls |
|---|---|
| `US_L`, `US_D`, `US_H`, `US_CLR` | USW-Ultra size and clearance |
| `US_WIN` | Port window size |
| `US_LIP` | How far the snap lips reach over the switch |
| `SW_X`, `UP_X` | PWR button and UP keystone positions |
| `FY0` | How far back the fan sits |

Other parameters work the same as in the full version.
