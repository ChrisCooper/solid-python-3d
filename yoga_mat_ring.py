from solid import *
from solid.utils import *
from math import cos, radians, sin, pi, tau
import subprocess
import utils

MAT_RADIUS = 165/2.0 # mm
RING_THICKNESS = 6
RING_HEIGHT = 5
CIRCLE_SEGMENTS = 256

LIP_BASE_SCALE = 4
RAMP_UP_MAX_HEIGHT = 70 / RING_THICKNESS
RAMP_UP_FRACTION = 0.4


MOUNT_WIDTH = 21 * 2 # 21 for large command strip
MOUNT_HEIGHT = 68 # 68 for large command strip

# DERIVED
RING_WALL_CENTER_RADIUS = MAT_RADIUS + RING_THICKNESS/2
MAX_HEIGHT = RING_HEIGHT * LIP_BASE_SCALE * 3

def mat_hole():
    return cylinder(r=MAT_RADIUS, h=MAX_HEIGHT*2, segments=CIRCLE_SEGMENTS, center=True)

def ring():
    cross_section_radius = RING_THICKNESS/2
    cross_section = utils.circle_points(radius=cross_section_radius)
    path = utils.circle_points(radius=RING_WALL_CENTER_RADIUS, num_points=CIRCLE_SEGMENTS + 1)

    ramp_up_length = int((RAMP_UP_FRACTION * (CIRCLE_SEGMENTS+1)) // 2)
    ramp_ups = [1 + RAMP_UP_MAX_HEIGHT*((i+1.0)/ramp_up_length)**2 for i in range(ramp_up_length)]
    ramp_up_scale = [(0.8 + ru/5, LIP_BASE_SCALE - 1 + ru) for ru in ramp_ups]
    scales = list(reversed(ramp_up_scale)) + [(1,LIP_BASE_SCALE) for i in range(CIRCLE_SEGMENTS+1 - ramp_up_length*2)] + ramp_up_scale

    #ramp_up_transforms = [ring_transform(ru*1) for ru in ramp_ups]
    #transforms = list(reversed(ramp_up_transforms)) + [ring_transform(0) for i in range(CIRCLE_SEGMENTS+1 - ramp_up_length*2)] + ramp_up_transforms

    return rotate([0,0,-90])(extrude_along_path(cross_section, path, scales=scales))
    #return rotate([0,0,-90])(extrude_along_path(cross_section, path, scales=scales, transforms=transforms))

def wall_mount_cutout():
    width = RING_THICKNESS*10
    return left(MOUNT_WIDTH/2)(
            back(RING_WALL_CENTER_RADIUS + RING_THICKNESS + width/2 - 2)(
                cube([MAT_RADIUS*3, RING_THICKNESS*10, MAX_HEIGHT*2], center=True)
            )
        )

def ring_point_caps():
    c = cube([MAX_HEIGHT, MAX_HEIGHT, MAX_HEIGHT], center=True)
    return back(RING_WALL_CENTER_RADIUS)(
        up(MAX_HEIGHT/2 + MOUNT_HEIGHT/2)(c) + 
        down(MAX_HEIGHT/2 + MOUNT_HEIGHT/2)(c)
    )
    

solid = ring() - mat_hole() - wall_mount_cutout() - ring_point_caps()

with open('ring.scad', 'w') as f:
    f.write(scad_render(solid))

subprocess.run(['C:\Program Files\OpenSCAD\openscad.com', '-o', 'ring.stl', 'ring.scad'])