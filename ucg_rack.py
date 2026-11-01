"""
UCG-Ultra 1U 19" rack mount with 5 keystone pass-through ports.
Original design. Units: mm.  X = width, Y = depth (0 = front face, + toward rear), Z = up.

Prints in two halves (each fits a 256 mm bed) joined by a splice bracket
with 8x M3 heat-set inserts + M3 countersunk screws.
"""
import numpy as np, trimesh
from manifold3d import Manifold, CrossSection, OpType

SEG = 48

# ---------------- parameters ----------------
RACK_W   = 482.6          # 19" panel width
PANEL_H  = 43.6           # 1U (44.45) minus clearance
T        = 4.0            # front panel thickness
HOLE_PITCH_X = 465.1      # EIA ear hole spacing
HOLE_Z   = (5.95, 37.70)  # EIA holes relative to panel bottom (0.4 offset)
INNER_X0, INNER_X1 = 20.0, RACK_W - 20.0   # stay clear of rack rails

# UCG-Ultra: 141.8 W x 127.6 D x 30 H (datasheet)
GW_W, GW_D, GW_H = 141.8, 127.6, 30.0
CLR      = 0.8            # clearance per side
GX       = 155.0          # gateway centre X (shifted right to make room for the fan)

# 5015 blower fan (50 x 50 x 15, e.g. 5 V USB blower)
FAN = 51.5                # pocket size (square)
FAN_H = 15.0
FX0 = 26.0                # pocket inner X start
FY0 = 6.0                 # pocket inner Y start behind panel
FLOOR    = 3.0
TRAY_D   = GW_D + 2*CLR + 6    # tray depth behind panel
FLANGE_D = 30.0           # stiffening floor flange elsewhere
RISE     = 5.0            # gateway raised on ribs -> air channel underneath
GZ       = FLOOR + RISE   # underside of the gateway

# Keystones (user supplied, standard size)
KS_N, KS_PITCH, KS_CX = 5, 22.0, 344.0
KS_W, KS_H = 14.9, 16.3   # cut-out
KS_WALL  = 2.0            # wall thickness at keystone (clip grip)
KS_POCKET = (20.0, 27.0)  # rear relief pocket W x H

SPLIT_X  = RACK_W / 2

# ---------------- helpers ----------------
def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1-x0, y1-y0, z1-z0]).translate([x0, y0, z0])

def cyl_y(x, z, r, y0, y1, r2=None):
    """cylinder along +Y from y0 to y1"""
    c = Manifold.cylinder(y1-y0, r, r if r2 is None else r2, SEG)
    return c.rotate([-90, 0, 0]).translate([x, y0, z])

def cyl_z(x, y, r, z0, z1, r2=None):
    return Manifold.cylinder(z1-z0, r, r if r2 is None else r2, SEG).translate([x, y, z0])

def rrect_y(cx, cz, w, h, r, y0, y1):
    """rounded rectangle prism along Y"""
    pts = [cyl_y(cx+sx*(w/2-r), cz+sz*(h/2-r), r, y0, y1) for sx in (-1,1) for sz in (-1,1)]
    return Manifold.batch_hull(pts)

def slot_y(cx, cz, w, h, y0, y1):
    r = h/2
    return Manifold.batch_hull([cyl_y(cx-(w/2-r), cz, r, y0, y1), cyl_y(cx+(w/2-r), cz, r, y0, y1)])

def _gusset_explicit(x, depth, height, th):
    pts = []
    for xx in (x - th/2, x + th/2):
        pts += [cyl_y(xx, FLOOR, 0.01, T, T+0.02),
                cyl_y(xx, FLOOR, 0.01, T+depth, T+depth+0.02),
                cyl_y(xx, FLOOR+height, 0.01, T, T+0.02)]
    return Manifold.batch_hull(pts)

def cs_screw_front(x, z):
    """M3 countersunk clearance through the panel, head at the front face"""
    return cyl_y(x, z, 1.7, -1, T+1) + cyl_y(x, z, 3.2, -0.01, 1.7, 1.5)

# ---------------- body ----------------
body = box(0, RACK_W, 0, T, 0, PANEL_H)

# full-width stiffening flange
body += box(INNER_X0, INNER_X1, T-0.01, T+FLANGE_D, 0, FLOOR)

# top rear rib
body += box(INNER_X0, INNER_X1, T-0.01, T+3, PANEL_H-5, PANEL_H)

# gateway tray floor
pw = GW_W + 2*CLR
tx0, tx1 = GX - pw/2 - 3, GX + pw/2 + 3
body += box(tx0, tx1, T-0.01, T+TRAY_D, 0, FLOOR)
# side rails
for x0 in (tx0, tx1-3):
    body += box(x0, x0+3, T-0.01, T+TRAY_D, 0, GZ+10)
# rear stops (posts clear of the rear ports)
ry0 = T + GW_D + 2*CLR
for sx in (-1, 1):
    x0, x1 = GX+sx*62-3, GX+sx*62+3     # low: clears USB-C / RJ45 plugs
    # 45 deg ramp below the gateway so the stop prints face-down without support
    body += Manifold.batch_hull([box(x0, x1, ry0-RISE, ry0+4, FLOOR-0.01, FLOOR),
                                 box(x0, x1, ry0, ry0+4, GZ, GZ+5)])
# no top rib above the gateway, so it can drop straight in from above
body -= box(tx0, tx1, T, T+3.01, PANEL_H-5.01, PANEL_H+1)

# gussets
for gx in (272, 410, 458):
    body += _gusset_explicit(gx, 24, 24, 3.0)


# ---------------- fan pocket ----------------
fx1, fy0 = FX0 + FAN, T + FY0
fy1 = fy0 + FAN
body += box(INNER_X0+2, tx0+0.01, T-0.01, fy1+FAN_H+9, 0, FLOOR)        # floor
body += box(FX0-3, FX0, T-0.01, fy1+3, 0, FLOOR+FAN_H+2)               # outer side wall
# rear wall: 3 mm vertical stop, then a 45 deg back-slope so it prints face-down
# without a long PETG bridge (it only needs to locate the fan's lower edge)
body += Manifold.batch_hull([box(FX0-3, tx0+0.01, fy1, fy1+3, 0, FLOOR+3),
                             box(FX0-3, tx0+0.01, fy1+FAN_H-1, fy1+FAN_H+2, 0, FLOOR+FAN_H+2)])
for x0 in (FX0, fx1-5):                                                  # front stops
    body += box(x0, x0+5, T-0.01, fy0, 0, FLOOR+6)
FCX, FCY = FX0 + FAN/2, fy0 + FAN/2
body -= Manifold.batch_hull([cyl_z(FCX, FCY, 17, -1, FLOOR+1),           # intake hole, teardrop
                             cyl_z(FCX, FCY+17*2**0.5-0.5, 0.5, -1, FLOOR+1)])  # (prints face-down)
body -= box(FCX-8, FCX+8, T+1.2, T+4.2, -1, FLOOR+1)                     # zip-tie slots
body -= box(FCX-8, FCX+8, fy1+FAN_H+3.5, fy1+FAN_H+6.0, -1, FLOOR+1)  # behind the sloped wall
body -= box(FX0+4, FX0+12, fy1-1, fy1+FAN_H+4, FLOOR+3, FLOOR+FAN_H+3)        # cable notch
# outlet through the gateway's left rail
body -= box(tx0-1, tx0+4, fy0+4, fy1-4, FLOOR, GZ)   # only into the channel: air is forced under the gateway
# front-panel intake grille in front of the fan
for i in range(7):
    x = FX0 + 6 + i*6.5
    body -= Manifold.batch_hull([cyl_y(x, 9, 1.6, -1, T+1), cyl_y(x, PANEL_H-9, 1.6, -1, T+1)])

# ---------------- cuts ----------------
# ear slots
for x in ((RACK_W-HOLE_PITCH_X)/2, RACK_W-(RACK_W-HOLE_PITCH_X)/2):
    for z in HOLE_Z:
        body -= slot_y(x, z, 10.0, 6.6, -1, T+1)

# gateway front window (front face/LCD visible)
WIN_W, WIN_H, WIN_Z = 136, 34, 21.0   # grille spans almost full panel height
DISP_Z = GZ + GW_H/2 + 0.5        # display centre on the gateway face
DISP_W, DISP_H = 34, 14          # display opening (pill), centred on the gateway face
DIA, RIB = 4.0, 1.0              # diamond diagonal and rib width
win = rrect_y(GX, WIN_Z, WIN_W, WIN_H, 4, -1, T+1)
a = DIA / 2**0.5
cell = Manifold.cube([a, T+2, a], center=True).rotate([0, 45, 0])
pitch = DIA + RIB * 2**0.5
frame = slot_y(GX, DISP_Z, DISP_W+2*RIB, DISP_H+2*RIB, -2, T+2)
dias = []
nx, nz = int(WIN_W/pitch)+3, int(WIN_H/(pitch/2))+3
for j in range(-nz, nz+1):
    for i in range(-nx, nx+1):
        x = GX + i*pitch + (pitch/2 if j % 2 else 0)
        z = WIN_Z + j*pitch/2
        c = cell.translate([x, T/2, z])
        # keep only whole diamonds: inside the window (1.4 mm border) and clear of the display frame
        if abs(x-GX) <= WIN_W/2-1.0-DIA/2 and abs(z-WIN_Z) <= WIN_H/2-1.0-DIA/2 \
           and (c ^ frame).volume() < 1e-6:
            dias.append(c)
mesh = Manifold.batch_boolean(dias, OpType.Add)
body -= mesh
body -= slot_y(GX, DISP_Z, DISP_W, DISP_H, -1, T+1)          # display opening

# keystone cut-outs + rear relief pockets
ks_z = PANEL_H/2
for i in range(KS_N):
    x = KS_CX + (i - (KS_N-1)/2) * KS_PITCH
    body -= box(x-KS_W/2, x+KS_W/2, -1, T+5, ks_z-KS_H/2, ks_z+KS_H/2)
    body -= box(x-KS_POCKET[0]/2, x+KS_POCKET[0]/2, KS_WALL, T+5,
                ks_z-KS_POCKET[1]/2, ks_z+KS_POCKET[1]/2)

# support ribs under the gateway (run left-right so fan air flows beneath it).
# lower face is 45 deg so they print without support when printed face-down.
for yo in (12, 37, 67, 97, 117):
    y0 = T + yo
    body += Manifold.batch_hull([box(tx0+2, tx1-2, y0, y0+0.01, FLOOR-0.01, FLOOR),
                                 box(tx0+2, tx1-2, y0+RISE, y0+RISE+2, FLOOR-0.01, GZ)])
# exhaust slots low in the right rail, between the ribs
for ya, yb in ((18, 35), (43, 65), (73, 95), (103, 115)):
    body -= box(tx1-4, tx1+1, T+ya, T+yb, FLOOR, GZ+2)
# hook-and-loop strap slots beside the gateway
sy = T + GW_D/2
for sx in (-1, 1):
    x = GX + sx*(pw/2 + 7)
    body -= box(x-1.75, x+1.75, sy-12, sy+12, -1, FLOOR+1)
# widen floor locally so the strap slots sit inside material
# (tray already spans tx0..tx1; extend ears)
ext = Manifold()
for sx in (-1, 1):
    x = GX + sx*(pw/2 + 7)
    ext += box(x-5, x+5, sy-15, sy+15, 0, FLOOR) - box(x-1.75, x+1.75, sy-12, sy+12, -1, FLOOR+1)
body += ext


# ---------------- patch-cable tie anchors (right half) ----------------
body += box(SPLIT_X+3, 425, T-0.01, T+52, 0, FLOOR)       # deeper flange behind keystones
for x in (252, 284, 316, 348, 380, 412):
    for y in (T+40, T+46):
        body -= box(x-2.75, x+2.75, y-1.1, y+1.1, -1, FLOOR+1)   # pair of slots per tie

# ---------------- port labels (engraved 0.6 mm into front face) ----------------
FONT = {
 "1": [[(0.3,0),(0.3,1),(0.1,0.8)]],
 "2": [[(0,0.8),(0.15,1),(0.45,1),(0.6,0.8),(0.6,0.62),(0,0),(0.6,0)]],
 "3": [[(0,0.88),(0.15,1),(0.45,1),(0.6,0.86),(0.6,0.66),(0.45,0.53),(0.2,0.53)],
       [(0.45,0.53),(0.6,0.4),(0.6,0.14),(0.45,0),(0.15,0),(0,0.12)]],
 "4": [[(0.45,0),(0.45,1),(0,0.35),(0.6,0.35)]],
 "W": [[(0,1),(0.15,0),(0.3,0.6),(0.45,0),(0.6,1)]],
 "A": [[(0,0),(0.3,1),(0.6,0)], [(0.12,0.4),(0.48,0.4)]],
 "N": [[(0,0),(0,1),(0.6,0),(0.6,1)]],
}
LBL_H, STROKE, ENGR = 5.5, 1.0, 1.0   # bold + deep enough to survive first-layer squish
def label(text, cx, z0):
    adv = 0.85 * LBL_H
    w = (len(text)-1)*adv + 0.6*LBL_H
    x0 = cx - w/2
    out = Manifold()
    for k, ch in enumerate(text):
        for line in FONT[ch]:
            for (u0,v0),(u1,v1) in zip(line, line[1:]):
                p = [cyl_y(x0+k*adv+u*LBL_H, z0+v*LBL_H, STROKE/2, -1, ENGR) for u,v in ((u0,v0),(u1,v1))]
                out += Manifold.batch_hull(p)
    return out
KS_LABELS = ["1", "2", "3", "4", "WAN"]
for i, t in enumerate(KS_LABELS):
    x = KS_CX + (i - (KS_N-1)/2) * KS_PITCH
    body -= label(t, x, ks_z - KS_H/2 - 2.0 - LBL_H)

# splice joint screw holes
SPL_HX = (SPLIT_X-4.5, SPLIT_X+15)
SPL_PZ = (13.0, 31.0)
for x in SPL_HX:
    for z in SPL_PZ:
        body -= cs_screw_front(x, z)
    # flange holes, countersunk from underneath
    y = T + 20
    body -= cyl_z(x, y, 1.7, -1, FLOOR+1)
    body -= cyl_z(x, y, 3.2, -0.01, 1.7, 1.5)

# ---------------- split ----------------
left  = body ^ box(-1, SPLIT_X, -5, 300, -5, 100)
right = body ^ box(SPLIT_X, RACK_W+1, -5, 300, -5, 100)

# ---------------- splice bracket ----------------
bx0, bx1 = tx1 + 0.6, 268.8
# vertical plate behind panel (below the top rib), horizontal plate on flange
br  = box(bx0, bx1, T, T+5, FLOOR, PANEL_H-5.2)
br += box(bx0, bx1, T, T+FLANGE_D-1, FLOOR, FLOOR+5)
# corner fillet
br += Manifold.batch_hull([box(bx0, bx1, T, T+5, FLOOR, FLOOR+14),
                           box(bx0, bx1, T, T+16, FLOOR, FLOOR+5)])
INS_R = 2.05   # M3 heat-set insert hole (4.1 mm)
for x in SPL_HX:
    for z in SPL_PZ:
        br -= cyl_y(x, z, INS_R, T-1, T+6)
    br -= cyl_z(x, T+20, INS_R, FLOOR-1, FLOOR+6)
# avoid the gussets near the split
br -= box(269, 275, 0, 60, 0, 60)

# ---------------- export ----------------
def to_trimesh(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(mm.vert_properties[:, :3], mm.tri_verts, process=True)

import os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(out, exist_ok=True)
parts = {"UCG-Ultra_rack_LEFT.stl": left, "UCG-Ultra_rack_RIGHT.stl": right,
         "UCG-Ultra_rack_SPLICE.stl": br}
for name, m in parts.items():
    t = to_trimesh(m)
    # export in print orientation: front face on the bed, turned 45 deg to fit a 220 mm bed
    t.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    if "SPLICE" not in name:
        t.apply_transform(trimesh.transformations.rotation_matrix(np.pi/4, [0, 0, 1]))
    t.apply_translation(-t.bounds[0])
    t.export(f"{out}/{name}")
    print("   print footprint", np.round(t.extents, 1))
    print(name, "watertight", t.is_watertight, "bbox", np.round(t.extents, 1), "vol cm3", round(t.volume/1000, 1))

asm = trimesh.util.concatenate([to_trimesh(left), to_trimesh(right), to_trimesh(br)])
asm.export(f"{out}/assembly_preview.stl")
# gateway ghost for previews
gw = box(GX-GW_W/2, GX+GW_W/2, T+CLR, T+CLR+GW_D, GZ, GZ+GW_H)
to_trimesh(gw).export(f"{out}/gateway_ghost.stl")
