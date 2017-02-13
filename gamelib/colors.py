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


class colorblind_8():
    # eight
    DARK_PINK = (120, 28, 129)
    LIGHT_PINK = (221, 153, 187)
    DARK_BLUE = (31, 102, 170)
    LIGHT_BLUE = (119, 179, 221)
    GREEN = (17, 119, 85)
    YELLOW = (246, 193, 65)
    ORANGE = (232, 140, 40)
    RED = (217, 33, 32)


class colorblind_14():
    # 14 colors
    DARK_PINK = (136, 46, 114)
    PINK = (177, 120, 166)
    LIGHT_PINK = (214, 193, 222)

    DARK_BLUE = (25, 101, 176)
    BLUE = (82, 137, 199)
    LIGHT_BLUE = (123, 175, 222)

    DARK_GREEN = (78, 178, 101)
    GREEN = (144, 201, 135)
    LIGHT_GREEN = (202, 224, 171)

    YELLOW = (247, 238, 85)

    DARK_ORANGE = (232, 96, 28)
    ORANGE = (241, 147, 45)
    LIGHT_ORANGE = (246, 193, 65)

    RED = (220, 5, 12)


def load_colors(load_dict):
    """meh."""
    for name, rgb in load_dict.items():
        setattr(sys.modules[__name__], name.upper(), rgb)
        setattr(sys.modules[__name__], name.lower(), pygame.Color(*rgb))
        log.debug(pygame.Color(*rgb))

    colorblind_colors = colorblind_8.__dict__.copy()
    for name, rgb in colorblind_colors.items():
        if not name.startswith('__'):
            setattr(colorblind_8, name.lower(), pygame.Color(*rgb))

    colorblind_colors = colorblind_14.__dict__.copy()
    for name, rgb in colorblind_colors.items():
        if not name.startswith('__'):
            setattr(colorblind_14, name.lower(), pygame.Color(*rgb))

    setattr(sys.modules[__name__], 'colorblind', colorblind_8)

    return


load_colors(color_dict)


def alpha(color, alpha_value):
    try:
        r, g, b, _ = color  # w/ alpha
    except:
        r, g, b = color  # w/ alpha
    return (r, g, b, alpha_value)


def main():
    pass


if __name__ == '__main__':
    gamelog.config()
    main()
