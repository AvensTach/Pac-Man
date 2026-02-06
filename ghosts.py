import random
import settings as s
import pygame as pg


class Ghost():
    """ Class to represent a ghost """

    def __init__(self, row: int, col: int, ghost_type: s.GhostType, level):
        # grid position
        self.row: int = row
        self.col: int = col
        self.level = level

        # visual / identity
        self.color: tuple = ghost_type.value
        self.name: str = ghost_type.name

        # movement
        self.base_speed: int = s.BASE_SPEED  # pixels per frame
        self.direction: s.Direction = s.Direction.STOP
        self.frightened: bool = False
        self.timer: int = 0

        # movement state for tile-by-tile movement
        self.moving: bool = False
        self.move_progress: int = 0  # pixels moved in current tile
        self.target_row: int = row
        self.target_col: int = col

        # sprite/rect -- make it slightly smaller than TILE_SIZE so borders show
        sprite_size: int = max(4, s.TILE_SIZE - 4)
        x: int = col * s.TILE_SIZE + (s.TILE_SIZE - sprite_size) // 2
        y: int = row * s.TILE_SIZE + (s.TILE_SIZE - sprite_size) // 2
        self.rect = pg.Rect(x, y, sprite_size, sprite_size)

    @property
    def grid_pos(self):
        return self.row, self.col

    def draw(self, screen):
        """ Draw the ghost centered in its tile rect """
        draw_color = (0, 0, 255) if self.frightened else self.color
        pg.draw.rect(screen, draw_color, self.rect)

    def _wrapped_coords(self, r:int, c:int) -> tuple:
        # Wrap coordinates around the map edges
        return r % s.ROWS, c % s.COLS

    def can_move_to(self, direction: s.Direction) -> bool:
        # Calculate the candidate tile coordinates after applying direction
        dx, dy = direction.value[0], direction.value[1]
        next_row = self.row + dy
        next_col = self.col + dx
        wrapped_row, wrapped_col = self._wrapped_coords(next_row, next_col)
        # Can't move into a wall
        return not self.level.is_wall(wrapped_row, wrapped_col)

    def _start_move(self, direction: s.Direction):
        # Begin moving one tile in the given direction (assumes can_move_to checked)
        dx, dy = direction.value[0], direction.value[1]
        self.direction = direction
        self.moving = True
        self.move_progress = 0
        # compute target tile with wrapping
        tr = self.row + dy
        tc = self.col + dx
        self.target_row, self.target_col = self._wrapped_coords(tr, tc)

    def update(self):
        """ choose a direction when aligned to the tile center, then move tile-by-tile in pixels. """
        # If not currently moving, pick a legal direction (for now random among available)
        if not self.moving:
            # Prefer continuing current direction if possible
            candidates = []
            for d in (s.Direction.UP, s.Direction.LEFT, s.Direction.DOWN, s.Direction.RIGHT):
                if self.can_move_to(d):
                    candidates.append(d)

            # If there are legal moves, pick one randomly (simple AI)
            if candidates:
                # Small bias: try to keep current direction if still legal
                if self.direction in candidates and self.direction != s.Direction.STOP:
                    chosen = self.direction
                else:
                    chosen = random.choice(candidates)
                self._start_move(chosen)
            else:
                # No legal move - remain stopped
                self.direction = s.Direction.STOP
                self.moving = False
                return

        # If moving, advance pixel-wise toward the target tile
        if self.moving and self.direction != s.Direction.STOP:
            dx_px = self.direction.value[0] * self.base_speed
            dy_px = self.direction.value[1] * self.base_speed

            self.rect.x += dx_px
            self.rect.y += dy_px
            self.move_progress += abs(dx_px) + abs(dy_px)

            # When we've moved a full tile, snap to the target tile
            if self.move_progress >= s.TILE_SIZE:
                self.row = self.target_row
                self.col = self.target_col
                # Recompute rect to be exactly centered in the tile (prevent drift)
                sprite_w, sprite_h = self.rect.width, self.rect.height
                new_x = self.col * s.TILE_SIZE + (s.TILE_SIZE - sprite_w) // 2
                new_y = self.row * s.TILE_SIZE + (s.TILE_SIZE - sprite_h) // 2
                self.rect.topleft = (new_x, new_y)
                self.moving = False
                self.move_progress = 0


