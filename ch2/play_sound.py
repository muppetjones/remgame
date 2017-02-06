#!/usr/bin/env python3
"""Play sounds using pygame."""

import logging
import sys
import time

import pygame
from gamelib import sounds
from pipeline.util import logging as pipelog
from pygame import locals as pylocals

log = logging.getLogger(__name__)


def main():
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((400, 300))
    pygame.display.set_caption('Hello world!')

    pygame.mixer.music.load(sounds.background)
    pygame.mixer.music.play(-1, 0.0)

    log.debug(sounds.pickup)
    log.debug(sounds.beep2)
    sound_obj = pygame.mixer.Sound(sounds.pickup)
    # sound_obj = pygame.mixer.Sound(sounds.beep2)

    while True:
        for event in pygame.event.get():
            if event.type == pylocals.QUIT:
                pygame.quit()
                sys.exit()
            else:
                if event.type == 5:
                    sound_obj.play()
                    # time.sleep(1)
                    # sound_obj.stop()
        pygame.display.update()


if __name__ == '__main__':
    pipelog.config()
    main()
