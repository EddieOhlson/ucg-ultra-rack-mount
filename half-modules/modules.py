"""
Modular 1U 19" rack mount: two half-width modules that bolt together.

  UCG module  (left):  UniFi UCG-Ultra, 5015 blower fan, lit master power switch,
                       diamond-mesh grille with display opening, 1 uplink keystone.
  USW module  (right): UniFi USW-Ultra PoE switch, ports facing front through a window.

Original design. Units: mm.  X = width, Y = depth (0 = front face, + toward rear), Z = up.
Each module prints face-down, turned 45 deg (fits a 220 x 220 mm bed).
Modules are joined by a splice bracket with 8x M3 heat-set inserts + M3 countersunk screws.
"""
import os
import numpy as np, trimesh
from manifold3d import Manifold, OpType

SEG = 48

# ---------------- rack ----------------
RACK_W   = 482.6
PANEL_H  = 43.6
T        = 4.0
HOLE_PITCH_X = 465.1
HOLE_Z   = (5.95, 37.70)
INNER_X0, INNER_X1 = 20.0, RACK_W - 20.0
SPLIT_X  = RACK_W / 2
FLOOR    = 3.0
FLANGE_D = 30.0

# ---------------- UCG module ----------------
GW_W, GW_D, GW_H = 141.8, 127.6, 30.0        # UCG-Ultra datasheet
CLR      = 0.8
GX       = 155.0
TRAY_D   = GW_D + 2*CLR + 6
RISE     = 5.0
GZ       = FLOOR + RISE

FAN, FAN_H = 51.5, 15.0                       # 5015 blower
FX0      = 26.0
FY0      = 42.0                               # fan sits further back: room for switch + keystone

SW_X, SW_Z, SW_HOLE = 46.0, PANEL_H/2, 16.3   # 16 mm lit latching push button
UP_X     = 68.0                               # uplink keystone
KS_W, KS_H, KS_WALL, KS_POCKET = 14.9, 16.3, 2.0, (20.0, 27.0)

WIN_W, WIN_H, WIN_Z = 136, 34, 21.0
DISP_Z   = GZ + GW_H/2 + 0.5
DISP_W, DISP_H = 34, 14
DIA, RIB = 4.0, 1.0

# ---------------- USW module ----------------
US_L, US_D, US_H = 203.0, 76.0, 33.0          # USW-Ultra datasheet
US_CLR   = 0.6
US_X0    = 252.0                              # left rail outer face (clear of splice bracket)
US_RAIL  = 2.5
US_LIP   = 1.2                                # snap lip over the switch's top edge
US_WIN   = (196.0, 27.0)                      # port window (W x H)

# ---------------- splice ----------------
SPL_HX   = (SPLIT_X-4.5, SPLIT_X+5.0)
SPL_PZ   = (13.0, 31.0)
INS_R    = 2.05

# ---------------- helpers ----------------
def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1-x0, y1-y0, z1-z0]).translate([x0, y0, z0])

def cyl_y(x, z, r, y0, y1, r2=None):
    c = Manifold.cylinder(y1-y0, r, r if r2 is None else r2, SEG)
    return c.rotate([-90, 0, 0]).translate([x, y0, z])

def cyl_z(x, y, r, z0, z1, r2=None):
    return Manifold.cylinder(z1-z0, r, r if r2 is None else r2, SEG).translate([x, y, z0])

def rrect_y(cx, cz, w, h, r, y0, y1):
    return Manifold.batch_hull([cyl_y(cx+sx*(w/2-r), cz+sz*(h/2-r), r, y0, y1)
                                for sx in (-1, 1) for sz in (-1, 1)])

def slot_y(cx, cz, w, h, y0, y1):
    r = h/2
    return Manifold.batch_hull([cyl_y(cx-(w/2-r), cz, r, y0, y1), cyl_y(cx+(w/2-r), cz, r, y0, y1)])

def cs_screw_front(x, z):
    return cyl_y(x, z, 1.7, -1, T+1) + cyl_y(x, z, 3.2, -0.01, 1.7, 1.5)

FONT = {
 "P": [[(0,0),(0,1),(0.45,1),(0.6,0.88),(0.6,0.62),(0.45,0.5),(0,0.5)]],
 "W": [[(0,1),(0.15,0),(0.3,0.6),(0.45,0),(0.6,1)]],
 "R": [[(0,0),(0,1),(0.45,1),(0.6,0.88),(0.6,0.62),(0.45,0.5),(0,0.5)], [(0.3,0.5),(0.6,0)]],
 "U": [[(0,1),(0,0.15),(0.15,0),(0.45,0),(0.6,0.15),(0.6,1)]],
}
LBL_H, STROKE, ENGR = 5.5, 1.0, 1.0
def label(text, cx, z0):
    adv = 0.85 * LBL_H
    x0 = cx - ((len(text)-1)*adv + 0.6*LBL_H)/2
    out = Manifold()
    for k, ch in enumerate(text):
        for line in FONT[ch]:
            for (u0, v0), (u1, v1) in zip(line, line[1:]):
                out += Manifold.batch_hull([cyl_y(x0+k*adv+u*LBL_H, z0+v*LBL_H, STROKE/2, -1, ENGR)
                                            for u, v in ((u0, v0), (u1, v1))])
    return out

# ================= common frame =================
body = box(0, RACK_W, 0, T, 0, PANEL_H)
body += box(INNER_X0, INNER_X1, T-0.01, T+FLANGE_D, 0, FLOOR)
body += box(INNER_X0, INNER_X1, T-0.01, T+3, PANEL_H-5, PANEL_H)          # top rib
for x in ((RACK_W-HOLE_PITCH_X)/2, RACK_W-(RACK_W-HOLE_PITCH_X)/2):
    for z in HOLE_Z:
        body -= slot_y(x, z, 10.0, 6.6, -1, T+1)

# ================= UCG module =================
pw = GW_W + 2*CLR
tx0, tx1 = GX - pw/2 - 3, GX + pw/2 + 3
body += box(tx0, tx1, T-0.01, T+TRAY_D, 0, FLOOR)
for x0 in (tx0, tx1-3):
    body += box(x0, x0+3, T-0.01, T+TRAY_D, 0, GZ+10)
ry0 = T + GW_D + 2*CLR
for sx in (-1, 1):
    x0, x1 = GX+sx*62-3, GX+sx*62+3
    body += Manifold.batch_hull([box(x0, x1, ry0-RISE, ry0+4, FLOOR-0.01, FLOOR),
                                 box(x0, x1, ry0, ry0+4, GZ, GZ+5)])
body -= box(tx0, tx1, T, T+3.01, PANEL_H-5.01, PANEL_H+1)
for yo in (12, 37, 67, 97, 117):                       # air-channel ribs (45 deg underside)
    y0 = T + yo
    body += Manifold.batch_hull([box(tx0+2, tx1-2, y0, y0+0.01, FLOOR-0.01, FLOOR),
                                 box(tx0+2, tx1-2, y0+RISE, y0+RISE+2, FLOOR-0.01, GZ)])
for ya, yb in ((18, 35), (43, 65), (73, 95), (103, 115)):
    body -= box(tx1-4, tx1+1, T+ya, T+yb, FLOOR, GZ+2)  # exhaust slots, right rail
sy = T + GW_D/2                                         # strap slots
for sx in (-1, 1):
    x = GX + sx*(pw/2 + 7)
    body += box(x-5, x+5, sy-15, sy+15, 0, FLOOR)
    body -= box(x-1.75, x+1.75, sy-12, sy+12, -1, FLOOR+1)

# fan bay
fx1, fy0 = FX0 + FAN, T + FY0
fy1 = fy0 + FAN
body += box(INNER_X0+2, tx0+0.01, T-0.01, fy1+FAN_H+9, 0, FLOOR)
body += box(FX0-3, FX0, T-0.01, fy1+3, 0, FLOOR+FAN_H+2)
body += Manifold.batch_hull([box(FX0-3, tx0+0.01, fy1, fy1+3, 0, FLOOR+3),
                             box(FX0-3, tx0+0.01, fy1+FAN_H-1, fy1+FAN_H+2, 0, FLOOR+FAN_H+2)])
for x0 in (FX0, fx1-5):
    body += box(x0, x0+5, fy0-10, fy0, 0, FLOOR+6)      # front stops
    body += Manifold.batch_hull([box(x0, x0+5, fy0-10-6, fy0-10, 0, FLOOR),   # 45 deg lead-in
                                 box(x0, x0+5, fy0-10, fy0-9.99, 0, FLOOR+6)])
FCX, FCY = FX0 + FAN/2, fy0 + FAN/2
body -= Manifold.batch_hull([cyl_z(FCX, FCY, 17, -1, FLOOR+1),
                             cyl_z(FCX, FCY+17*2**0.5-0.5, 0.5, -1, FLOOR+1)])
body -= box(FCX-8, FCX+8, fy0-4, fy0-1.5, -1, FLOOR+1)                 # zip-tie slots
body -= box(FCX-8, FCX+8, fy1+FAN_H+3.5, fy1+FAN_H+6.0, -1, FLOOR+1)
body -= box(FX0+4, FX0+12, fy1-1, fy1+FAN_H+4, FLOOR+3, FLOOR+FAN_H+3)  # cable notch
body -= box(tx0-1, tx0+4, fy0+4, fy1-4, FLOOR, GZ)                      # outlet into channel

# diamond mesh grille + display opening
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
        if abs(x-GX) <= WIN_W/2-1.0-DIA/2 and abs(z-WIN_Z) <= WIN_H/2-1.0-DIA/2:
            c = cell.translate([x, T/2, z])
            if (c ^ frame).volume() < 1e-6:
                dias.append(c)
body -= Manifold.batch_boolean(dias, OpType.Add)
body -= slot_y(GX, DISP_Z, DISP_W, DISP_H, -1, T+1)

# master power switch + uplink keystone
body -= cyl_y(SW_X, SW_Z, SW_HOLE/2, -1, T+1)
body -= label("PWR", SW_X, SW_Z + 11.5)
kz = PANEL_H/2
body -= box(UP_X-KS_W/2, UP_X+KS_W/2, -1, T+5, kz-KS_H/2, kz+KS_H/2)
body -= box(UP_X-KS_POCKET[0]/2, UP_X+KS_POCKET[0]/2, KS_WALL, T+5, kz-KS_POCKET[1]/2, kz+KS_POCKET[1]/2)
body -= label("UP", UP_X, kz - KS_H/2 - 2.0 - LBL_H)

# ================= USW module =================
ux0 = US_X0 + US_RAIL                     # pocket inner faces
ux1 = ux0 + US_L + 2*US_CLR
UX  = (ux0 + ux1) / 2
uy1 = T + US_CLR + US_D                   # switch rear face
assert ux1 + US_RAIL <= RACK_W - 16.3, "USW tray hits the rack rail"
body += box(US_X0, ux1+US_RAIL, T-0.01, uy1+8, 0, FLOOR)                  # tray floor
ZL = FLOOR + US_H + 0.3                                                   # lip underside
for x0, d in ((US_X0, +1), (ux1, -1)):                                     # snap rails
    body += box(x0, x0+US_RAIL, T-0.01, uy1+8, 0, ZL+2.4)
    xi = x0 + US_RAIL if d > 0 else x0                                     # rail inner face
    # lip: flat underside holds the switch, sloped top lets it snap down past
    body += Manifold.batch_hull([box(min(xi, xi+d*US_LIP), max(xi, xi+d*US_LIP), T+10, uy1-10, ZL, ZL+0.01),
                                 box(min(xi, xi+d*0.01), max(xi, xi+d*0.01), T+10, uy1-10, ZL, ZL+2.4)])
body -= box(US_X0, ux1+US_RAIL, T, T+3.01, PANEL_H-5.01, PANEL_H+1)     # no rib over the switch
for sx in (-1, 1):                                                         # low rear stops
    x = UX + sx*70
    body += box(x-3, x+3, uy1, uy1+4, 0, FLOOR+5)
for i in range(5):                                                         # floor vents
    y = T + 15 + i*12
    body -= Manifold.batch_hull([cyl_z(UX-80, y, 1.75, -1, FLOOR+1), cyl_z(UX+80, y, 1.75, -1, FLOOR+1)])
body -= rrect_y(UX, FLOOR + US_H/2, US_WIN[0], US_WIN[1], 4, -1, T+1)     # port window

# ================= splice holes =================
for x in SPL_HX:
    for z in SPL_PZ:
        body -= cs_screw_front(x, z)
    body -= cyl_z(x, T+20, 1.7, -1, FLOOR+1)
    body -= cyl_z(x, T+20, 3.2, -0.01, 1.7, 1.5)

ucg = body ^ box(-1, SPLIT_X, -5, 300, -5, 100)
usw = body ^ box(SPLIT_X, RACK_W+1, -5, 300, -5, 100)

bx0, bx1 = tx1 + 0.6, US_X0 - 0.6
br  = box(bx0, bx1, T, T+5, FLOOR, PANEL_H-5.2)
br += box(bx0, bx1, T, T+FLANGE_D-1, FLOOR, FLOOR+5)
br += Manifold.batch_hull([box(bx0, bx1, T, T+5, FLOOR, FLOOR+14), box(bx0, bx1, T, T+16, FLOOR, FLOOR+5)])
for x in SPL_HX:
    for z in SPL_PZ:
        br -= cyl_y(x, z, INS_R, T-1, T+6)
    br -= cyl_z(x, T+20, INS_R, FLOOR-1, FLOOR+6)

# ================= export =================
def to_trimesh(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(mm.vert_properties[:, :3], mm.tri_verts, process=True)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(out, exist_ok=True)
trimesh.util.concatenate([to_trimesh(ucg), to_trimesh(usw), to_trimesh(br)]).export(f"{out}/assembly_preview.stl")
for name, m in {"UCG_module.stl": ucg, "USW_module.stl": usw, "SPLICE.stl": br}.items():
    t = to_trimesh(m)
    t.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    if "SPLICE" not in name:
        t.apply_transform(trimesh.transformations.rotation_matrix(np.pi/4, [0, 0, 1]))
    t.apply_translation(-t.bounds[0])
    t.export(f"{out}/{name}")
    print(f"{name:16s} watertight={t.is_watertight}  print footprint={np.round(t.extents, 1)}")
