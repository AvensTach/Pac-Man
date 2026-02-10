import math
import settings as s
import pygame as pg


class Ghost:
    """ Class to represent a ghost """

    def __init__(self, row: int, col: int, ghost_type: s.GhostType, level):
        # grid position
        self.row: int = row
        self.col: int = col
        self.level = level

        # visual / identity
        self.color: tuple = ghost_type.value
        self.name: str = ghost_type.name
        self.ghost_type = ghost_type

        # movement params
        self.base_speed: int = s.BASE_SPEED
        self.direction: s.Direction = s.Direction.STOP

        # AI State
        self.mode: str = 'SCATTER'  # SCATTER or CHASE
        self.mode_timer: int = 0
        self.scatter_target: tuple = self._get_scatter_target()

        # Default Scatter/Chase cycle config (in frames)
        self.scatter_duration = 7 * s.FPS
        self.chase_duration = 20 * s.FPS

        # movement state for tile-by-tile movement
        self.moving: bool = False
        self.move_progress: int = 0
        self.target_row: int = row
        self.target_col: int = col

        # sprite setup
        sprite_size: int = max(4, s.TILE_SIZE - 4)
        x: int = col * s.TILE_SIZE + (s.TILE_SIZE - sprite_size) // 2
        y: int = row * s.TILE_SIZE + (s.TILE_SIZE - sprite_size) // 2
        self.rect = pg.Rect(x, y, sprite_size, sprite_size)

    @property
    def grid_pos(self):
        return self.row, self.col

    def _is_opposite(self, d1: s.Direction, d2: s.Direction) -> bool:
        """ Check if two directions are opposites """
        return (d1.value[0] * -1 == d2.value[0]) and (d1.value[1] * -1 == d2.value[1])

    def _get_scatter_target(self) -> tuple:
        """ Returns the fixed target corner based on ghost identity """
        # Coordinates can be outside the map to force ghosts into corners
        match self.ghost_type:
            case s.GhostType.BLINKY:
                return -2, s.COLS - 3  # Top Right
            case s.GhostType.PINKY:
                return -2, 2  # Top Left
            case s.GhostType.INKY:
                return s.ROWS + 1, s.COLS - 1  # Bottom Right
            case s.GhostType.CLYDE:
                return s.ROWS + 1, 0  # Bottom Left
            case _:
                return 0, 0  # Default fallback

    def _get_chase_target(self, pacman) -> tuple:
        """ Returns target tile based on specific ghost personality """
        pr, pc = pacman.grid_pos

        # BLINKY: Direct chase
        if self.ghost_type == s.GhostType.BLINKY:
            return pr, pc

        # PINKY: Target 4 tiles ahead of Pacman
        if self.ghost_type == s.GhostType.PINKY:
            dr, dc = pacman.direction.value
            if pacman.direction == s.Direction.UP:  # Replicate overflow bug from original if desired, but keeping simple
                return pr + (dr * 4), pc + (dc * 4)
            return pr + (dr * 4), pc + (dc * 4)

        # INKY: Usually uses Blinky's pos, but simplified here to just be aggressive
        # Let's make him target 2 tiles ahead to be slightly different from Blinky
        if self.ghost_type == s.GhostType.INKY:
            dr, dc = pacman.direction.value
            return pr + (dr * 2), pc + (dc * 2)

        # CLYDE: Chase Pacman, but if closer than 8 tiles, retreat to scatter corner
        if self.ghost_type == s.GhostType.CLYDE:
            dist = math.dist((self.row, self.col), (pr, pc))
            if dist < 8:
                return self.scatter_target
            return pr, pc

        return pr, pc

    def draw(self, screen):
        pg.draw.rect(screen, self.color, self.rect)

    def _wrapped_coords(self, r: int, c: int) -> tuple:
        return r % s.ROWS, c % s.COLS

    def can_move_to(self, direction: s.Direction) -> bool:
        dx, dy = direction.value
        next_row = self.row + dy
        next_col = self.col + dx
        wrapped_row, wrapped_col = self._wrapped_coords(next_row, next_col)
        return not self.level.is_wall(wrapped_row, wrapped_col)

    def _start_move(self, direction: s.Direction):
        dx, dy = direction.value
        self.direction = direction
        self.moving = True
        self.move_progress = 0
        tr = self.row + dy
        tc = self.col + dx
        self.target_row, self.target_col = self._wrapped_coords(tr, tc)

    def _choose_best_direction(self, target_row, target_col):
        """ Picks the valid direction that minimizes distance to target """
        possible_directions = []

        # Standard directions (excluding STOP)
        for direction in [s.Direction.UP, s.Direction.LEFT, s.Direction.DOWN, s.Direction.RIGHT]:
            # 1. Must be a valid move (not a wall)
            if self.can_move_to(direction):
                # 2. Ghosts cannot immediately reverse direction (unless stuck)
                if self.direction != s.Direction.STOP and self._is_opposite(direction, self.direction):
                    continue
                possible_directions.append(direction)

        # If locked (dead end), allow reversing
        if not possible_directions and self.direction != s.Direction.STOP:
            reverse = s.Direction((self.direction.value[0] * -1, self.direction.value[1] * -1))
            if self.can_move_to(reverse):
                possible_directions.append(reverse)

        if not possible_directions:
            return s.Direction.STOP

        # Sort candidates by distance to target
        best_dir = possible_directions[0]
        min_dist = float('inf')

        for direction in possible_directions:
            dx, dy = direction.value
            next_row = self.row + dy
            next_col = self.col + dx

            # Simple Euclidean distance squared
            d_sq = (next_row - target_row) ** 2 + (next_col - target_col) ** 2

            if d_sq < min_dist:
                min_dist = d_sq
                best_dir = direction

        return best_dir

    def update(self, pacman):
        """ Update position and AI logic """

        #  1. Mode Logic
        self.mode_timer += 1

        # Switch to Chase
        if self.mode == 'SCATTER' and self.mode_timer > self.scatter_duration:
            self.mode = 'CHASE'
            self.mode_timer = 0
            # Flip direction on mode switch
            if self.direction != s.Direction.STOP:
                self.direction = s.Direction((self.direction.value[0] * -1, self.direction.value[1] * -1))

        # Switch to Scatter
        elif self.mode == 'CHASE' and self.mode_timer > self.chase_duration:
            self.mode = 'SCATTER'
            self.mode_timer = 0
            if self.direction != s.Direction.STOP:
                self.direction = s.Direction((self.direction.value[0] * -1, self.direction.value[1] * -1))

        # Target Selection
        if self.mode == 'SCATTER':
            tr, tc = self.scatter_target
        else:
            tr, tc = self._get_chase_target(pacman)

        # Movement Decision
        if not self.moving:
            next_dir = self._choose_best_direction(tr, tc)
            if next_dir != s.Direction.STOP:
                self._start_move(next_dir)
            else:
                self.direction = s.Direction.STOP

        # Pixel Movement Execution
        if self.moving and self.direction != s.Direction.STOP:
            dx_px = self.direction.value[0] * self.base_speed
            dy_px = self.direction.value[1] * self.base_speed

            self.rect.x += dx_px
            self.rect.y += dy_px
            self.move_progress += abs(dx_px) + abs(dy_px)

            if self.move_progress >= s.TILE_SIZE:
                self.row = self.target_row
                self.col = self.target_col

                # Re-center sprite
                sprite_w = self.rect.width
                new_x = self.col * s.TILE_SIZE + (s.TILE_SIZE - sprite_w) // 2
                new_y = self.row * s.TILE_SIZE + (s.TILE_SIZE - sprite_w) // 2
                self.rect.topleft = (new_x, new_y)

                self.moving = False
                self.move_progress = 0
