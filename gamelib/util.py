"""Various utility methods for handling pygame."""

import sys

import pygame
from pygame.locals import K_ESCAPE, KEYUP, QUIT


def terminate():
    pygame.quit()
    sys.exit()


def check_for_quit():
    for event in pygame.event.get(QUIT):
        terminate()  # any quit event exits
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()  # quit on escape key
        pygame.event.post(event)  # put the object back
    return
