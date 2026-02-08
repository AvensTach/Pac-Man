import pygame as pg
from settings import TILE_SIZE, Direction, BASE_SPEED, ROWS, COLS

class Pacman:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

        # visual position in pixels
        self.x = col * TILE_SIZE
        self.y = row * TILE_SIZE

        self.alive = True
        self.base_speed = BASE_SPEED

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

    def _is_tunnel_row(self) -> bool:
        """Check if current row is in the tunnel area (middle of map)"""
        # Tunnel is roughly in the middle rows
        return 8 <= self.row <= 11

    def _handle_teleport(self):
        """Handle teleportation through the tunnel"""
        # If Pacman goes off the left side of the tunnel, teleport to right
        if self.col < 0 and self._is_tunnel_row():
            self.col = COLS - 1
            self.x = self.col * TILE_SIZE

        # If Pacman goes off the right side of the tunnel, teleport to left
        elif self.col >= COLS and self._is_tunnel_row():
            self.col = 0
            self.x = self.col * TILE_SIZE

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

        # Check bounds - allow movement off-screen in tunnel rows only
        if next_row < 0 or next_row >= len(layout):
            return False

        # Allow wrapping through tunnel on left/right sides
        if next_col < 0 or next_col >= len(layout[0]):
            # Only allow if in tunnel row
            return self._is_tunnel_row() or (next_col == -1 and self._is_tunnel_row()) or (
                        next_col == COLS and self._is_tunnel_row())

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
    def update(self, layout, level):
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

                # Handle teleportation through tunnel
                self._handle_teleport()

                self.x = self.col * TILE_SIZE
                self.y = self.row * TILE_SIZE
                self.moving = False
                self.move_progress = 0
        
        # Determine the current tile coordinates based on pixel position
        row = self.y // TILE_SIZE
        col = self.x // TILE_SIZE
        pos = (row, col)

        # If Pacman enters a tile containing a coin, collect it
        if pos in level.coins:
            level.coins.remove(pos)


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