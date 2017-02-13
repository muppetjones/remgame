#!/usr/bin/env python3
"""Basic game board."""


class GameBoard():
    """A simple game board."""

    def __init__(self, display):
        """Initialize the game board."""
        self.display = display

    # @classmethod
    def calc_board_dimensions(
            self, screen_size, box_arrangement, gap_size=0.02):
        """Calculate margins, box size, and gap size."""
        width, height = screen_size
        n_col, n_row = box_arrangement
        box_size = 1 - gap_size

        # adjust box size to margin
        x_margin = int(width * 0.1)
        y_margin = int(height * 0.1)

        board_w = width - 2 * x_margin
        board_h = height - 2 * y_margin

        box_w = board_w / n_col
        box_w_size = int(box_w * box_size)
        gap_w_size = int(box_w * gap_size)

        box_h = board_h / n_row
        box_h_size = int(box_h * box_size)
        gap_h_size = int(box_h * gap_size)

        box_size = min(box_h_size, box_w_size)
        gap_size = min(gap_h_size, gap_w_size)
        animation_speed = int(box_size / 3)

        self.board_w = board_w
        self.board_h = board_h

        return {
            'x_margin': x_margin,
            'y_margin': y_margin,
            'width': board_w,
            'height': board_h,
            'box_size': box_size,
            'gap_size': gap_size,
            'animation_speed': animation_speed,
        }

    def get_button_clicked(self, mouse_coord):
        """Determine which button was clicked."""
        for box in self.box_list:
            if box.contains(mouse_coord):
                return box
        for button in self.button_list:
            if button.contains(mouse_coord):
                return button

    #
    #  ######
    #  #     # #####    ##   #    # # #    #  ####
    #  #     # #    #  #  #  #    # # ##   # #    #
    #  #     # #    # #    # #    # # # #  # #
    #  #     # #####  ###### # ## # # #  # # #  ###
    #  #     # #   #  #    # ##  ## # #   ## #    #
    #  ######  #    # #    # #    # # #    #  ####

    def draw(self, msg=None):
        """Draw the board."""
        self.display.fill()
        if msg:
            surface = self.display.font.render(
                msg, True, self.fg_color, self.display.bg_color)
            rect = surface.get_rect()
            left = (self.x_margin * 2) + (self.box_size * self.n_col) + \
                (self.gap_size * (self.n_col + 1))
            rect.topright = (
                left,
                self.y_margin,
            )
            self.display.blit(surface, rect)

        self.draw_buttons()
        self.draw_boxes()

    def draw_buttons(self):
        for button in self.button_list:
            button.draw(self.display)

    def draw_boxes(self):
        for box in self.box_list:
            box.draw(self.display)
