from solid import *
from solid.utils import *
from math import cos, radians, sin, pi, tau

HEX_LONG_TO_SHORT_RATIO = 0.8660254

EPS = 0.01
MAX_DIAMETER = 100
REFERENCE_HEIGHT = 100

N_ROWS = 6
N_COLS = 2

SPACER = 2

def hex():
    return cylinder(d=MAX_DIAMETER+EPS, h=REFERENCE_HEIGHT, segments=6)

def row():
    row = cube(0)

    for i in range(N_COLS):
        row += right((MAX_DIAMETER + SPACER) * 1.5 * i)(hex())

    return row

def board():
    board = cube(0)

    for i in range(N_ROWS):
        right_offset = 0 if i % 2 == 0 else (MAX_DIAMETER + SPACER)*0.75
        
        board += right(right_offset) (
            back(i * (MAX_DIAMETER + SPACER) * HEX_LONG_TO_SHORT_RATIO / 2) (
                row()
            )
        )

    return board


# board += right(MAX_DIAMETER*0.75) (
#     back(MAX_DIAMETER * HEX_LONG_TO_SHORT_RATIO / 2) (
#         row
#     )
# )

#for i in range 



with open('hex.scad', 'w') as f:
    f.write(scad_render(board()))