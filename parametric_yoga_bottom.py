from __future__ import annotations
from solid import *
from solid.utils import *
from math import cos, radians, sin, pi, tau
import subprocess
import utils
import math
from dataclasses import dataclass
from typing import Callable

@dataclass
class Shape:
    raw_shape: OpenSCADObject
    parent: Shape = None
    trnsfm_off_parent: OpenSCADObject | Callable = up(0)
    local_offset: OpenSCADObject | Callable = up(0)

    @property
    def full_transform(self):
        parent_transform = up(0)
        if self.parent:
            parent_transform = self.parent.full_transform
        
        def combined_transforms(*args):
            return parent_transform(self.trnsfm_off_parent(self.local_offset(*args)))
        
        return combined_transforms

    def __call__(self):
        #return self.trnsfm_off_parent(self.local_offset)
        return self.full_transform(self.raw_shape)

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

def lerp(a: float, b: float, t: float) -> float:
    return (1 - t) * a + t * b

def centered_scaled_range(num_values, max_val, bias = 0):
    num_values_non_zero = num_values - 1

    vals = []

    for i in range(num_values):
        # Center around 0
        input = i - num_values_non_zero/2

        # Scale from -1 to 1
        input = input / (num_values_non_zero/2)
        
        # Scale to window distance
        input *= max_val

        vals.append(input + bias)
    return vals

def mirror_first_half_with_middle(second_half_values):
    return list(reversed(second_half_values)) + [second_half_values[0]] + second_half_values

FILENAME = 'yoga_mat_bottom_simple'
CIRCLE_SEGMENTS = 64
EPS = 0.01

ACTUAL_MAT_DIAMETER = 155 # mm
MAT_BUFFER_FRACTION_TOTAL = 0.06 # fairly comfortable

COMMAND_STRIP_WIDTH = 19.75 # mm, buffer built in
COMMAND_STRIP_HEIGHT = 50 # mm, full strength is 68mm
COMMAND_STRIP_DEPTH = 0.4 # mm
NUM_COMMAND_STRIPS = 2

WALL_ATTACHMENT_THICKNESS = 6 # mm
MIN_RING_HEIGHT = 8 # mm
MIN_RING_WIDTH = 3 # mm
MAX_RING_HEIGHT = COMMAND_STRIP_HEIGHT + 7 # mm
RING_SIGMOID_WINDOW_DISTANCE = 7.3 # Higher numbers mean a steeper curve
RING_SIGMOID_WINDOW_BIAS = -3.9 # More negative means more of the ring is thin

# DERIVED
MAT_DIAMETER = ACTUAL_MAT_DIAMETER * (1 + MAT_BUFFER_FRACTION_TOTAL)
MAT_RADIUS = MAT_DIAMETER/2
MAX_RING_WIDTH = WALL_ATTACHMENT_THICKNESS * 1.5
WALL_SIZE = (MAT_DIAMETER + MAX_RING_WIDTH) * 1.3

COMMAND_CUTOUT_WIDTH = COMMAND_STRIP_WIDTH * NUM_COMMAND_STRIPS
COMMAND_CUTOUT_HEIGHT = COMMAND_STRIP_HEIGHT
COMMAND_CUTOUT_PULL_EXTRA = 40 # mm

RING_WALL_CENTER_RADIUS = MAT_RADIUS + MIN_RING_WIDTH/2
RING_HEIGHT_DIFFERENCE = MAX_RING_HEIGHT - MIN_RING_HEIGHT/2
MIN_RING_HALF_HEIGHT = MIN_RING_HEIGHT / 2
MIN_RING_HALF_WIDTH = MIN_RING_WIDTH / 2
MAX_RING_HALF_WIDTH = MAX_RING_WIDTH / 2

# WALLS
wall_box = cube([WALL_SIZE, WALL_SIZE, WALL_SIZE], center = True)
wall = forward(WALL_SIZE/2)(wall_box)
floor_box = cube([WALL_SIZE, WALL_SIZE, WALL_SIZE], center = True)
floor_ = back(MAT_RADIUS)(down(WALL_SIZE/2)(floor_box))

 
# COMMAND STRIP CUTOUT
command_strip_cutout = Shape(
    raw_shape = cube([COMMAND_CUTOUT_WIDTH, COMMAND_STRIP_DEPTH, COMMAND_CUTOUT_HEIGHT + COMMAND_CUTOUT_PULL_EXTRA], center = True),
    trnsfm_off_parent = up(COMMAND_CUTOUT_HEIGHT/2 - COMMAND_CUTOUT_PULL_EXTRA/2),
    local_offset = translate([0, -COMMAND_STRIP_DEPTH/2  + EPS, 0]),
)

# RING
cross_section = utils.circle_points(num_points=CIRCLE_SEGMENTS/2)
path = utils.circle_points(radius=RING_WALL_CENTER_RADIUS, num_points=CIRCLE_SEGMENTS + 1)

vertical_xs = list(centered_scaled_range(CIRCLE_SEGMENTS//2, RING_SIGMOID_WINDOW_DISTANCE, bias = RING_SIGMOID_WINDOW_BIAS))
full_vertical_xs = mirror_first_half_with_middle(vertical_xs)
for x in full_vertical_xs:
    print(f'{x:0.2f}')


vertical_scale_factors = [sigmoid(x) for x in full_vertical_xs]

horizontal_xs = list(centered_scaled_range(CIRCLE_SEGMENTS//2, RING_SIGMOID_WINDOW_DISTANCE, bias = RING_SIGMOID_WINDOW_BIAS))
full_horizontal_xs = mirror_first_half_with_middle(horizontal_xs)

horizontal_scale_factors = [sigmoid(x) for x in full_horizontal_xs]

# The scaling factor needs to be scales to the ring height difference

scales = [(lerp(MIN_RING_WIDTH, MAX_RING_WIDTH, horizontal_scale_factors[i]), lerp(MIN_RING_HEIGHT, MAX_RING_HEIGHT, vertical_scale_factors[i])) for i in range(CIRCLE_SEGMENTS+1)]
#scales = [(1, 1) for i in range(CIRCLE_SEGMENTS+1)]

ring_back_offset = RING_WALL_CENTER_RADIUS + MAX_RING_HALF_WIDTH - WALL_ATTACHMENT_THICKNESS
ring = Shape(
    raw_shape = color([0.5,0.5,0.5], alpha=1)(extrude_along_path(cross_section, path, scales=scales, connect_ends=True)),
    trnsfm_off_parent = up(MIN_RING_HALF_HEIGHT),
    #trnsfm_off_parent = down(MOUNT_HEIGHT/2),
    local_offset = lambda *args: back(ring_back_offset)(rotate(90)(*args)),
)

# MAT CUTOUT
mat_cutout = Shape(
    raw_shape = cylinder(r=MAT_RADIUS, h=1000, segments=CIRCLE_SEGMENTS, center=True),
    parent = ring,
    local_offset = back(MAT_RADIUS),
)

# TEST MAT
test_mat = Shape(
    raw_shape = cylinder(r=ACTUAL_MAT_DIAMETER/2, h=600, segments=CIRCLE_SEGMENTS, center=True),
    parent = ring,
    local_offset=left(MAX_RING_WIDTH/4),
)



# def wall_mount():
        
#         translate(MOUNT_DEPTH/2)
#     return (
#             back(CUP_WALL_CENTER_RADIUS)(
#                 cube([MOUNT_WIDTH, CUP_THICKNESS, MOUNT_HEIGHT])
#             )
#         )


# Wall
#solid = wall()

# Full solid
#solid = wall_mount()

#solid = command_strip_cutout() + ring() #+ mat_cutout()

solid = ring()

cutouts = wall + floor_ + command_strip_cutout()
solid -= cutouts
#solid += color([0.5,0.5,1], alpha=0.2)(test_mat())
# solid -= wall
# solid = floor_
# solid -= command_strip_cutout()

#solid += cube([COMMAND_CUTOUT_WIDTH, COMMAND_STRIP_DEPTH, COMMAND_CUTOUT_HEIGHT])
#solid += color([0.5,0.5,1])(command_strip_cutout())

with open(f'{FILENAME}.scad', 'w') as f:
    f.write(scad_render(solid))

subprocess.run(['C:\Program Files\OpenSCAD\openscad.com', '-o', f'{FILENAME}.stl', f'{FILENAME}.scad'])
# 'C:\Program Files\OpenSCAD\openscad.exe' -o bottom.stl bottom.scad
# 'C:\Program Files\OpenSCAD\openscad.com' -o bottom.stl bottom.scad

#rotate_extrude(convexity = 10)
#translate([2, 0, 0])
#circle(r = 1, $fn = 100);


