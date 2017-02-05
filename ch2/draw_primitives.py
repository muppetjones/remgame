#!/usr/bin/env python3
"""Draw primitive shapes using pygame."""

import logging
import sys

import pygame
from gamelib import colours
from pipeline.util import logging as pipelog
from pygame import locals as pylocals

log = logging.getLogger(__name__)


def main():
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((500, 400), 0, 32)
    pygame.display.set_caption('Drawing!')

    # draw on surface
    DISPLAYSURF.fill(colours.WHITE)
    pygame.draw.polygon(
        DISPLAYSURF, GREEN,
        ((146, 0), (291, 106), (236, 277), (56, 277), (0, 106))
    )
    pygame.draw.line(DISPLAYSURF, BLUE, (60, 60), (120, 60), 4)
    pygame.draw.line(DISPLAYSURF, BLUE, (120, 60), (60, 120))
    pygame.draw.line(DISPLAYSURF, BLUE, (60, 120), (120, 120), 4)
    pygame.draw.circle(DISPLAYSURF, BLUE, (300, 50), 20, 0)
    pygame.draw.ellipse(DISPLAYSURF, RED, (300, 250, 40, 80), 1)
    pygame.draw.rect(DISPLAYSURF, RED, (200, 150, 100, 50))

    pixObj = pygame.PixelArray(DISPLAYSURF)
    pixObj[480][380] = colours.BLACK
    pixObj[482][382] = colours.BLACK
    pixObj[483][384] = colours.BLACK
    pixObj[486][386] = colours.BLACK
    pixObj[488][388] = colours.BLACK
    del pixObj

    while True:
        for event in pygame.event.get():
            if event.type == pylocals.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()


if __name__ == '__main__':
    pipelog.config()
    main()
