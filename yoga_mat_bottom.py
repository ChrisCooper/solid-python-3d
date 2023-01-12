from solid import *
from solid.utils import *
from math import cos, radians, sin, pi, tau
import subprocess
import utils

EPS = 0.01

MAT_RADIUS = 165/2.0 # mm
CUP_THICKNESS = 6
CUP_DEPTH = 6
CIRCLE_SEGMENTS = 256
CUP_STRUT_WIDTH = 15
CUTOUT_EDGE = 10 #CUP_THICKNESS * 1.5
N_STRUTS = 5
LIP_BASE_SCALE = 4

MOUNT_WIDTH = 21 * 2 # 21 for large command strip
MOUNT_HEIGHT = 68 # 68 for large command strip

RAMP_UP_MAX_HEIGHT = 70 / CUP_THICKNESS
RAMP_UP_FRACTION = 0.4

# DERIVED
CUP_WALL_CENTER_RADIUS = MAT_RADIUS + CUP_THICKNESS

def cup_bottom(cutout=False):
    full_puck = cylinder(r=MAT_RADIUS + EPS, h=CUP_THICKNESS, segments=CIRCLE_SEGMENTS)
    if not cutout:
        return full_puck

    small_puck = down(0.1)(cylinder(r=MAT_RADIUS - CUTOUT_EDGE, h=CUP_THICKNESS + 0.5, segments=CIRCLE_SEGMENTS))
    edge_ring = full_puck - small_puck

    length = MAT_RADIUS*2 - CUTOUT_EDGE + EPS


    strut = up(CUP_THICKNESS/2)(cube(size = [CUP_STRUT_WIDTH, length, CUP_THICKNESS], center=True))

    bottom = edge_ring
    for i in range(N_STRUTS):
        rotation = i * 180/N_STRUTS
        bottom += rotate([0,0,rotation])(strut)

    return bottom

    #return cylinder(r=MAT_RADIUS, h=CUP_DEPTH + 1, segments=CIRCLE_SEGMENTS)
    #for rotation in 
    #return cutout + rotate([0,0,90])(cutout)
    #180 / n_cutouts


def cup_walls():
    mat_hole = cylinder(r=MAT_RADIUS, h=CUP_DEPTH + CUP_THICKNESS + 0.5, segments=CIRCLE_SEGMENTS)
    cup = cylinder(r=CUP_WALL_CENTER_RADIUS, h=CUP_DEPTH+CUP_THICKNESS, segments=CIRCLE_SEGMENTS)
    return difference()(
        cup,
        down(0.1)(mat_hole),
    )

def wall_mount():
    return left(MOUNT_WIDTH/2)(
            back(CUP_WALL_CENTER_RADIUS)(
                cube([MOUNT_WIDTH, CUP_THICKNESS, MOUNT_HEIGHT])
            )
        )
     


def ring_transform(offset):
    return lambda p, pn, ln: (p.x, p.y + offset, p.z)

def ring():
    cross_section_radius = CUP_THICKNESS/2
    cross_section = utils.circle_points(radius=cross_section_radius)
    path = utils.circle_points(radius=CUP_WALL_CENTER_RADIUS - cross_section_radius, num_points=CIRCLE_SEGMENTS + 1)

    ramp_up_length = int((RAMP_UP_FRACTION * (CIRCLE_SEGMENTS+1)) // 2)
    ramp_ups = [1 + RAMP_UP_MAX_HEIGHT*((i+1.0)/ramp_up_length)**2 for i in range(ramp_up_length)]
    ramp_up_scale = [(1, LIP_BASE_SCALE - 1 + ru) for ru in ramp_ups]
    scales = list(reversed(ramp_up_scale)) + [(1,LIP_BASE_SCALE) for i in range(CIRCLE_SEGMENTS+1 - ramp_up_length*2)] + ramp_up_scale

    #ramp_up_transforms = [ring_transform(ru*1) for ru in ramp_ups]
    #transforms = list(reversed(ramp_up_transforms)) + [ring_transform(0) for i in range(CIRCLE_SEGMENTS+1 - ramp_up_length*2)] + ramp_up_transforms

    return rotate([0,0,-90])(extrude_along_path(cross_section, path, scales=scales))
    #return rotate([0,0,-90])(extrude_along_path(cross_section, path, scales=scales, transforms=transforms))

ring_solid = up(CUP_DEPTH + CUP_THICKNESS)(ring()) - down(49)(cube(size=[300, 300, 100], center=True))
solid = cup_walls() + cup_bottom(cutout=True) + wall_mount() + ring_solid
# solid = cup_shape()

with open('bottom.scad', 'w') as f:
    f.write(scad_render(solid))

subprocess.run(['C:\Program Files\OpenSCAD\openscad.com', '-o', 'bottom.stl', 'bottom.scad'])
# 'C:\Program Files\OpenSCAD\openscad.exe' -o bottom.stl bottom.scad
# 'C:\Program Files\OpenSCAD\openscad.com' -o bottom.stl bottom.scad

#rotate_extrude(convexity = 10)
#translate([2, 0, 0])
#circle(r = 1, $fn = 100);


