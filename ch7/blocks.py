#!/usr/bin/env python3

import logging
import random
import time

import pygame
from gamelib import logging as gamelog
from gamelib import util as gameutil
from gamelib import Display, GameBoard, colors, fonts, sounds
from gamelib.constants import KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_UP
from pieces import BLANK, SHAPES, TEMPLATE_HEIGHT, TEMPLATE_WIDTH
from pygame.locals import K_SPACE, KEYDOWN, KEYUP, K_q

log = logging.getLogger(__name__)

FPS = 15
WIN_WIDTH = 640
WIN_HEIGHT = 480
WIN_CENTER = (int(WIN_WIDTH / 2), int(WIN_HEIGHT / 2))

MOVE_SIDE_FREQ = 0.15
MOVE_DOWN_FREQ = 0.1

BIG_FONT = None
REG_FONT = None

BORDER_COLOR = colors.colorblind_14.blue
BOARD_BG_COLOR = colors.black
BG_COLOR = colors.black
TEXT_COLOR = colors.white
TEXT_SHADOW_COLOR = colors.gray


COLOR_LOOKUP = {
    color: highlight
    for shape, color, highlight in SHAPES.values()
}


def check_for_key_press():
    """Look for KEYUP events and remove KEYDOWN events."""
    gameutil.check_for_quit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def draw_box(display, pixel_coord, color, highlight):
    x, y = pixel_coord
    x, y = x + 1, y + 1
    box_size = TetrisBoard.BOX_SIZE - 1
    pygame.draw.rect(display, color, (x, y, box_size, box_size))
    pygame.draw.rect(display, highlight, (x, y, box_size - 3, box_size - 3))
    return


def get_new_piece():
    pass


def make_text_obj(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def run_game(display):
    board = TetrisBoard(display)

    now = time.time()
    last_move_down_time = now
    last_move_side_time = now
    last_fall_time = now

    move_down = False  # NOTE: no move_up
    move_left = False
    move_right = False

    falling_piece = TetrisPiece()
    next_piece = TetrisPiece()

    while True:  # main game loop
        if not falling_piece:
            # no falling piece in play, so start a new one at the top
            falling_piece = next_piece
            next_piece = TetrisPiece()
            last_fall_time = time.time()  # reset last fall time

            if not board.is_valid_pos(falling_piece):
                return  # can't fit a new piece, so game over

        gameutil.check_for_quit()
        for event in pygame.event.get():  # event handling loop
            if event.type == KEYUP:  # key release
                if event.key == K_SPACE:
                    display.fill(BG_COLOR)
                    pygame.mixer.music.pause()
                    show_text_screen(display, 'Pause')
                    pygame.mixer.music.unpause()

                    now = time.time()
                    last_fall_time = now
                    last_move_down_time = now
                    last_move_side_time = now
                elif event.key in KEY_LEFT:
                    move_left = False
                elif event.key in KEY_RIGHT:
                    move_right = False
                elif event.key in KEY_DOWN:
                    move_down = False

            elif event.type == KEYDOWN:  # key press
                if event.key in KEY_LEFT and \
                        board.is_valid_pos(falling_piece, adj_x=-1):
                    falling_piece.move_left()
                    move_left = True
                    move_right = False
                    last_move_side_time = time.time()
                elif event.key in KEY_RIGHT and \
                        board.is_valid_pos(falling_piece, adj_x=1):
                    falling_piece.move_right()
                    move_left = False
                    move_right = True
                    last_move_side_time = time.time()
                elif event.key in KEY_DOWN:
                    move_down = True
                    if board.is_valid_pos(falling_piece, adj_y=1):
                        falling_piece.move_down()
                    last_move_down_time = time.time()
                elif event.key in KEY_UP:
                    falling_piece.rotate()
                    if not board.is_valid_pos(falling_piece):
                        falling_piece.rotate(-1)
                elif event.key == K_q:
                    falling_piece.rotate(-1)
                    if not board.is_valid_pos(falling_piece):
                        falling_piece.rotate()

        # handle user input--left or right
        move_side = move_left or move_right
        if move_side and time.time() - last_move_side_time > MOVE_SIDE_FREQ:
            if move_left and board.is_valid_pos(falling_piece, adj_x=-1):
                falling_piece.move_left()
            elif move_right and board.is_valid_pos(falling_piece, adj_x=1):
                falling_piece.move_right()
            last_move_side_time = time.time()

        if move_down and time.time() - last_move_down_time > MOVE_DOWN_FREQ \
                and board.is_valid_pos(falling_piece, adj_y=1):
            falling_piece.move_down()
            last_move_down_time = time.time()

        # let the piece fall
        if time.time() - last_fall_time > board.fall_freq:
            if not board.is_valid_pos(falling_piece, adj_y=1):
                # falling piece has landed--add it to the board
                board.add_piece(falling_piece)
                board.remove_completed_lines()
                falling_piece = None
            else:
                # falling piece didn't land yet--move it down
                falling_piece.move_down()
                last_fall_time = time.time()

        board.draw(next_piece)
        if falling_piece:
            falling_piece.draw(display.display)
        # board.draw_next_piece(next_piece)
        display.update()
    return


def show_text_screen(display, text):
    """Display large text in center of screen until key press."""
    x, y = WIN_CENTER
    y = y - (y * 0.2)
    # shadow
    surf, rect = make_text_obj(text, BIG_FONT, TEXT_SHADOW_COLOR)
    rect.center = (x, y)
    display.blit(surf, rect)

    surf, rect = make_text_obj(text, BIG_FONT, TEXT_COLOR)
    rect.center = (x - 3, y - 3)
    offset = rect.height / 2
    display.blit(surf, rect)

    # press a key to play text
    surf, rect = make_text_obj('Press any key to play', REG_FONT, colors.gray)
    rect.center = (x, y + offset + 25)
    display.blit(surf, rect)

    while check_for_key_press() is None:
        display.update()


class TetrisPiece():

    def __init__(self):
        shape = random.choice(list(SHAPES.keys()))
        self.name = shape
        self.shape, self.color, self.highlight = SHAPES[shape]
        self.rotation = random.randint(0, len(self.shape) - 1)

        self.x = int(TetrisBoard.BOARD_W / 2) - int(TEMPLATE_WIDTH / 2)
        self.y = -2

    @property
    def coord(self):
        return (self.x, self.y)

    @coord.setter
    def coord(self, coord):
        self.x, self.y = coord

    def draw(self, display, pixel_coord=None):
        if pixel_coord:
            px, py = pixel_coord
        else:
            px, py = TetrisBoard.convert_to_pixel_coord(*self.coord)
        shape = self.shape[self.rotation]
        for x in range(TEMPLATE_WIDTH):
            for y in range(TEMPLATE_HEIGHT):
                if shape[y][x] != BLANK:
                    _x = px + (x * TetrisBoard.BOX_SIZE)
                    _y = py + (y * TetrisBoard.BOX_SIZE)
                    draw_box(display, (_x, _y), self.color, self.highlight)

    def coord_list(self):
        shape = self.shape[self.rotation]

        for x in range(TEMPLATE_WIDTH):
            for y in range(TEMPLATE_HEIGHT):
                if shape[y][x] != BLANK:
                    yield self.x + x, self.y + y

    def move_down(self):
        self.y = self.y + 1

    def move_left(self):
        self.x = self.x - 1

    def move_right(self):
        self.x = self.x + 1

    def rotate(self, direction=1):
        self.rotation = (self.rotation + direction) % len(self.shape)


class TetrisBoard(GameBoard):

    BOARD_W = 10
    BOARD_H = 20

    X_MARGIN = None
    Y_MARGIN = None

    BOX_SIZE = 20

    LEVEL_COLOR_LIST = [
        colors.black,
        colors.colorblind_14.dark_pink,
        colors.colorblind_14.pink,
        colors.colorblind_14.dark_blue,
        colors.colorblind_14.blue,
        colors.colorblind_14.dark_green,
        colors.colorblind_14.green,
        colors.colorblind_14.yellow,
        colors.colorblind_14.orange,
        colors.colorblind_14.red,
    ]
    BORDER_COLOR_LIST = [
        colors.colorblind_14.light_blue,
        colors.colorblind_14.light_green,
        colors.colorblind_14.light_orange,
        colors.colorblind_14.light_pink,
        colors.white,
    ]

    def __init__(self, display):
        """Initialize gameboard."""
        super().__init__(display)
        self._display = self.display.display

        self.board = self.get_blank_board()
        self.score = 0
        self.level, self.fall_freq = self.calc_level_and_fall(self.score)

        self.board_w_px = self.BOARD_W * self.BOX_SIZE
        self.board_h_px = self.BOARD_H * self.BOX_SIZE

        # margins
        win_w, win_h = self.display.size
        TetrisBoard.X_MARGIN = int(
            (win_w - (self.BOARD_W * self.BOX_SIZE)) / 2)
        TetrisBoard.Y_MARGIN = win_h - (self.BOARD_H * (self.BOX_SIZE + 1)) - \
            (self.BOX_SIZE / 4)

        # board boxes
        self.border_box = pygame.Rect(
            self.X_MARGIN - 3, self.Y_MARGIN - 3,
            self.board_w_px + 8, self.board_h_px + 8,
        )
        self.board_box = pygame.Rect(
            self.X_MARGIN, self.Y_MARGIN, self.board_w_px, self.board_h_px,
        )

        # status loc
        self.gap_size = ((win_w - self.board_box.right) * 0.1)
        self.info_iter = self.BOX_SIZE
        info_x = self.board_box.right + self.gap_size
        info_y = self.board_box.top
        info_w = (win_w - self.board_box.right) - \
            (2 * (info_x - self.board_box.right))
        info_h = self.info_iter * 3
        self.info_box = pygame.Rect(info_x, info_y, info_w, info_h)
        self.info_border = pygame.Rect(
            info_x - 3, info_y - 3,
            info_w + 8, info_h + 8,
        )

        # next box loc
        next_x, next_y = self.info_box.bottomleft
        next_y += self.gap_size
        next_dim = self.BOX_SIZE * 5
        self.next_box = pygame.Rect(next_x, next_y, next_dim, next_dim)
        self.next_border = pygame.Rect(
            next_x - 3, next_y - 3, next_dim + 8, next_dim + 8)

        self.board = self.get_blank_board()

    @staticmethod
    def calc_level_and_fall(score):
        level = int(score / 100) + 1
        fall_freq = 0.27 - (level * 0.02)
        return level, fall_freq

    @classmethod
    def convert_to_pixel_coord(cls, x, y):
        return (
            cls.X_MARGIN + (x * cls.BOX_SIZE),
            cls.Y_MARGIN + (y * cls.BOX_SIZE),
        )

    def add_piece(self, piece):
        for x, y in piece.coord_list():
            self.board[y][x] = piece.color

    def draw(self, next_piece=None):
        lc_idx = (self.level - 1) % len(self.LEVEL_COLOR_LIST)
        bc_idx = int(self.level / len(self.LEVEL_COLOR_LIST)) % \
            len(self.BORDER_COLOR_LIST)
        level_color = self.LEVEL_COLOR_LIST[lc_idx]
        border_color = self.BORDER_COLOR_LIST[bc_idx]

        self.display.fill(level_color)

        self.draw_board(border_color=border_color)
        self.draw_status(border_color=border_color)
        self.draw_next_piece(next_piece, border_color=border_color)
        return

    def draw_board(self, border_color=BORDER_COLOR):
        """Draw the tetris board."""
        # draw the border and fill it
        pygame.draw.rect(self._display, border_color, self.border_box, 5)
        pygame.draw.rect(self._display, BOARD_BG_COLOR, self.board_box)

        # draw the board
        for x in range(self.BOARD_W):
            for y in range(self.BOARD_H):
                if self.board[y][x] != BLANK:
                    pcoord = self.convert_to_pixel_coord(x, y)
                    draw_box(
                        self._display, pcoord,
                        self.board[y][x], COLOR_LOOKUP[self.board[y][x]],
                    )
        return

    def draw_next_piece(self, piece, border_color=BORDER_COLOR):
        # draw the border and fill it
        pygame.draw.rect(self._display, border_color, self.next_border, 5)
        pygame.draw.rect(self._display, BOARD_BG_COLOR, self.next_box)

        if piece:
            piece.draw(self._display, pixel_coord=self.next_box.topleft)

    def draw_status(self, border_color=BORDER_COLOR):
        # draw the border and fill it
        pygame.draw.rect(self._display, border_color, self.info_border, 5)
        pygame.draw.rect(self._display, BOARD_BG_COLOR, self.info_box)

        text_list = [
            'Score: {}'.format(self.score),
            'Level: {}'.format(self.level),
        ]
        x, y = self.info_box.topleft
        for i, text in enumerate(text_list):
            surf = REG_FONT.render(text, True, TEXT_COLOR)
            rect = surf.get_rect()
            rect.topleft = (x + 5, y + (i * self.info_iter))
            self.display.blit(surf, rect)
        pass

    def flash_lines(self, y_list):
        self.draw()
        for y in y_list:
            for x in range(self.BOARD_W):
                pixel_coord = self.convert_to_pixel_coord(x, y)
                draw_box(
                    self._display, pixel_coord, colors.light_gray, colors.gray)
        self.display.update()
        for y in y_list:
            for x in range(self.BOARD_W):
                pixel_coord = self.convert_to_pixel_coord(x, y)
                draw_box(
                    self._display, pixel_coord, colors.black, colors.dark_gray)
        self.display.update()
        return

    def get_blank_board(self):
        board = []
        for x in range(self.BOARD_H):
            board.append([BLANK] * self.BOARD_W)
        return board

    def is_line_complete(self, y):
        """Return True if none of the boxes are blank."""
        for x in range(self.BOARD_W):
            if self.board[y][x] == BLANK:
                return False
        return True

    def is_on_board(self, x, y):
        return x >= 0 and x < self.BOARD_W and y < self.BOARD_H

    def is_valid_pos(self, piece, adj_x=0, adj_y=0):
        """Return True if the piece is within the board and not colliding."""
        for x, y in piece.coord_list():
            x = x + adj_x
            y = y + adj_y
            if y < 0:
                continue  # above the board
            if not self.is_on_board(x, y):
                return False
            if self.board[y][x] != BLANK:
                return False
        return True

    def remove_completed_lines(self):
        rm_list = []
        for y in range(self.BOARD_H, 0, -1):
            y = y - 1
            if self.is_line_complete(y):
                rm_list.append(y)

        if not rm_list:
            return

        # flash lines
        self.flash_lines(rm_list)

        # remove lines
        new_lines = []
        for rm_y in rm_list:
            del self.board[rm_y]
            new_lines.append([BLANK] * self.BOARD_W)

        # calculate the score
        # -- add a bonus for extra lines
        n_lines = len(rm_list)
        base_score = int(n_lines * 10)
        bonus_score = int(0.1 * (n_lines - 1) * base_score)
        super_bonus = int(0.15 * max(0, n_lines - 3) * base_score)
        self.score += base_score + bonus_score + super_bonus

        # add new lines and update score
        self.board = new_lines + self.board
        self.level, self.fall_freq = self.calc_level_and_fall(self.score)
        return


def main():
    global BIG_FONT, REG_FONT
    pygame.init()
    BIG_FONT = pygame.font.Font(fonts.open_sans, 100)
    REG_FONT = pygame.font.Font(fonts.open_sans, 18)
    display = Display(
        fps=FPS, win_width=WIN_WIDTH, win_height=WIN_HEIGHT,
        caption='Tetris',
    )

    show_text_screen(display, display.caption)
    while True:  # game loop
        if random.randint(0, 1) == 0:
            pygame.mixer.music.load(sounds.tetris_b)
        else:
            pygame.mixer.music.load(sounds.tetris_c)
        pygame.mixer.music.play(-1, 0.0)  # loop indefinitely
        run_game(display)
        pygame.mixer.music.stop()
        show_text_screen(display, 'Game Over')


if __name__ == '__main__':
    gamelog.config()
    main()
