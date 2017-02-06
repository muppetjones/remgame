#!/usr/bin/env python3
"""Simple slide puzzle.

Based on slidepuzzle by Al Sweigart.
"""

import logging
import random
import sys

import pygame
from gamelib import logging as gamelog
from gamelib import GameBoard, colors, fonts
from pygame.locals import (K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_UP, KEYUP,
                           MOUSEBUTTONUP, QUIT, K_a, K_d, K_s, K_w)

log = logging.getLogger(__name__)

# static variables
FPS = 60
WIN_WIDTH = 640
WIN_HEIGHT = 480
N_COL, N_ROW = 4, 4
SIDE_BAR_WIDTH = 200

# font
FONT = fonts.open_sans
FONT_SIZE = 20

# colors
BG_COLOR = colors.light_gray
BG_COLOR_LIGHT = colors.gray

TEXT_COLOR = colors.white
TILE_COLOR = colors.colorblind.dark_pink

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

KEY_LEFT = (K_LEFT, K_a)
KEY_RIGHT = (K_RIGHT, K_d)
KEY_UP = (K_UP, K_w)
KEY_DOWN = (K_DOWN, K_s)

#
#  ######
#  #     # #  ####  #####  #        ##   #   #
#  #     # # #      #    # #       #  #   # #
#  #     # #  ####  #    # #      #    #   #
#  #     # #      # #####  #      ######   #
#  #     # # #    # #      #      #    #   #
#  ######  #  ####  #      ###### #    #   #


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
        """Draw?"""
        self.display.blit(*args, **kwargs)

    def fill(self, color=None):
        """Fill in the background."""
        color = color if color else self.bg_color
        self.display.fill(color)

    def tick(self):
        self.fps_clock.tick(self.fps)

#
#  ######
#  #     # #    # ##### #####  ####  #    #
#  #     # #    #   #     #   #    # ##   #
#  ######  #    #   #     #   #    # # #  #
#  #     # #    #   #     #   #    # #  # #
#  #     # #    #   #     #   #    # #   ##
#  ######   ####    #     #    ####  #    #


class GameButton():
    """Store and handle data for a single button."""

    def __init__(
            self, display, text='', coord=None, action=None,
            color=TEXT_COLOR, bg_color=TILE_COLOR, antialias=True,
    ):
        """Initialize."""
        self.bg_color = bg_color
        self.pixel_coord = coord
        self.action = action
        self.text = text

        # create text
        self.surface = display.font.render(text, True, color, self.bg_color)
        self.rect = self.surface.get_rect()

        # create box behind text
        box = self.rect.copy()
        box.size = (box.width + 10, box.height + 5)
        self.box = box

        self.width = self.box.width
        self.height = self.box.height

    def draw(self, display):
        """Draw the button."""
        self.rect.bottomright = self.pixel_coord
        self.box.center = self.rect.center

        pygame.draw.rect(display.display, self.bg_color, self.box)
        display.blit(self.surface, self.rect)

    def contains(self, pixel_coord):
        """Checks if the given pixel is within the box."""
        return self.box.collidepoint(*pixel_coord)

#
#  ######
#  #     #  ####  #    #
#  #     # #    #  #  #
#  ######  #    #   ##
#  #     # #    #   ##
#  #     # #    #  #  #
#  ######   ####  #    #


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

    def __init__(self, coord=None, text=''):
        """Initialize."""
        self.box_coord = coord
        self.box_x, self.box_y = coord
        self.text = text

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

        If revealed, draw the icon on the card background; otherwise
        draw the card back.

        Arguments:
            display: A pygame.display object.
            force_reveal: If true, will draw the revealed card,
                regardless of the value of self.revealed.
        Returns: None.
        """
        left, top = self.pixel_coord
        if not self.text:
            pygame.draw.rect(
                display.display, display.bg_color, self.box)
            return  # blank tile!

        pygame.draw.rect(
            display.display, self.box_bg_color,
            (left + offset_x, top + offset_y, self.box_size, self.box_size),
        )
        surface = display.font.render(
            self.text, True, self.box_color)  # True = antialias
        rect = surface.get_rect()
        rect.center = (
            left + int(self.box_size / 2) + offset_x,
            top + int(self.box_size / 2) + offset_y,
        )
        display.blit(surface, rect)
        return

    def swap_with(self, box):
        """Swap the boxes."""
        self.text, box.text = box.text, self.text
        return


#
#   #####                       ######
#  #     #   ##   #    # ###### #     #  ####    ##   #####  #####
#  #        #  #  ##  ## #      #     # #    #  #  #  #    # #    #
#  #  #### #    # # ## # #####  ######  #    # #    # #    # #    #
#  #     # ###### #    # #      #     # #    # ###### #####  #    #
#  #     # #    # #    # #      #     # #    # #    # #   #  #    #
#   #####  #    # #    # ###### ######   ####  #    # #    # #####


class SlideBoard(GameBoard):
    """Functionality for a Memory board."""

    def __init__(
        self, display, buttons={},
        n_col=N_COL, n_row=N_ROW,
        box_color=TEXT_COLOR, box_bg_color=TILE_COLOR,
    ):
        """Initialize."""
        super().__init__(display)

        self.buttons = buttons
        self.n_col = n_col
        self.n_row = n_row
        self.box_color = box_color
        self.box_bg_color = box_bg_color

        # set dimensions
        dimensions = self.calc_board_dimensions(display.size)
        for name, value in dimensions.items():
            setattr(self, name, value)

        coord_list = [
            (x, y)
            for y in range(self.n_row)
            for x in range(self.n_col)
        ]
        text_list = [str(i + 1) for i in range(15)] + ['']

        # initialize the board
        GameBox.set_board_data({
            'n_col': self.n_col,
            'n_row': self.n_row,
            'gap_size': self.gap_size,
            'box_size': self.box_size,
            'x_margin': self.x_margin,
            'y_margin': self.y_margin,
            'box_color': self.box_color,
            'box_bg_color': self.box_bg_color,
        })
        self.box_list = [
            GameBox(coord=coord, text=text)
            for coord, text in zip(coord_list, text_list)
        ]
        self.set_tile_lookup()

        # update button dimensions
        # --uses box coords, so do after we've created boxes
        button_right = self.display.width - (self.x_margin / 2)
        button_bottom = self.box_list[-1].box.bottom
        for button in self.buttons:
            log.debug('{} --> {}'.format(button.pixel_coord,
                                         (button_right, button_bottom)))
            button.pixel_coord = (button_right, button_bottom)
            button_bottom = button_bottom - button.height - self.gap_size

        # shuffle
        self.shuffle()

    def calc_board_dimensions(self, screen_size):
        """Calculate margins, box size, and gap size."""
        width, height = screen_size

        # adjust box size to margin
        x_margin = int(width * 0.1)
        y_margin = int(height * 0.1)

        board_w = width - 2 * x_margin
        board_h = height - 2 * y_margin

        box_w = board_w / self.n_col
        box_w_size = int(box_w * 0.96)
        gap_w_size = int(box_w * 0.02)

        box_h = board_h / self.n_row
        box_h_size = int(box_h * 0.96)
        gap_h_size = int(box_h * 0.02)

        box_size = min(box_h_size, box_w_size)
        gap_size = min(gap_h_size, gap_w_size)
        animation_speed = int(box_size / 3)

        return {
            'x_margin': x_margin,
            'y_margin': y_margin,
            'box_size': box_size,
            'gap_size': gap_size,
            'animation_speed': animation_speed,
        }

    def is_valid_move(self, direction):
        blank_x, blank_y = self.text_lookup[''].box_coord

        bad_directions = [
            direction == LEFT and blank_x == (self.n_col - 1),
            direction == RIGHT and blank_x == 0,
            direction == UP and blank_y == (self.n_row - 1),
            direction == DOWN and blank_y == 0,
        ]

        if any(bad_directions):
            return False
        return True

    def set_tile_lookup(self):
        self.text_lookup = {
            box.text: box
            for box in self.box_list
        }
        self.coord_lookup = {
            box.box_coord: text
            for text, box in self.text_lookup.items()
        }
        return

    def is_solved(self):
        solution = list(range(1, self.n_col * self.n_row))
        current_state = [
            int(box.text) for box in self.box_list
            if box.text
        ]
        return solution == current_state

    def reset(self):
        for text, box in zip(self.initial_order, self.box_list):
            box.text = text
        self.set_tile_lookup()

    def shuffle(self):
        text_list = [text for text in self.text_lookup.keys()]
        random.shuffle(text_list)
        for text, box in zip(text_list, self.box_list):
            box.text = text
        self.set_tile_lookup()
        self.initial_order = text_list
        return

    #
    #    ##   #    # # #    #   ##   ##### #  ####  #    #
    #   #  #  ##   # # ##  ##  #  #    #   # #    # ##   #
    #  #    # # #  # # # ## # #    #   #   # #    # # #  #
    #  ###### #  # # # #    # ######   #   # #    # #  # #
    #  #    # #   ## # #    # #    #   #   # #    # #   ##
    #  #    # #    # # #    # #    #   #   #  ####  #    #

    def slide_to_blank(self, direction):
        """Slide the blank tile."""
        # NOTE: left means moving the tile on the right etc.
        blank_x, blank_y = self.text_lookup[''].box_coord

        if not self.is_valid_move(direction):
            return

        move_x, move_y = blank_x, blank_y
        dir_x, dir_y = 0, 0
        if direction == LEFT:
            move_x = blank_x + 1
            dir_x = -1
        if direction == RIGHT:
            move_x = blank_x - 1
            dir_x = +1
        if direction == UP:
            move_y = blank_y + 1
            dir_y = -1
        if direction == DOWN:
            move_y = blank_y - 1
            dir_y = + 1

        move_text = self.coord_lookup[(move_x, move_y)]
        move_tile = self.text_lookup[move_text]

        tmp_blank = GameBox(coord=(move_x, move_y), text='')

        for i in range(0, self.box_size, self.animation_speed):
            tmp_blank.draw(self.display)
            move_tile.draw(
                self.display, offset_x=(dir_x * i), offset_y=(dir_y * i))
            pygame.display.update()
            self.display.tick()

        move_tile.swap_with(self.text_lookup[''])
        self.set_tile_lookup()

        return

    #
    #  ######
    #  #     # #####    ##   #    # # #    #  ####
    #  #     # #    #  #  #  #    # # ##   # #    #
    #  #     # #    # #    # #    # # # #  # #
    #  #     # #####  ###### # ## # # #  # # #  ###
    #  #     # #   #  #    # ##  ## # #   ## #    #
    #  ######  #    # #    # #    # # #    #  ####

    def draw_board(self, msg=None):
        """Draw the board."""
        self.display.fill()
        if msg:
            surface = self.display.font.render(
                msg, True, self.box_bg_color, self.display.bg_color)
            rect = surface.get_rect()
            rect.topright = (
                self.buttons[0].pixel_coord[0],
                self.box_list[0].pixel_coord[1],
            )
            self.display.blit(surface, rect)

        for button in self.buttons:
            button.draw(self.display)
            # log.debug(button.pixel_coord)

        for box in self.box_list:
            box.draw(self.display)

#
#   ####  #    # # #####
#  #    # #    # #   #
#  #    # #    # #   #
#  #  # # #    # #   #
#  #   #  #    # #   #
#   ### #  ####  #   #


def terminate():
    """Stop the game and exit."""
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


def new_game(board):
    board.shuffle()


def reset_game(board):
    board.reset()

#
#  #    #   ##   # #    #
#  ##  ##  #  #  # ##   #
#  # ## # #    # # # #  #
#  #    # ###### # #  # #
#  #    # #    # # #   ##
#  #    # #    # # #    #


def main():
    """Entrypoint."""
    pygame.init()

    log.debug(BG_COLOR)

    display = Display(caption='Slide!')

    buttons = [
        GameButton(
            display, 'New Game', action=new_game,
            coord=(display.width - SIDE_BAR_WIDTH, display.height - 90)
        ),
        GameButton(
            display, 'Reset', action=reset_game,
            coord=(display.width - SIDE_BAR_WIDTH, display.height - 60)
        ),
    ]
    main_board = SlideBoard(display, buttons)
    main_board.shuffle()

    msg = None
    while True:
        slide_to = None

        check_for_quit()  # quit if any quit event found
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mouse_coord = event.pos
                for button in buttons:
                    if button.contains(mouse_coord):
                        button.action(main_board)
                        msg = button.text
            elif event.type == KEYUP:
                if event.key in KEY_UP:
                    slide_to = UP
                elif event.key in KEY_DOWN:
                    slide_to = DOWN
                elif event.key in KEY_LEFT:
                    slide_to = LEFT
                elif event.key in KEY_RIGHT:
                    slide_to = RIGHT

        if slide_to:
            # slide, and if solved, alert the user
            # -- __must__ slide to trigger solved alert!
            main_board.slide_to_blank(slide_to)
            msg = None  # clear current message on move

        msg = 'Solved!' if main_board.is_solved() else msg
        main_board.draw_board(msg)

        pygame.display.update()
        display.tick()


if __name__ == '__main__':
    gamelog.config()
    main()
