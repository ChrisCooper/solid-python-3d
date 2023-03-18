from __future__ import annotations
from solid import *
from solid.utils import *
from math import cos, radians, sin, pi, tau
import subprocess
import utils
import math
from dataclasses import dataclass
from typing import Callable


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

RING_FILENAME = 'yoga_mat_ring_parametric'
BOTTOM_FILENAME = 'yoga_mat_bottom_parametric'
CIRCLE_SEGMENTS = 64
EPS = 0.01

MAKE_BOTTOM = False
ACTUAL_MAT_DIAMETER = 155 # mm
MAT_BUFFER_FRACTION_TOTAL = 0.06 # fairly comfortable

COMMAND_STRIP_WIDTH = 19.75 # mm, buffer built in
COMMAND_STRIP_HEIGHT = 50 # mm, full strength is 68mm
COMMAND_STRIP_DEPTH = 0.4 # mm
NUM_COMMAND_STRIPS = 2

RING_WIDTH = 6 # mm
MAX_RING_WIDTH = 12 # mm
MIN_RING_HEIGHT = 16 # mm
MAX_RING_HEIGHT = COMMAND_STRIP_HEIGHT + 7 # mm
RING_SIGMOID_WINDOW_DISTANCE = 7.3 # Higher numbers mean a steeper curve
RING_SIGMOID_WINDOW_BIAS = -3.3 # More negative means more of the ring is thin

BOTTOM_THICKNESS = 5 # mm

# DERIVED
if MAKE_BOTTOM:
    MIN_RING_HEIGHT = BOTTOM_THICKNESS

MAT_DIAMETER = ACTUAL_MAT_DIAMETER * (1 + MAT_BUFFER_FRACTION_TOTAL)
MAT_RADIUS = MAT_DIAMETER/2
WALL_SIZE = (MAT_DIAMETER + RING_WIDTH) * 1.3

COMMAND_CUTOUT_WIDTH = COMMAND_STRIP_WIDTH * NUM_COMMAND_STRIPS
COMMAND_CUTOUT_HEIGHT = COMMAND_STRIP_HEIGHT
COMMAND_CUTOUT_PULL_EXTRA = 40 # mm

RING_HEIGHT_DIFFERENCE = MAX_RING_HEIGHT - MIN_RING_HEIGHT/2
MIN_RING_HALF_HEIGHT = MIN_RING_HEIGHT / 2
RING_HALF_WIDTH = RING_WIDTH / 2

MINKOWSKI_RADIUS=RING_WIDTH

# WALLS
wall_box = cube([WALL_SIZE, WALL_SIZE, WALL_SIZE], center = True)
wall = forward(WALL_SIZE/2)(wall_box)
floor_box = cube([WALL_SIZE, WALL_SIZE, WALL_SIZE], center = True)
floor_ = back(MAT_RADIUS)(down(WALL_SIZE/2)(floor_box))

 
# COMMAND STRIP CUTOUT
command_strip_cutout = translate([0, -COMMAND_STRIP_DEPTH/2  + EPS, COMMAND_CUTOUT_HEIGHT/2 - COMMAND_CUTOUT_PULL_EXTRA/2])(
    cube([COMMAND_CUTOUT_WIDTH, COMMAND_STRIP_DEPTH, COMMAND_CUTOUT_HEIGHT + COMMAND_CUTOUT_PULL_EXTRA], center = True)
)


# Center on center of yoga mat, at 0 height
def center_on_yoga_mat():
    return lambda *args: translate([
        0,
        -RING_HALF_WIDTH -MAT_RADIUS,
        0
    ])(*args)


# RING
def get_ring():
    cross_section = utils.circle_points(num_points=CIRCLE_SEGMENTS/2)
    path = utils.circle_points(radius=MAT_RADIUS + RING_HALF_WIDTH, num_points=CIRCLE_SEGMENTS + 1)[:-1] # Don't include the last point, because connect_ends will bridge to the first one

    vertical_xs = list(centered_scaled_range(CIRCLE_SEGMENTS//2, RING_SIGMOID_WINDOW_DISTANCE, bias = RING_SIGMOID_WINDOW_BIAS))
    full_vertical_xs = mirror_first_half_with_middle(vertical_xs)

    # multiply by 2 because we cut off half the model
    vertical_scale_factors = [sigmoid(x) * 2 for x in full_vertical_xs]

    horizontal_xs = list(centered_scaled_range(CIRCLE_SEGMENTS//2, RING_SIGMOID_WINDOW_DISTANCE, bias = RING_SIGMOID_WINDOW_BIAS))
    full_horizontal_xs = mirror_first_half_with_middle(horizontal_xs)

    horizontal_scale_factors = [sigmoid(x) for x in full_horizontal_xs]

    # The scaling factor needs to be scales to the ring height difference

    scales = [(lerp(RING_WIDTH, MAX_RING_WIDTH, horizontal_scale_factors[i]), lerp(MIN_RING_HEIGHT, MAX_RING_HEIGHT, vertical_scale_factors[i])) for i in range(CIRCLE_SEGMENTS+1)]
    #scales = [(1, 1) for i in range(CIRCLE_SEGMENTS+1)]

    return extrude_along_path(cross_section, path, scales=scales, connect_ends=True)
    #return extrude_along_path(cross_section, path, connect_ends=True)

ring = center_on_yoga_mat() (
    up(MIN_RING_HALF_HEIGHT) (
        rotate([0, 0, 90]) (
            get_ring()
        )
    )
)


def get_bottom():
    return up(BOTTOM_THICKNESS/2 - EPS)(cylinder(r=MAT_RADIUS+RING_HALF_WIDTH, h=BOTTOM_THICKNESS, segments=CIRCLE_SEGMENTS, center=True))
      
bottom = center_on_yoga_mat()(
    get_bottom()
)

def get_bottom_cutout():
#     # BOTTOM
    
    return minkowski()(
        cylinder(r=MAT_RADIUS - MINKOWSKI_RADIUS, h=BOTTOM_THICKNESS, segments=CIRCLE_SEGMENTS, center=True),
        sphere(r=MINKOWSKI_RADIUS)
    )

bottom_cutout = center_on_yoga_mat()(
    up(BOTTOM_THICKNESS + MINKOWSKI_RADIUS)(
        get_bottom_cutout()
    )
)

# MAT CUTOUT
mat_cutout = center_on_yoga_mat() (
    cylinder(r=MAT_RADIUS, h=1000, segments=CIRCLE_SEGMENTS, center=True)
)
 
# TEST MAT
test_mat = center_on_yoga_mat() (
    color([0.3,0.3,0.3], alpha=0.1) (
        cylinder(r=ACTUAL_MAT_DIAMETER/2, h=600, segments=CIRCLE_SEGMENTS, center=True)
    )
)
mat_pin = center_on_yoga_mat() (
    color([0.3,0.3,0.3], alpha=0.3) (
        cylinder(r=1, h=600, segments=6, center=True)
    )
)
    #trnsfm_off_parent=back(MAT_RADIUS),


# ---------------- RENDERING ----------------
ring_solid = ring


ring_solid -= mat_cutout
#ring_solid += test_mat

if MAKE_BOTTOM:
    ring_solid += bottom

cutouts = wall + floor_ + command_strip_cutout
ring_solid -= cutouts
#ring_solid += bottom_cutout

#ring_solid += back((MAT_RADIUS + RING_HALF_WIDTH)/2)(cube([50, MAT_RADIUS + RING_HALF_WIDTH, 50], center=True))
#ring_solid += back((MAT_RADIUS + RING_HALF_WIDTH)/2)(cube([50, MAT_RADIUS, 100], center=True))
#ring_solid += mat_pin

#ring_solid += test_mat

filename = RING_FILENAME
if MAKE_BOTTOM:
    filename = BOTTOM_FILENAME

with open(f'{filename}.scad', 'w') as f:
    f.write(scad_render(ring_solid))

subprocess.run(['C:\Program Files\OpenSCAD\openscad.com', '-o', f'{filename}.stl', f'{filename}.scad'])
