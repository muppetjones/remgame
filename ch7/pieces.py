#!/usr/bin/env python3
"""Define the Tetris shapes and colors."""

from gamelib import colors

TEMPLATE_WIDTH = 5
TEMPLATE_HEIGHT = 5
BLANK = '.'

shape_templates = {
    'S': [
        ('.....',
         '.....',
         '..oo.',
         '.oo..',
         '.....'),
        ('.....',
         '..o..',
         '..oo.',
         '...o.',
         '.....')
    ],

    'Z': [
        ('.....',
         '.....',
         '.oo..',
         '..oo.',
         '.....'),
        ('.....',
         '..o..',
         '.oo..',
         '.o...',
         '.....')
    ],

    'I': [
        ('..o..',
         '..o..',
         '..o..',
         '..o..',
         '.....'),
        ('.....',
         '.....',
         'oooo.',
         '.....',
         '.....')
    ],

    'O': [
        ('.....',
         '.....',
         '.oo..',
         '.oo..',
         '.....')
    ],

    'J': [
        ('.....',
         '.o...',
         '.ooo.',
         '.....',
         '.....'),
        ('.....',
         '..oo.',
         '..o..',
         '..o..',
         '.....'),
        ('.....',
         '.....',
         '.ooo.',
         '...o.',
         '.....'),
        ('.....',
         '..o..',
         '..o..',
         '.oo..',
         '.....')
    ],

    'L': [
        ('.....',
         '...o.',
         '.ooo.',
         '.....',
         '.....'),
        ('.....',
         '..o..',
         '..o..',
         '..oo.',
         '.....'),
        ('.....',
         '.....',
         '.ooo.',
         '.o...',
         '.....'),
        ('.....',
         '.oo..',
         '..o..',
         '..o..',
         '.....')
    ],

    'T': [
        ('.....',
         '..o..',
         '.ooo.',
         '.....',
         '.....'),
        ('.....',
         '..o..',
         '..oo.',
         '..o..',
         '.....'),
        ('.....',
         '.....',
         '.ooo.',
         '..o..',
         '.....'),
        ('.....',
         '..o..',
         '.oo..',
         '..o..',
         '.....')
    ],
}


SHAPES = {
    'S': (
        shape_templates['S'],  # shape
        colors.colorblind_14.DARK_GREEN,  # main color
        colors.colorblind_14.GREEN
    ),  # highlight color
    'Z': (
        shape_templates['Z'],
        colors.colorblind_14.GREEN,
        colors.colorblind_14.LIGHT_GREEN
    ),

    'I': (
        shape_templates['I'],
        colors.colorblind_14.DARK_ORANGE,
        colors.colorblind_14.ORANGE
    ),

    'O': (
        shape_templates['O'],
        colors.colorblind_14.DARK_PINK,
        colors.colorblind_14.PINK
    ),

    'J': (
        shape_templates['J'],
        colors.colorblind_14.DARK_BLUE,
        colors.colorblind_14.BLUE
    ),
    'L': (
        shape_templates['L'],
        colors.colorblind_14.BLUE,
        colors.colorblind_14.LIGHT_BLUE
    ),

    'T': (
        shape_templates['T'],
        colors.colorblind_14.PINK,
        colors.colorblind_14.LIGHT_PINK
    ),
}
