from solid import *
from solid.utils import *
from math import cos, radians, sin, pi, tau

EPS = 0.01

MAT_RADIUS = 16.5/2 # cm
CUP_THICKNESS = 1
CUP_DEPTH = 2
CIRCLE_SEGMENTS = 64
CUP_STRUT_WIDTH = 2
CUTOUT_EDGE = 1 #CUP_THICKNESS * 1.5
N_STRUTS = 5

MOUNT_WIDTH = 2.1 * 2 # 2.1 for large command strip
MOUNT_HEIGHT = 6.8 # 6.8 for large command strip

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
     

def circle_points(radius, num_points=48):
    angles = frange(0, tau, num_steps=num_points, include_end=True)
    points = list([Point2(radius*cos(a), radius*sin(a)) for a in angles])
    return points

def ring():
    cross_section_radius = CUP_THICKNESS/2
    cross_section = circle_points(radius=cross_section_radius)
    path = circle_points(radius=CUP_WALL_CENTER_RADIUS - cross_section_radius, num_points=CIRCLE_SEGMENTS + 1)
    return extrude_along_path(cross_section, path)


solid = cup_walls() + cup_bottom(cutout=True) + wall_mount() + up(CUP_DEPTH + CUP_THICKNESS)(ring())
# solid = cup_shape()

with open('bottom.scad', 'w') as f:
    f.write(scad_render(solid))


#rotate_extrude(convexity = 10)
#translate([2, 0, 0])
#circle(r = 1, $fn = 100);

