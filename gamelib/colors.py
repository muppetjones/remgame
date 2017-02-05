#!/usr/bin/env python3
"""Declare basic colors."""

import logging
import sys

import pygame
from pipeline.util import logging as pipelog
from pygame import locals as pylocals

log = logging.getLogger(__name__)


BLACK = pygameColor(0, 0, 0)
WHITE = pygameColor(255, 255, 255)
RED = pygameColor(255, 0, 0)
GREEN = pygameColor(0, 255, 0)
BLUE = pygameColor(0, 0, 255)


def main():
    pass


if __name__ == '__main__':
    pipelog.config()
    main()
