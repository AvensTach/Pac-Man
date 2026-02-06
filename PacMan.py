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


    #INPUT
    def handle_input(self,event):
        if event.type != pg.KEYDOWN:
            return
        if event.key in (pg.K_LEFT, pg.K_a):
            self.next_direction = pg.Vector2(-1, 0)

        elif event.key in (pg.K_RIGHT, pg.K_d):
            self.next_direction = pg.Vector2(1, 0)

        elif event.key in (pg.K_UP, pg.K_w):
            self.next_direction = pg.Vector2(0, -1)

        elif event.key in (pg.K_DOWN, pg.K_s):
            self.next_direction = pg.Vector2(0, 1)
