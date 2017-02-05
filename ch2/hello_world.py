#!/usr/bin/env python3
"""pygame book."""

import logging
import sys

import pygame
from pipeline.util import logging as pipelog
from pygame import locals as pylocals

log = logging.getLogger(__name__)


def main():
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((400, 300))
    pygame.display.set_caption('Hello world!')
    while True:
        for event in pygame.event.get():
            if event.type == pylocals.QUIT:
                pygame.quit()
                sys.exit()
            else:
                log.info('got event: {}, {}'.format(event.type, event))
        pygame.display.update()


if __name__ == '__main__':
    pipelog.config()
    main()
