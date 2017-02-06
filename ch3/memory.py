#!/usr/bin/env python3
"""A simple memory game.

Based on memorypuzzle by Al Sweigart
"""

import logging
import random
import sys

import pygame
from gamelib import colors, icons, sounds
from pygame.locals import K_ESCAPE, KEYUP, MOUSEBUTTONUP, MOUSEMOTION, QUIT

log = logging.getLogger(__name__)

# static variables
FPS = 30
WIN_WIDTH = 640
WIN_HEIGHT = 480
REVEAL_SPEED = 8
BOX_SIZE = 40
GAP_SIZE = 10
N_COL = 6
N_ROW = 4
DISPLAY = None

# colors
BG_COLOR = colors.light_gray
BG_COLOR_LIGHT = colors.gray
BOX_COLOR = colors.dark_gray
BOX_BG_COLOR = colors.white
HIGHLIGHT_COLOR = colors.blue


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
        self.display.fill(self.bg_color)

    def fill(self, color=None):
        """Fill in the background."""
        color = color if color else self.bg_color
        self.display.fill(color)

    def tick(self):
        self.fps_clock.tick(self.fps)


#
#   #####                       ######
#  #     #   ##   #    # ###### #     #  ####  #    #
#  #        #  #  ##  ## #      #     # #    #  #  #
#  #  #### #    # # ## # #####  ######  #    #   ##
#  #     # ###### #    # #      #     # #    #   ##
#  #     # #    # #    # #      #     # #    #  #  #
#   #####  #    # #    # ###### ######   ####  #    #

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

    def __init__(self, coord, icon):
        """Initialize the box."""
        self.box_coord = coord
        self.box_x, self.box_y = coord
        self.icon = icon
        self.shape, self.color = icon
        self.revealed = False

        self.pixel_coord = self.upper_left_coord_of_box(*coord)
        self.pixel_x, self.pixel_y = self.pixel_coord

        self.box = pygame.Rect(
            self.pixel_x, self.pixel_y, self.box_size, self.box_size)

    def __eq__(self, box):
        """Compare the shape and color of the icon."""
        if self.icon == box.icon:
            return True
        return False

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

    def draw(self, display, force_reveal=False):
        """Draw ourselves.

        If revealed, draw the icon on the card background; otherwise
        draw the card back.

        Arguments:
            display: A pygame.display object.
            force_reveal: If true, will draw the revealed card,
                regardless of the value of self.revealed.
        Returns: None.
        """
        if self.revealed or force_reveal:
            # draw the icon
            pygame.draw.rect(display, self.box_bg_color, self.box)
            icons.draw(
                display, self.shape, self.pixel_coord, self.box_size,
                color=self.color, bg_color=self.box_bg_color,
            )
        else:
            # just draw the rectangle
            pygame.draw.rect(display, self.box_color, self.box)


#
#   #####                       ######
#  #     #   ##   #    # ###### #     #  ####    ##   #####  #####
#  #        #  #  ##  ## #      #     # #    #  #  #  #    # #    #
#  #  #### #    # # ## # #####  ######  #    # #    # #    # #    #
#  #     # ###### #    # #      #     # #    # ###### #####  #    #
#  #     # #    # #    # #      #     # #    # #    # #   #  #    #
#   #####  #    # #    # ###### ######   ####  #    # #    # #####


class GameBoard():
    """Functionality for a Memory board."""

    SHAPES = (
        'diamond',
        'donut',
        'lines',
        'oval',
        'square',
    )
    COLORS = (
        colors.colorblind.red,
        colors.colorblind.green,
        colors.colorblind.dark_blue,
        colors.colorblind.yellow,
        colors.colorblind.orange,
        colors.colorblind.dark_pink,
        colors.colorblind.light_blue,
    )

    def __init__(
            self, display, n_col=N_COL, n_row=N_ROW,
            box_size=BOX_SIZE, gap_size=GAP_SIZE,
            box_color=BOX_COLOR, box_bg_color=BOX_BG_COLOR,
            highlight_color=HIGHLIGHT_COLOR,
            reveal_speed=REVEAL_SPEED,
    ):
        """Initialize the game board."""
        self.display_obj = display
        self.display = display.display

        # validate variables
        if (n_col * n_row) % 2 != 0:
            dim = n_col * n_row
            log.error('{} * {} = {}'.format(n_col, n_row, dim))
            log.error('{} % 2 = {}'.format(dim, dim % 2))
            raise ValueError('Must have even number of boxes.')
        if len(self.COLORS) * len(self.SHAPES) * 2 < n_col * n_row:
            msg = 'Not enough color and shape combos for given board size'
            raise ValueError(msg)

        width, height = self.display_obj.size

        # adjust box size to margin
        x_margin = int(width * 0.1)
        y_margin = int(height * 0.1)

        board_w = width - 2 * x_margin
        board_h = height - 2 * y_margin

        box_w = board_w / n_col
        box_w_size = int(box_w * 0.8)
        gap_w_size = int(box_w * 0.2)

        box_h = board_h / n_row
        box_h_size = int(box_h * 0.8)
        gap_h_size = int(box_h * 0.2)

        box_size = min(box_h_size, box_w_size)
        gap_size = min(gap_h_size, gap_w_size)
        reveal_speed = int(box_size / 5)

        # store given vars
        self.n_col = n_col
        self.n_row = n_row
        self.box_size = box_size
        self.gap_size = gap_size
        self.reveal_speed = reveal_speed
        self.box_color = box_color
        self.box_bg_color = box_bg_color
        self.highlight_color = highlight_color

        # calculate margins
        self.x_margin = int((width - (n_col * (box_size + gap_size))) / 2)
        self.y_margin = int((height - (n_row * (box_size + gap_size))) / 2)

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
        self.board = self.get_randomized_board(self.n_col, self.n_row)

    @classmethod
    def get_randomized_board(cls, n_col, n_row):
        """Get a dictionary of GameBox items, with random shapes and colors.

        Arguments:
            n_col, n_row: The dimensions of the board.
        Return:
            A dict with of GameBox objects, {coord: box}.
        """
        icons = [
            (shape, color)
            for color in cls.COLORS
            for shape in cls.SHAPES
        ]
        random.shuffle(icons)  # shake up the order
        n_used = int(n_col * n_row / 2)
        icons = icons[:n_used] * 2
        random.shuffle(icons)

        # create the board structure
        coord = [(x, y) for x in range(n_col) for y in range(n_row)]
        board = {
            coord: GameBox(coord, icon)
            for coord, icon in zip(coord, icons)
        }
        return board

    def get_box_at_pixel(self, pixel_coord):
        """Find the box that contains the given pixel_coord."

        Arguments:
            pixel_coord: Pixel coordinates, e.g., mouse position.
        Return:
            The box that contains the pixel; None if pixe isn't in a box.
        """
        box_list = [
            box for box in self.board.values()
            if box.contains(pixel_coord)
        ]
        if box_list:
            return box_list[0]
        else:
            return None

    def has_won(self):
        """Check if the player has won, e.g., all boxes revealed."""
        return all(box.revealed for box in self.board.values())

    #
    #    ##   #    # # #    #   ##   ##### #  ####  #    #
    #   #  #  ##   # # ##  ##  #  #    #   # #    # ##   #
    #  #    # # #  # # # ## # #    #   #   # #    # # #  #
    #  ###### #  # # # #    # ######   #   # #    # #  # #
    #  #    # #   ## # #    # #    #   #   # #    # #   ##
    #  #    # #    # # #    # #    #   #   #  ####  #    #

    def start_game_animation(self):
        """Randomly reveal boxes (n_col at a time) at game start."""
        boxes = list(self.board.values())
        random.shuffle(boxes)
        box_groups = [boxes[i::self.n_row] for i in range(self.n_row)]

        self.draw_board()
        for box_group in box_groups:
            self.reveal_boxes_animation(box_group)
            self.cover_boxes_animation(box_group)

    def reveal_boxes_animation(self, boxes_to_reveal):
        """Animate the box revealing.

        Arguments: A list of box objects.
        Returns: None.
        """
        cov_list = range(
            self.box_size,
            (-1 * self.reveal_speed) - 1,
            -1 * self.reveal_speed,
        )
        for coverage in cov_list:
            self.draw_box_covers(boxes_to_reveal, coverage)
        return

    def cover_boxes_animation(self, boxes_to_cover):
        """Animate the box covering.

        Arguments: A list of box objects.
        Returns: None.
        """
        cov_list = range(
            0, self.box_size + self.reveal_speed, self.reveal_speed)
        for coverage in cov_list:
            self.draw_box_covers(boxes_to_cover, coverage)
        return

    def game_won_animation(self):
        """Flash the background color when the player has won."""
        color1 = self.display_obj.bg_color
        color2 = self.display_obj.bg_color_light

        for i in range(4):
            color1, color2 = color2, color1
            self.display.fill(color1)
            self.draw_board()
            pygame.display.update()
            pygame.time.wait(300)
        return

    #
    #  ######
    #  #     # #####    ##   #    # # #    #  ####
    #  #     # #    #  #  #  #    # # ##   # #    #
    #  #     # #    # #    # #    # # # #  # #
    #  #     # #####  ###### # ## # # #  # # #  ###
    #  #     # #   #  #    # ##  ## # #   ## #    #
    #  ######  #    # #    # #    # # #    #  ####

    def draw_box_covers(self, boxes, coverage):
        """Draw boxes being covered/revealed.

        Draw a single frame for the animation of covering and
        revealing boxes.

        Arguments:
            boxes: The list of boxes to cover/reveal.
            coverage: Portion of box to cover.
        Returns: None.
        """
        coverage = min(coverage, self.box_size)
        for box in boxes:
            left, top = box.pixel_coord

            # draw the card and it's icon
            box.draw(self.display, force_reveal=True)

            if coverage > 0:  # huh?
                pygame.draw.rect(
                    self.display, self.box_color,
                    (left, top, coverage, self.box_size),
                )
        pygame.display.update()
        self.display_obj.tick()
        return

    def draw_board(self):
        """Draws all boxes in their covered or reavealed state."""
        for box_coord, box in sorted(self.board.items()):
            box.draw(self.display)
        return

    def draw_box_highlight(self, box):
        """Draw a highlight around the given box.

        Arguments: The box to highlight.
        Returns: None.
        """
        left, top = box.pixel_coord
        pygame.draw.rect(
            self.display, self.highlight_color,
            (left - 5, top - 5, self.box_size + 10, self.box_size + 10), 4)
        return

#
#  #    #   ##   # #    #
#  ##  ##  #  #  # ##   #
#  # ## # #    # # # #  #
#  #    # ###### # #  # #
#  #    # #    # # #   ##
#  #    # #    # # #    #


def main():
    """Entrypoint."""
    global FPSCLOCK, DIPLAY, PIXEL_LOOKUP
    pygame.init()
    display_obj = Display(caption='Memory!')
    main_board = None
    match_sound = pygame.mixer.Sound(sounds.pickup)
    first_sound = pygame.mixer.Sound(sounds.beep2)
    second_sound = pygame.mixer.Sound(sounds.beep4)

    mouse_coord = (0, 0)
    first_box = None  # store the (x, y) coord of the first box clicked

    while True:  # main game board
        mouse_clicked = False

        if main_board:
            # clear the board (remove highlights)
            display_obj.fill()
            main_board.draw_board()

        # event handling loop
        for event in pygame.event.get():
            if event.type == QUIT or \
                    (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mouse_coord = event.pos
            elif event.type == MOUSEBUTTONUP:
                mouse_coord = event.pos
                mouse_clicked = True

        if not main_board:
            # get a new board
            # NOTE: we must wait until after checking events to run
            #   the start animation, otherwise the first one won't happen
            main_board = GameBoard(display_obj)
            main_board.draw_board()

            pygame.display.update()
            pygame.time.wait(1000)

            main_board.start_game_animation()
            mouse_coord = (-1, -1)

        # box_coord = PIXEL_LOOKUP[mouse_coord]
        box = main_board.get_box_at_pixel(mouse_coord)
        if box:
            if not box.revealed:
                # simple mouse over
                main_board.draw_box_highlight(box)

            if not box.revealed and mouse_clicked:
                # reveal the box!
                main_board.reveal_boxes_animation([box])
                box.revealed = True

                if first_box is None:
                    # first choice -- keep it open
                    first_sound.play()
                    first_box = box
                else:
                    # second choice -- check it and close if different
                    if box != first_box:
                        # icon's don't match
                        # -- play a sound then cover the two boxes
                        second_sound.play()
                        pygame.time.wait(100)
                        main_board.cover_boxes_animation([first_box, box])
                        first_box.revealed = False
                        box.revealed = False
                    elif main_board.has_won():
                        # all boxes matched -- flash screen and reload
                        main_board.game_won_animation()
                        main_board = None
                        pygame.time.wait(1000)
                    else:
                        match_sound.play()

                    first_box = None  # done handling the choices

        # redraw the screen
        pygame.display.update()
        display_obj.tick()


if __name__ == '__main__':
    main()
