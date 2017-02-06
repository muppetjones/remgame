#!/usr/bin/env python3
"""Draw primitive shapes using pygame."""

import logging
import sys

import pygame
from gamelib import logging as gamelog
from gamelib import colors
from pygame import locals as pylocals

log = logging.getLogger(__name__)


def main():
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((500, 400), 0, 32)
    pygame.display.set_caption('Drawing!')

    # draw on surface
    DISPLAYSURF.fill(colors.WHITE)
    pygame.draw.polygon(
        DISPLAYSURF, colors.GREEN,
        ((146, 0), (291, 106), (236, 277), (56, 277), (0, 106))
    )
    pygame.draw.aaline(DISPLAYSURF, colors.BLUE, (60, 60), (120, 60), 4)
    pygame.draw.aaline(DISPLAYSURF, colors.BLUE, (120, 60), (60, 120))
    pygame.draw.aaline(DISPLAYSURF, colors.BLUE, (60, 120), (120, 120), 4)
    pygame.draw.circle(DISPLAYSURF, colors.BLUE, (300, 50), 20, 0)
    pygame.draw.ellipse(DISPLAYSURF, colors.RED, (300, 250, 40, 80), 1)
    pygame.draw.rect(DISPLAYSURF, colors.RED, (200, 150, 100, 50))

    pixObj = pygame.PixelArray(DISPLAYSURF)
    pixObj[480][380] = colors.BLACK
    pixObj[482][382] = colors.BLACK
    pixObj[483][384] = colors.BLACK
    pixObj[486][386] = colors.BLACK
    pixObj[488][388] = colors.BLACK
    del pixObj

    while True:
        for event in pygame.event.get():
            if event.type == pylocals.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()


if __name__ == '__main__':
    gamelog.config()
    main()
