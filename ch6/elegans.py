#!/usr/bin/env python3

import logging
import random
import sys

import pygame
from gamelib import logging as gamelog
from gamelib import util as gameutil
from gamelib import Display, colors, fonts
from gamelib.constants import (DOWN, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_UP,
                               LEFT, RIGHT, UP)
from pygame.locals import K_ESCAPE, K_SPACE, KEYDOWN, KEYUP, QUIT

log = logging.getLogger(__name__)

FPS = 15
WIN_WIDTH = 640
WIN_HEIGHT = 480
CELL_SIZE = 20

assert WIN_WIDTH % CELL_SIZE == 0, \
    "Window width must be a multiple of cell size."
assert WIN_HEIGHT % CELL_SIZE == 0, \
    "Window height must be a multiple of cell size."

HEAD = 0  # index of worm's head

CELL_WIDTH = int(WIN_WIDTH / CELL_SIZE)
CELL_HEIGHT = int(WIN_HEIGHT / CELL_SIZE)

BG_COLOR = colors.black


def check_for_key_press():
    for event in pygame.event.get(QUIT):
        gameutil.terminate()  # any quit event exits
    key_up_list = pygame.event.get(KEYUP)
    if len(key_up_list) == 0:
        return None
    if key_up_list[0].key == K_ESCAPE:
        gameutil.terminate()
    return key_up_list[0].key


def draw_apple(display, coord):
    x = coord['x'] * CELL_SIZE
    y = coord['y'] * CELL_SIZE
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(display.display, colors.red, rect)
    return


def draw_grid(display):
    for x in range(0, WIN_WIDTH, CELL_SIZE):  # draw vertical lines
        pygame.draw.line(
            display.display, colors.dark_gray, (x, 0), (x, WIN_HEIGHT))
    for y in range(0, WIN_HEIGHT, CELL_SIZE):  # draw vertical lines
        pygame.draw.line(
            display.display, colors.dark_gray, (0, y), (WIN_WIDTH, y))
    return


def draw_pause(display):
    font = pygame.font.Font(fonts.open_sans, 50)
    surf = font.render('PAUSE', True, colors.light_gray)
    rect = surf.get_rect()
    rect.center = (WIN_WIDTH / 2, WIN_HEIGHT * 0.3)
    display.blit(surf, rect)
    return


def draw_press_key_msg(display):
    press_key_surf = display.font.render(
        'Press any key to play.', True, colors.gray)
    press_key_rect = press_key_surf.get_rect()
    press_key_rect.topleft = (display.width - 200,
                              display.height - 100)
    display.blit(press_key_surf, press_key_rect)
    return


def draw_score(display, score):
    surf = display.font.render('Score: {}'.format(score), True, colors.white)
    rect = surf.get_rect()
    rect.topleft = (WIN_WIDTH - 120, 10)
    display.blit(surf, rect)
    return


def get_random_loc():
    return {
        'x': random.randint(0, CELL_WIDTH - 1),
        'y': random.randint(0, CELL_HEIGHT - 1),
    }


def run_game(display):
    # random start coordinates
    direction = RIGHT

    # start the apple in a random place
    worm = Elegans()
    apple = get_random_loc()

    pause = False
    pause_direction = None

    while True:  # main game loop
        for event in pygame.event.get():
            if event.type == QUIT:
                gameutil.terminate()
            elif event.type == KEYDOWN:
                if event.key in KEY_LEFT:
                    direction = LEFT
                elif event.key in KEY_RIGHT:
                    direction = RIGHT
                elif event.key in KEY_UP:
                    direction = UP
                elif event.key in KEY_DOWN:
                    direction = DOWN
                elif event.key == K_SPACE:
                    pause = not pause
                    if pause:  # maintain same direction as before
                        pause_direction = direction
                    else:
                        direction = pause_direction
                elif event.key == K_ESCAPE:
                    gameutil.terminate()

        if pause:
            display.fill(BG_COLOR)
            draw_grid(display)
            worm.draw(display)
            # draw_apple(display, apple)
            draw_score(display, worm.length - 3)
            draw_pause(display)
            display.update()
            continue

        # check if the head has collided with itself or the edge
        if worm.has_edge_collision() or worm.has_self_collision():
            return  # game over

        # check if apple has been eaten, shorten if it has
        if worm.coord[HEAD] == apple:
            apple = get_random_loc()  # move apple (and don't shrink!)
        else:
            worm.shrink()

        worm.move(direction)

        display.fill(BG_COLOR)
        draw_grid(display)
        worm.draw(display)
        draw_apple(display, apple)
        draw_score(display, worm.length - 3)
        display.update()
    return


def show_game_over_screen(display):
    font = pygame.font.Font(fonts.open_sans, 150)
    text_list = [('GAME', -1), ('OVER', 1)]
    for text, direction in text_list:
        surf = font.render(text, True, colors.white)
        rect = surf.get_rect()
        offset = direction * (rect.height / 4)
        rect.center = (WIN_WIDTH / 2, WIN_HEIGHT / 2 + offset)
        display.blit(surf, rect)

    draw_press_key_msg(display)
    display.update()
    pygame.time.wait(500)
    check_for_key_press()  # clear keypresses in event queue

    while True:
        if check_for_key_press():
            pygame.event.get()  # clear event queue
            return
    return


def show_start_screen(display):
    title_font = pygame.font.Font(fonts.open_sans, 100)

    title_surf_list = [
        title_font.render('elegans!', True, *text_colors)
        for text_colors in (
            (colors.colorblind_14.dark_blue, ),
            (colors.colorblind_14.blue, ),
        )
    ]

    degree_list = [0, 0]
    rotate_list = [3, -7]
    while True:
        display.fill(BG_COLOR)

        for title, deg, rot in zip(title_surf_list, degree_list, rotate_list):
            rot_surf = pygame.transform.rotate(title, deg)
            rot_rect = rot_surf.get_rect()
            rot_rect.center = (display.width / 2, display.height / 2)
            display.blit(rot_surf, rot_rect)

        draw_press_key_msg(display)

        if check_for_key_press():
            pygame.event.get()  # clear event queue
            return

        display.update()

        degree_list = [x + y for x, y in zip(degree_list, rotate_list)]


class Elegans():

    def __init__(self):
        start_x = random.randint(5, CELL_WIDTH - 6)
        start_y = random.randint(5, CELL_HEIGHT - 6)
        self.coord = [
            {'x': start_x, 'y': start_y},
            {'x': start_x - 1, 'y': start_y},
            {'x': start_x - 2, 'y': start_y},
        ]
        self.head = 0

        self.dir_change_table = {
            UP: {'x': 0, 'y': -1},
            DOWN: {'x': 0, 'y': 1},
            LEFT: {'x': -1, 'y': 0},
            RIGHT: {'x': 1, 'y': 0},
        }

    @property
    def length(self):
        return len(self.coord)

    def draw(self, display):
        margin = int(CELL_SIZE / 5)
        inner_size = CELL_SIZE - (margin * 2)
        for coord in self.coord:
            x, y = [coord[k] * CELL_SIZE for k in ('x', 'y')]
            outer_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            inner_rect = pygame.Rect(
                x + margin, y + margin, inner_size, inner_size)
            pygame.draw.rect(
                display.display, colors.colorblind_14.dark_blue, outer_rect)
            pygame.draw.rect(
                display.display, colors.colorblind_14.blue, inner_rect)
        return

    def has_edge_collision(self):
        x_collision = (-1, CELL_WIDTH)
        y_collision = (-1, CELL_HEIGHT)
        if self.coord[HEAD]['x'] in x_collision:
            return True
        elif self.coord[HEAD]['y'] in y_collision:
            return True
        return False

    def has_self_collision(self):
        if self.coord[HEAD] in self.coord[1:]:
            return True
        return False

    def move(self, direction):
        new_coord = {
            k: v + self.dir_change_table[direction][k]
            for k, v in self.coord[HEAD].items()
        }
        self.coord.insert(0, new_coord)
        return

    def shrink(self):
        self.coord.pop(-1)
        return


def main():
    global FPS
    pygame.init()
    display = Display(
        fps=FPS, win_width=WIN_WIDTH, win_height=WIN_HEIGHT,
        caption='C. elegans',
    )

    show_start_screen(display)
    while True:
        run_game(display)
        show_game_over_screen(display)


if __name__ == '__main__':
    gamelog.config()
    main()
