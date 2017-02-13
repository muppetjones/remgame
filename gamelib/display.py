#!/usr/bin/env python3
"""Define a Display object for interfacing with a pygame display."""


import pygame
from gamelib import colors, fonts

# Standards
FPS = 30
WIN_WIDTH = 640
WIN_HEIGHT = 480

# colors
BG_COLOR = colors.light_gray
BG_COLOR_LIGHT = colors.gray

# font
FONT = fonts.open_sans
FONT_SIZE = 20


class Display():
    """Store and handle data related to pygame.display."""

    def __init__(
            self, fps=FPS, win_width=WIN_WIDTH, win_height=WIN_HEIGHT,
            bg_color=BG_COLOR, bg_color_light=BG_COLOR_LIGHT, caption='',
            font=FONT, font_size=FONT_SIZE,
    ):
        """Initialize a pygame display."""
        self.fps = fps
        self.fps_clock = pygame.time.Clock()
        self.width = win_width
        self.height = win_height
        self.size = (win_width, win_height)
        self.display = pygame.display.set_mode(self.size)

        self.caption = caption
        pygame.display.set_caption(self.caption)

        self.bg_color = bg_color
        self.bg_color_light = bg_color_light

        self.font = pygame.font.Font(font, font_size)

        self.fill()  # fill display with the bg color

    def blit(self, *args, **kwargs):
        """Draw text."""
        self.display.blit(*args, **kwargs)

    def fill(self, color=None):
        """Fill in the background."""
        color = color if color else self.bg_color
        self.display.fill(color)

    def tick(self):
        """Tick away fps."""
        self.fps_clock.tick(self.fps)

    def update(self):
        """Update the screen."""
        pygame.display.update()
        self.tick()


# __END__
