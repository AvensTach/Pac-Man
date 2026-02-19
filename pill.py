import pygame as pg
import settings as s


class Pill:
    def __init__(self, row, col):
        self.row = row
        self.col = col

        self.eaten = False
        self.blink_timer = 0

        self.center = (
            col * s.TILE_SIZE + s.TILE_SIZE // 2,
            row * s.TILE_SIZE + s.TILE_SIZE // 2
        )

    def draw(self, screen):
        if self.eaten:
            return

        self.blink_timer += 1

        if (self.blink_timer // s.PILL_BLINK_SPEED) % 2 == 0:
            pg.draw.circle(
                screen,
                s.PILL_COLOR,
                self.center,
                s.PILL_RADIUS
            )

    def check_collision(self, pacman, ghosts):
        if self.eaten:
            return

        if pacman.grid_pos == (self.row, self.col):
            self.eaten = True
            pacman.score += s.PILL_SCORE_VALUE

            for g in ghosts:
                g.frightened = True
                g.timer = s.PILL_FRIGHT_TIME
