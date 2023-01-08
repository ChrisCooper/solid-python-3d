from solid import *
from solid.utils import *
from math import cos, radians, sin, pi, tau
import random

EPS = 0.01
MAX_DIAMETER = 100
MAX_HEIGHT = 5

N_ROWS = 5
N_COLS = 5

MAX_SPACING = 1

SUBDIVISIONS = 3
SUBD_MAX_DEPTH = 3


def make_squares(subd_depth, diameter, base_height):
    base_dimensions = [diameter, diameter, base_height]
    base_cube = up(base_height/2)(cube(base_dimensions, center=True))

    if subd_depth == SUBD_MAX_DEPTH:
        return base_cube

    spacing = MAX_SPACING / (SUBDIVISIONS - 1)**subd_depth
    sub_square_diameter = (diameter - spacing*(SUBDIVISIONS - 1))/SUBDIVISIONS

    squares = base_cube

    offset_shift = diameter/2 - sub_square_diameter/2

    return squares + left(offset_shift)(
        forward(offset_shift)(
            sub_squares(subd_depth, base_height, sub_square_diameter, spacing)
        )
    )
    

def sub_squares(subd_depth, base_height, sub_square_diameter, spacing):
    squares = cube(0)
    
    for row_i in range(SUBDIVISIONS):
        for col_j in range(SUBDIVISIONS):
            
            height_scale = MAX_HEIGHT / 5**subd_depth
            height = base_height + height_scale * random.uniform(0.1, 1)

            right_shift = col_j * (sub_square_diameter + spacing)
            back_shift = row_i * (sub_square_diameter + spacing)
            
            squares += right(right_shift)(
                back(back_shift) (
                    make_squares(subd_depth + 1, sub_square_diameter, height)
                )
            )
    
    return squares

with open('squares.scad', 'w') as f:
    f.write(scad_render(make_squares(0, MAX_DIAMETER, MAX_HEIGHT)))