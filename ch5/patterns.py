#!/usr/bin/env python3
"""Implementation of Simon using pygame."""

import logging
import random
import time

import pygame
from gamelib import logging as gamelog
from gamelib import util as gameutil
from gamelib import Display, GameBoard, GameBox, colors, sounds
from pygame.locals import (K_PERIOD, K_SEMICOLON, K_SLASH, KEYUP,
                           MOUSEBUTTONUP, K_a, K_l, K_q, K_s, K_w)

log = logging.getLogger(__name__)


FLASHDELAY = 200
FLASHSPEED = 500


class StopInput(Exception):
    pass  # use this exception when the input is fully matched


class SimonBox(GameBox):

    def __init__(self, name=None, sound=None, highlight=None, **kwargs):
        """Initialize Simon box."""
        super().__init__(**kwargs)
        self.name = name
        self.highlight_color = highlight

        if isinstance(sound, str):
            self.sound = pygame.mixer.Sound(sound)
        else:
            self.sound = sound


class SimonBoard(GameBoard):
    """A game board for playing Simon."""

    def __init__(self, display):
        """Initialize gameboard."""
        super().__init__(display)
        box_layout = (2, 2)
        self.n_col, self.n_row = box_layout
        self.score = 0

        # set dimensions
        dimensions = self.calc_board_dimensions(
            display.size, box_layout, gap_size=0.1)
        for name, value in dimensions.items():
            setattr(self, name, value)

        # initialize the board
        GameBox.set_board_data({
            'n_col': self.n_col,
            'n_row': self.n_row,
            'gap_size': self.gap_size,
            'box_size': self.box_size,
            'x_margin': self.x_margin,
            'y_margin': self.y_margin,
            # 'box_color': self.box_color,
            # 'box_bg_color': self.box_bg_color,
        })

        # define boxes
        color_list = [
            ('red', (155, 0, 0), (255, 0, 0)),
            ('blue', (0, 0, 155), (0, 0, 255)),
            ('green', (0, 155, 0), (0, 255, 0)),
            ('yellow', (155, 155, 0), (255, 255, 0))
        ]
        sound_list = [sounds.beep1, sounds.beep2, sounds.beep3, sounds.beep4]
        coord_list = [
            (x, y)
            for y in range(self.n_row)
            for x in range(self.n_col)
        ]
        self.box_list = [
            SimonBox(
                coord=coord, name=name,
                color=color, highlight=bright,
                sound=sound,
            )
            for coord, (name, color, bright), sound in zip(
                coord_list, color_list, sound_list)
        ]
        self.box_dict = {
            box.name: box
            for box in self.box_list
        }
        self.box_order = [name for name, _, _ in color_list]

        # define buttons
        self.button_list = []
        self.pattern = []
        self.match = []

    def get_button_typed(self, key):
        mappings = [
            (K_q, K_l),
            (K_w, K_SEMICOLON),
            (K_a, K_PERIOD),
            (K_s, K_SLASH),
        ]
        for i, mapping in enumerate(mappings):
            if key in mapping:
                return self.box_dict[self.box_order[i]]
        return None

    def flash_button_animation(self, box):
        """Flash a single button."""
        orig_surface = self.display.display.copy()
        flash_surface = pygame.Surface((self.box_size, self.box_size))
        flash_surface = flash_surface.convert_alpha()
        try:
            r, g, b, _ = box.highlight_color  # w/ alpha
        except:
            r, g, b = box.highlight_color  # w/ alpha

        # loop over the range
        box.sound.play()
        for beg, end, step in ((0, 255, 1), (255, 0, -1)):
            for alpha in range(beg, end, self.animation_speed * step):
                gameutil.check_for_quit()
                self.display.blit(orig_surface, (0, 0))
                flash_surface.fill((r, g, b, alpha))
                # flash_surface.set_alpha(alpha)
                self.display.blit(flash_surface, box.pixel_coord)
                self.display.update()
        self.display.blit(orig_surface, (0, 0))
        return

    def animate_pattern(self):
        """Extend the pattern and animate."""
        next_box = random.choice(self.box_order)
        self.pattern.append(next_box)
        pygame.time.wait(1000)
        for name in self.pattern:
            self.flash_button_animation(self.box_dict[name])
            pygame.time.wait(FLASHDELAY)

    def game_over_animation(self):
        """End the game."""
        orig_surface = self.display.display.copy()
        flash_surface = pygame.Surface(self.display.display.get_size())
        flash_surface = flash_surface.convert_alpha()
        sound = pygame.mixer.Sound(sounds.fail)
        sound.play()
        try:
            r, g, b, _ = colors.black  # w/ alpha
        except:
            r, g, b = colors.black  # w/ alpha
        for start, end, step in ((0, 255, 1), (255, 0, -1)):
            for alpha in range(start, end, self.animation_speed * step):
                gameutil.check_for_quit()
                flash_surface.fill((r, g, b, alpha))
                self.display.blit(orig_surface, (0, 0))
                self.display.blit(flash_surface, (0, 0))
                self.draw_boxes()
                self.display.update()
        return

    def check_input(self, box):
        """Check if the input matches."""
        self.match.append(box.name)
        # log.debug('{}\n{}\n{}\n{}'.format(
        #     self.pattern, self.match,
        #     list(zip(self.match, self.pattern)),
        #     all(x == y for x, y in zip(self.match, self.pattern)),
        # ))
        matched = False
        if all(x == y for x, y in zip(self.match, self.pattern)):
            matched = True  # limit check by smallest number of elements
        if matched and len(self.match) == len(self.pattern):
            self.match = []
            self.score = self.score + 1
            raise StopInput()
        return matched

    def draw(self):
        """Draw the board."""
        msg = 'Score: {}'.format(self.score)
        return super().draw(msg=msg)

    def reset(self):
        self.pattern = []
        self.score = 0
        self.match = []


def main():
    """Entrypoint."""
    pygame.init()

    display = Display(caption='Simon!', bg_color=colors.dark_gray)
    main_board = SimonBoard(display)
    main_board.animation_speed = 60
    main_board.fg_color = colors.black

    waiting_for_input = False
    last_click_time = time.time()
    timeout = 4

    # main_board.draw()

    while True:  # main game loop
        main_board.draw()
        clicked_button = None

        gameutil.check_for_quit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                clicked_button = main_board.get_button_clicked(event.pos)

            elif event.type == KEYUP:
                clicked_button = main_board.get_button_typed(event.key)

        curr_time = time.time()
        if time.time() - timeout > last_click_time:
            log.debug('timeout: {} -> {} ({})'.format(
                curr_time, last_click_time, timeout))
            main_board.game_over_animation()
            pygame.time.wait(1000)

        if not waiting_for_input:
            # draw the pattern
            main_board.animate_pattern()
            last_click_time = time.time()
            waiting_for_input = True

        else:
            # let the user input the pattern
            if clicked_button:
                last_click_time = time.time()

                main_board.flash_button_animation(clicked_button)

                try:
                    matched = main_board.check_input(clicked_button)
                except StopInput:
                    # pattern matched!
                    waiting_for_input = False
                else:
                    # not finished with the pattern
                    if matched:
                        pass
                    else:
                        main_board.game_over_animation()
                        main_board.reset()
                        waiting_for_input = False

        pygame.display.update()
        display.tick()


if __name__ == '__main__':
    gamelog.config()
    main()
