#!/usr/bin/env python3
"""Test with pygame."""

import logging
import sys

import pygame
import pygame.locals as pylocals
from gamelib import colors, fonts
from pipeline.util import logging as pipelog

log = logging.getLogger(__name__)


def main():
    """Entrypoint."""
    pygame.init()
    DISPLAY = pygame.display.set_mode((400, 300))
    pygame.display.set_caption('Hello, world.')
    log.debug(dir(fonts))

    font_obj = pygame.font.Font(fonts.open_sans, 32)
    text_surf_obj = font_obj.render(
        'Hello, world!', True, colors.GREEN, colors.BLUE)
    text_rect_obj = text_surf_obj.get_rect()
    text_rect_obj.center = (200, 150)

    while True:
        DISPLAY.fill(colors.WHITE)
        DISPLAY.blit(text_surf_obj, text_rect_obj)
        for event in pygame.event.get():
            if event.type == pylocals.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

if __name__ == '__main__':
    pipelog.config()
    main()
