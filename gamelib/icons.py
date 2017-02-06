#!/usr/bin/env python3
"""Draw various icons within a box using pygame."""

import logging
import sys

import pygame
from gamelib import colors

SHAPE_DICT = None

log = logging.getLogger(__name__)


def get_shape_dict():
    global SHAPE_DICT
    mod = sys.modules[__name__]
    if not SHAPE_DICT:
        SHAPE_DICT = {
            shape_func[5:]: getattr(mod, shape_func)
            for shape_func in dir(mod)
            if shape_func.startswith('draw_')
        }
    return SHAPE_DICT


def draw(display, shape, coord, size,
         color=colors.black, bg_color=colors.white):
    """Draw a shape.

    Arguments:
        shape: The string name of the shape to draw.
        color: The color of the shape.
        coord: The top left coordinates of the shape.
        size: The box dimensions in which the shape should be drawn.
    """
    shape_dict = get_shape_dict()
    shape_dict[shape](display, coord, size, color, bg_color)
    return


def draw_diamond(display, coord, box_size, color, bg_color):
    """Draw a diamond at the given location."""
    half = int(box_size * 0.5)
    left, top = coord
    vertices = [
        (left + half, top),
        (left + box_size - 1, top + half),
        (left + half, top + box_size - 1),
        (left, top + half),
    ]
    pygame.draw.polygon(display, color, vertices)
    return


def draw_donut(display, coord, box_size, color, bg_color):
    """Draw a donut at the given location."""
    left, top = coord
    half = int(box_size * 0.5)
    quarter = int(box_size * 0.25)
    center = (left + half, top + half)

    pygame.draw.circle(display, color, center, half - 5)
    pygame.draw.circle(display, bg_color, center, quarter - 5)
    return


def draw_lines(display, coord, box_size, color, bg_color):
    """Draw a pair of lines at the given location."""
    left, top = coord
    stroke = 6
    half_stroke = int(stroke / 2)
    left = left + half_stroke
    top = top + half_stroke
    box_size = box_size - stroke
    for i in range(0, box_size, int(stroke + 2)):
        pygame.draw.line(
            display, color,
            (left, top + i),
            (left + i, top),
            stroke,
        )
        pygame.draw.line(
            display, color,
            (left + i, top + box_size - 1),
            (left + box_size - 1, top + i),
            stroke,
        )
    return


def draw_oval(display, coord, box_size, color, bg_color):
    """Draw an oval at the given location."""
    left, top = coord
    half = int(box_size * 0.5)
    quarter = int(box_size * 0.25)
    pygame.draw.ellipse(display, color, (left, top + quarter, box_size, half))


def draw_square(display, coord, box_size, color, bg_color):
    """Draw a square at the given location."""
    left, top = coord
    half = int(box_size * 0.5)
    quarter = int(box_size * 0.25)
    pygame.draw.rect(
        display, color, (left + quarter, top + quarter, half, half))
    return
