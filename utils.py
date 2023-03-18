from solid import *
from solid.utils import *
from math import cos, radians, sin, pi, tau


def circle_points(radius=1, num_points=48):
    angles = frange(0, tau, num_steps=num_points, include_end=True)
    points = list([Point2(radius*cos(a), radius*sin(a)) for a in angles])
    return points