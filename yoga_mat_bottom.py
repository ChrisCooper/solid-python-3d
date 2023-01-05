from solid import *
from solid.utils import *
from math import cos, radians, sin, pi, tau

MAT_RADIUS = 16.5/2 # cm
CUP_THICKNESS = 1
CUP_DEPTH = 2


def cup_shape():
    mat_hole = cylinder(r=MAT_RADIUS, h=CUP_DEPTH + 0.5)
    cup = cylinder(r=MAT_RADIUS + CUP_THICKNESS, h=CUP_DEPTH+CUP_THICKNESS)
    cup = difference()(
        cup,
        up(CUP_THICKNESS)(mat_hole),
    )

def circle_points(radius, num_points=48):
    angles = frange(0, tau, num_steps=num_points, include_end=True)
    points = list([Point2(radius*cos(a), radius*sin(a)) for a in angles])
    return points

def ring():
    circle = circle_points(radius=CUP_THICKNESS/2)
    path = circle_points(radius=50, num_points=64)
    return extrude_along_path(circle, path)


shape = cup_shape()
shape = ring()

with open('bottom.scad', 'w') as f:
    f.write(scad_render(shape))


#rotate_extrude(convexity = 10)
#translate([2, 0, 0])
#circle(r = 1, $fn = 100);