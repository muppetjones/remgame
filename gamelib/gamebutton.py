

TEXT_COLOR = colors.white
TILE_COLOR = colors.colorblind.dark_pink


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
