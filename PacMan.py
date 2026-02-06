import pygame as pg
from settings import TILE_SIZE, Direction, BASE_SPEED


class Pacman:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

        # visual position in pixels
        self.x = col * TILE_SIZE
        self.y = row * TILE_SIZE

        self.alive = True
        self.base_speed = BASE_SPEED  # pixels per frame (use BASE_SPEED like ghosts)

        self.direction = Direction.STOP
        self.next_direction = Direction.STOP

        # movement state for tile-by-tile movement
        self.moving = False
        self.move_progress = 0  # pixels moved in current tile
        self.target_row = row
        self.target_col = col

        self.radius = TILE_SIZE // 2 - 2
        self.color = (255, 255, 0)

    @property
    def grid_pos(self):
        return self.row, self.col

    # INPUT
    def handle_input(self, event):
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

    # COLLISION
    def can_move_to(self, layout, direction):
        dx, dy = direction.value
        next_row = self.row + dy
        next_col = self.col + dx

        # Check bounds
        if next_row < 0 or next_row >= len(layout) or next_col < 0 or next_col >= len(layout[0]):
            return False

        return layout[next_row][next_col] == "0"

    def _start_move(self, layout, direction):
        # Begin moving one tile in the given direction
        if self.can_move_to(layout, direction):
            dx, dy = direction.value
            self.direction = direction
            self.moving = True
            self.move_progress = 0
            self.target_row = self.row + dy
            self.target_col = self.col + dx

    # UPDATE
    def update(self, layout):
        # If not currently moving, try to move in the desired direction
        if not self.moving:
            if self.next_direction != Direction.STOP:
                self._start_move(layout, self.next_direction)
            elif self.direction != Direction.STOP:
                self._start_move(layout, self.direction)
            else:
                return

        # If moving, advance pixel-wise toward the target tile
        if self.moving and self.direction != Direction.STOP:
            dx_px, dy_px = self.direction.value
            dx_px *= self.base_speed
            dy_px *= self.base_speed

            self.x += dx_px
            self.y += dy_px
            self.move_progress += abs(dx_px) + abs(dy_px)

            # When we've moved a full tile, snap to the target tile
            if self.move_progress >= TILE_SIZE:
                self.row = self.target_row
                self.col = self.target_col
                self.x = self.col * TILE_SIZE
                self.y = self.row * TILE_SIZE
                self.moving = False
                self.move_progress = 0

    # DRAW
    def draw(self, screen):
        pg.draw.circle(
            screen,
            self.color,
            (int(self.x + TILE_SIZE / 2), int(self.y + TILE_SIZE / 2)),
            self.radius
        )

    # Logic of death
    def check_ghost_collision(self, ghosts):
        for g in ghosts:
            if self.grid_pos == (g.row, g.col):
                self.alive = False