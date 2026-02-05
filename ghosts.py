import settings as s
import pygame as pg


class Ghost():
    """ Class to represent a ghost """

    def __init__(self, x: int, y: int, ghost_type: s.GhostType):
        self.x: int = x
        self.y: int = y
        self.color: tuple = ghost_type.value
        self.name: str = ghost_type.name
        self.base_speed = s.BASE_SPEED
        self.direction = s.Direction.DOWN
        self.frightened = False
        self.timer = 0

        self.rect = pg.Rect(self.x, self.y, 30, 30)

    def draw(self, screen):
        """ Draw the ghost """
        draw_color = (0, 0, 255) if self.frightened else self.color
        pg.draw.rect(screen, draw_color, self.rect)

    def update(self):
        """ Move the ghost """

        # 1. Calculate and apply movement based on current direction
        dx = self.direction.value[0] * self.base_speed
        dy = self.direction.value[1] * self.base_speed

        self.rect.x += dx
        self.rect.y += dy

        # Wrap around logic (Tunneling)
        # If it goes off the RIGHT side, put it on the LEFT
        if self.rect.left > s.SCREEN_WIDTH:
            self.rect.right = 0

        # If it goes off the LEFT side, put it on the RIGHT
        elif self.rect.right < 0:
            self.rect.left = s.SCREEN_WIDTH

        # If it goes off the BOTTOM, put it at the TOP
        if self.rect.top > s.SCREEN_HEIGHT:
            self.rect.bottom = 0

        # If it goes off the TOP, put it at the BOTTOM
        elif self.rect.bottom < 0:
            self.rect.top = s.SCREEN_HEIGHT

        # Sync the raw x, y coordinates with the rect
        self.x, self.y = self.rect.topleft
