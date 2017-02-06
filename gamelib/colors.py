#!/usr/bin/env python3
"""Declare basic colors."""

import logging
import sys

import pygame
from gamelib import logging as gamelog

log = logging.getLogger(__name__)

color_dict = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),

    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),

    'yellow': (255, 255, 0),
    'orange': (255, 128, 0),
    'purple': (255, 0, 255),
    'cyan': (0, 255, 255),
    'navy_blue': (60, 60, 100),

    'light_gray': (200, 200, 200),
    'gray': (100, 100, 100),
    'dark_gray': (50, 50, 50),
}


class colorblind():
    DARK_PINK = (120, 28, 129)
    LIGHT_PINK = (221, 153, 187)
    DARK_BLUE = (31, 102, 170)
    LIGHT_BLUE = (119, 179, 221)
    GREEN = (17, 119, 85)
    YELLOW = (246, 193, 65)
    ORANGE = (232, 140, 40)
    RED = (217, 33, 32)


def load_colors(load_dict):
    """meh."""
    for name, rgb in load_dict.items():
        setattr(sys.modules[__name__], name.upper(), rgb)
        setattr(sys.modules[__name__], name.lower(), pygame.Color(*rgb))
        log.debug(pygame.Color(*rgb))

    colorblind_colors = colorblind.__dict__.copy()
    for name, rgb in colorblind_colors.items():
        if not name.startswith('__'):
            setattr(colorblind, name.lower(), pygame.Color(*rgb))
    return


load_colors(color_dict)


def main():
    pass


if __name__ == '__main__':
    gamelog.config()
    main()
