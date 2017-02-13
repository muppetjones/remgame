"""GameBox."""

import logging

import pygame

log = logging.getLogger(__name__)


class GameBox():
    """Store data for a single box."""

    BOARD_DATA = {
        'n_col': None,
        'n_row': None,
        'gap_size': None,
        'box_size': None,
        'x_margin': None,
        'y_margin': None,
        'box_color': None,
        'box_bg_color': None,
    }

    def __init__(self, coord=None, text='', color=None):
        """Initialize."""
        self.box_coord = coord
        self.box_x, self.box_y = coord
        self.text = text
        self.color = color

        self.pixel_coord = self.upper_left_coord_of_box(*coord)
        self.pixel_x, self.pixel_y = self.pixel_coord

        self.box = pygame.Rect(
            self.pixel_x, self.pixel_y, self.box_size, self.box_size)

    @classmethod
    def set_board_data(cls, data):
        """Set the board data for the class."""
        cls.BOARD_DATA.update(data)
        for k, v in cls.BOARD_DATA.items():
            setattr(cls, k, v)

    @classmethod
    def upper_left_coord_of_box(cls, x, y):
        """Convert board coordinates to pixel coordinates.

        Arguments:
            x, y: Box coordinates.
        Return:
            A tuple of pixel coordinates.
        """
        left = x * (cls.box_size + cls.gap_size) + cls.x_margin
        top = y * (cls.box_size + cls.gap_size) + cls.y_margin
        return (left, top)

    def contains(self, pixel_coord):
        """Checks if the given pixel is within the box."""
        return self.box.collidepoint(*pixel_coord)

    def draw(self, display, offset_x=0, offset_y=0):
        """Draw ourselves.

        Arguments:
            display: A pygame.display object.
            force_reveal: If true, will draw the revealed card,
                regardless of the value of self.revealed.
        Returns: None.
        """
        left, top = self.pixel_coord

        # draw rectagle
        color = self.color if self.color else self.box_color
        pygame.draw.rect(
            display.display, color,
            (left + offset_x, top + offset_y, self.box_size, self.box_size),
        )

        if self.text:
            surface = display.font.render(
                self.text, True, self.box_color)  # True = antialias
            rect = surface.get_rect()
            rect.center = (
                left + int(self.box_size / 2) + offset_x,
                top + int(self.box_size / 2) + offset_y,
            )
            display.blit(surface, rect)
        return
