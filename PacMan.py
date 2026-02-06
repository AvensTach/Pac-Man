import pygame as pg
from settings import TILE_SIZE, Direction


class Pacman:
    def __init__(self, row: int, col: int, speed=2):
        self.x = col * TILE_SIZE
        self.y = row * TILE_SIZE

        self.alive = True

        self.speed = speed

        self.direction = Direction.STOP
        self.next_direction = Direction.STOP

        self.radius = TILE_SIZE// 2 - 2
        self.color = (255, 255, 0)

    @property
    def grid_pos(self):
        return int(self.y // TILE_SIZE), int(self.x // TILE_SIZE)

    #INPUT
    def handle_input(self,event):
        if event.type != pg.KEYDOWN:
            return
        if event.key in (pg.K_LEFT, pg.K_a):
            self.next_direction = Direction.LEFT

        elif event.key in (pg.K_RIGHT, pg.K_d):
            self.next_direction = Direction.RIGHT

        elif event.key in (pg.K_UP, pg.K_w):
            self.next_direction = Direction.UP

        elif event.key in (pg.K_DOWN, pg.K_s):
            self.next_direction = Direction.DOWN

    #COLLISION
    def _can_move(self, layout, direction):
        dx, dy = direction.value

        new_x, new_y = self.x + dx * self.speed, self.y + dy * self.speed

        col = int((new_x + TILE_SIZE/2) // TILE_SIZE)
        row = int((new_y + TILE_SIZE / 2) // TILE_SIZE)

        return layout[row][col] == "0"


    #UPDATE
    def update(self, layout):

        if self.direction == Direction.STOP:
            if self._can_move(layout, self.next_direction):
                self.direction = self.next_direction
            else:
                return

        dx, dy = self.direction.value
        next_row = int(self.y // TILE_SIZE + dy)
        next_col = int(self.x // TILE_SIZE + dx)


        if layout[next_row][next_col] == "0":
            self.y = next_row * TILE_SIZE
            self.x = next_col * TILE_SIZE
        else:
            self.direction = Direction.STOP


    #DRAW
    def draw(self, screen):
        pg.draw.circle(
            screen,
            self.color,
            (int(self.x + TILE_SIZE/2), int(self.y + TILE_SIZE/2)),
            self.radius
        )
    #Logic of death
    def check_ghost_collision(self, ghosts):
        for g in ghosts:
            if self.grid_pos == g.grid_pos:
                self.alive = False