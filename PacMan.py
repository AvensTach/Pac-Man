import pygame as pg

class PacMan:
    def __init__(self, x, y, tile,speed=2,color=(255, 255, 0)):
        self.tile = tile
        self.speed = speed
        self.color=color

        self.pos = pg.Vector2(x * tile, y * tile)

        self.direction = pg.Vector2(0, 0)
        self.next_direction = pg.Vector2(0, 0)

        self.radius = tile // 2 - 2
