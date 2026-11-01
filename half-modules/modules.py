"""
Modular 1U 19" rack mount: two half-width modules that bolt together.

  UCG module  (left):  UniFi UCG-Ultra (set back), 5 keystones (1-4 + WAN) in front of it,
                       5015 blower fan blowing under the gateway, display opening, diamond mesh.
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
GYF      = T + 66.0                           # gateway front face: set back so the keystones
                                              # and their patch-cable plugs fit in front of it
RISE     = 5.0
GZ       = FLOOR + RISE

KS_N, KS_PITCH, KS_X0 = 5, 20.0, 34.0         # 5 keystones (user supplied)
KS_W, KS_H, KS_WALL, KS_POCKET = 14.9, 16.3, 2.0, (19.0, 27.0)
KS_LABELS = ["1", "2", "3", "4", "WAN"]

FAN, FAN_H = 51.5, 15.0                       # 5015 blower, lying flat in front of the gateway,
FX0, FY0   = 176.0, 8.0                       # outlet facing back into the channel under it

DISP_Z   = GZ + GW_H/2 + 0.5                  # display opening (gateway is set back behind it)
DISP_W, DISP_H = 34, 14
MESH_X0, MESH_X1 = 178.0, 229.0               # diamond mesh in front of the fan
MESH_H, MESH_Z = 34, 21.0
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
 "1": [[(0.3,0),(0.3,1),(0.1,0.8)]],
 "2": [[(0,0.8),(0.15,1),(0.45,1),(0.6,0.8),(0.6,0.62),(0,0),(0.6,0)]],
 "3": [[(0,0.88),(0.15,1),(0.45,1),(0.6,0.86),(0.6,0.66),(0.45,0.53),(0.2,0.53)],
       [(0.45,0.53),(0.6,0.4),(0.6,0.14),(0.45,0),(0.15,0),(0,0.12)]],
 "4": [[(0.45,0),(0.45,1),(0,0.35),(0.6,0.35)]],
 "A": [[(0,0),(0.3,1),(0.6,0)], [(0.12,0.4),(0.48,0.4)]],
 "N": [[(0,0),(0,1),(0.6,0),(0.6,1)]],
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
gy0 = GYF - CLR                                   # pocket front
gy1 = GYF + GW_D + CLR                            # pocket rear (gateway rear face)
YEND = gy1 + 8                                    # end of the floor
body += box(INNER_X0+2, tx1, T-0.01, YEND, 0, FLOOR)          # one floor for the whole module
for x0 in (tx0, tx1-3):                                       # side rails start at the gateway
    body += box(x0, x0+3, gy0-6, YEND, 0, GZ+10)
for sx, fdx in ((-1, -50), (1, 12)):                           # (right stop kept clear of the fan bay)
    x0, x1 = GX+fdx-3, GX+fdx+3
    # front stops: contact face toward the gateway, 45 deg ramp on the front side
    body += Manifold.batch_hull([box(x0, x1, gy0-4-(GZ+5-FLOOR), gy0, FLOOR-0.01, FLOOR),
                                 box(x0, x1, gy0-4, gy0, FLOOR-0.01, GZ+5)])
    x0, x1 = GX+sx*62-3, GX+sx*62+3                            # rear stops (low, clear of plugs)
    body += Manifold.batch_hull([box(x0, x1, gy1-RISE, gy1+4, FLOOR-0.01, FLOOR),
                                 box(x0, x1, gy1, gy1+4, GZ, GZ+5)])
for dx in (-60, -30, 0, 30, 60):                               # ribs run front-to-back: fan air
    body += box(GX+dx-1, GX+dx+1, gy0, gy1, FLOOR-0.01, GZ)    # flows under the gateway and out the back
for sx in (-1, 1):                                             # strap slots
    x = GX + sx*(pw/2 + 7)
    sy = (gy0 + gy1) / 2
    body += box(x-5, x+5, sy-15, sy+15, 0, FLOOR)
    body -= box(x-1.75, x+1.75, sy-12, sy+12, -1, FLOOR+1)
body -= box(INNER_X0, tx1, T, T+3.01, PANEL_H-5.01, PANEL_H+1)  # no top rib: room to drop things in

# keystones + labels
kz = PANEL_H/2
for i, t in enumerate(KS_LABELS):
    x = KS_X0 + i*KS_PITCH
    body -= box(x-KS_W/2, x+KS_W/2, -1, T+5, kz-KS_H/2, kz+KS_H/2)
    body -= box(x-KS_POCKET[0]/2, x+KS_POCKET[0]/2, KS_WALL, T+5, kz-KS_POCKET[1]/2, kz+KS_POCKET[1]/2)
    body -= label(t, x, kz - KS_H/2 - 2.0 - LBL_H)
# patch-cable tie anchors along the left side of the gateway (cables run front-to-back here)
for y in (gy0 + 25, gy0 + 65, gy0 + 105):
    for x in (36, 64):
        body -= box(x-1.1, x+1.1, y-2.75, y+2.75, -1, FLOOR+1)

# fan bay (in front of the gateway's right half)
fx1, fy0 = FX0 + FAN, T + FY0
fy1 = fy0 + FAN
for x0 in (FX0-3, fx1):                                        # side walls, grown from the panel
    body += box(x0, x0+3, T-0.01, fy1, 0, FLOOR+FAN_H+2)
for x0 in (FX0, fx1-6):                                        # front stops
    body += box(x0, x0+6, T-0.01, fy0, 0, FLOOR+6)
FCX, FCY = FX0 + FAN/2, fy0 + FAN/2
body -= Manifold.batch_hull([cyl_z(FCX, FCY, 17, -1, FLOOR+1),           # intake, teardrop
                             cyl_z(FCX, FCY+17*2**0.5-0.5, 0.5, -1, FLOOR+1)])
body -= box(FCX-8, FCX+8, T+0.8, T+3.3, -1, FLOOR+1)                     # zip-tie slots
body -= box(FCX-8, FCX+8, fy1+0.6, fy1+2.6, -1, FLOOR+1)

# display opening + diamond mesh in front of the fan
body -= slot_y(GX, DISP_Z, DISP_W, DISP_H, -1, T+1)
a = DIA / 2**0.5
cell = Manifold.cube([a, T+2, a], center=True).rotate([0, 45, 0])
pitch = DIA + RIB * 2**0.5
mcx, mw = (MESH_X0+MESH_X1)/2, MESH_X1-MESH_X0
dias = []
for jj in range(-12, 13):
    for ii in range(-20, 21):
        x = mcx + ii*pitch + (pitch/2 if jj % 2 else 0)
        z = MESH_Z + jj*pitch/2
        if abs(x-mcx) <= mw/2-1.0-DIA/2 and abs(z-MESH_Z) <= MESH_H/2-1.0-DIA/2:
            dias.append(cell.translate([x, T/2, z]))
body -= Manifold.batch_boolean(dias, OpType.Add)
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
