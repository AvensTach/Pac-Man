import math
import settings as s
import pygame as pg
from level import Level
from PacMan import Pacman


class Ghost:
    """ Class to represent a ghost """

    def __init__(self, row: int, col: int, ghost_type: s.GhostType, level: Level):
        # grid position
        self.row = row
        self.col = col
        self.level = level

        # visual / identity
        self.color = ghost_type.value
        self.name = ghost_type.name
        self.ghost_type = ghost_type

        # movement params
        self.base_speed = s.BASE_SPEED
        self.direction = s.Direction.STOP

        # AI State
        self.mode = 'SCATTER'
        self.mode_timer = 0
        self.scatter_target = self._get_scatter_target()

        # Default Scatter/Chase cycle config
        self.scatter_duration = 7 * s.FPS
        self.chase_duration = 20 * s.FPS

        # movement state
        self.moving = False
        self.move_progress = 0
        self.target_row = row
        self.target_col = col

        sprite_size = max(4, s.TILE_SIZE - 4)
        x = col * s.TILE_SIZE + (s.TILE_SIZE - sprite_size) // 2
        y = row * s.TILE_SIZE + (s.TILE_SIZE - sprite_size) // 2

        self.rect = pg.Rect(x, y, sprite_size, sprite_size)

    @property
    def grid_pos(self) -> tuple[int, int]:
        return self.row, self.col

    @staticmethod
    def _is_opposite(d1: s.Direction, d2: s.Direction) -> bool:
        """ Check if two directions are opposites """
        return (d1.value[0] + d2.value[0] == 0) and (d1.value[1] + d2.value[1] == 0)

    @staticmethod
    def _wrapped_coords(r: int, c: int) -> tuple[int, int]:
        return r % s.ROWS, c % s.COLS

    def _get_scatter_target(self) -> tuple[int, int]:
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
                raise ValueError('Unknown ghost type')

    def _get_chase_target(self, pacman: Pacman) -> tuple[int, int]:
        pr, pc = pacman.grid_pos

        match self.ghost_type:
            # BLINKY: Direct chase
            case s.GhostType.BLINKY:
                return pr, pc

            # PINKY: Target 4 tiles ahead of Pacman
            case s.GhostType.PINKY:
                dr, dc = pacman.direction.value
                return pr + (dr * 4), pc + (dc * 4)

            # INKY: Usually uses Blinky pos, but simplified here to just be aggressive
            # Let's make him target 2 tiles ahead to be slightly different from Blinky
            case s.GhostType.INKY:
                dr, dc = pacman.direction.value
                return pr + (dr * 2), pc + (dc * 2)

            # CLYDE: Chase Pacman, but if closer than 8 tiles, retreat to scatter corner
            case s.GhostType.CLYDE:
                dist = math.dist((self.row, self.col), (pr, pc))
                if dist < 8:
                    return self.scatter_target
                return pr, pc
            case _:
                # This catches any errors if a new ghost type is added later
                # and prevents the function from returning None implicitly.
                raise ValueError(f"Unknown ghost type: {self.ghost_type}")

    def draw(self, screen: pg.Surface) -> None:
        pg.draw.rect(screen, self.color, self.rect)

    def can_move_to(self, direction: s.Direction) -> bool:
        dx, dy = direction.value
        next_row = self.row + dy
        next_col = self.col + dx
        wrapped_row, wrapped_col = self._wrapped_coords(next_row, next_col)
        return not self.level.is_wall(wrapped_row, wrapped_col)

    def _start_move(self, direction: s.Direction) -> None:
        dx, dy = direction.value
        self.direction = direction
        self.moving = True
        self.move_progress = 0
        tr = self.row + dy
        tc = self.col + dx
        self.target_row, self.target_col = self._wrapped_coords(tr, tc)

    def _choose_best_direction(self, target_row: int, target_col: int) -> s.Direction:
        """ Picks the valid direction that minimizes distance to target """
        possible_directions = []

        # Filter valid moves
        for direction in [s.Direction.UP, s.Direction.LEFT, s.Direction.DOWN, s.Direction.RIGHT]:
            if self.can_move_to(direction):
                # Don't reverse unless forced
                if self.direction != s.Direction.STOP and self._is_opposite(direction, self.direction):
                    continue
                possible_directions.append(direction)

        # Handle Dead Ends (Force Reverse)
        if not possible_directions:
            if self.direction == s.Direction.STOP:
                return s.Direction.STOP

            # Construct reverse direction
            reverse_val = (self.direction.value[0] * -1, self.direction.value[1] * -1)
            reverse_dir = s.Direction(reverse_val)

            if self.can_move_to(reverse_dir):
                return reverse_dir
            return s.Direction.STOP

        # Pick Best Direction using Euclidean distance squared
        def dist_sq(d: s.Direction) -> float:
            dx, dy = d.value
            return (self.row + dy - target_row) ** 2 + (self.col + dx - target_col) ** 2

        return min(possible_directions, key=dist_sq)

    def update(self, pacman: Pacman) -> None:
        """ Update position and AI logic """
        self._update_mode()
        self._update_movement_decision(pacman)  # Pass pacman instead of target
        self._update_pixel_position()

    def _update_movement_decision(self, pacman: Pacman) -> None:
        """ If not currently moving, pick the next best direction """
        if self.moving:
            return

        # Only calculate target if we are actually allowed to choose a direction
        match self.mode:
            case 'SCATTER':
                tr, tc = self.scatter_target
            case 'CHASE':
                tr, tc = self._get_chase_target(pacman)
            case _:
                raise ValueError('Unknown ghost mode')

        next_dir = self._choose_best_direction(tr, tc)

        if next_dir != s.Direction.STOP:
            self._start_move(next_dir)
        else:
            self.direction = s.Direction.STOP

    def _update_mode(self) -> None:
        """ Handles the timer for switching between SCATTER and CHASE """
        self.mode_timer += 1

        switch_needed = False
        if self.mode == 'SCATTER' and self.mode_timer > self.scatter_duration:
            self.mode = 'CHASE'
            switch_needed = True
        elif self.mode == 'CHASE' and self.mode_timer > self.chase_duration:
            self.mode = 'SCATTER'
            switch_needed = True

        if switch_needed:
            self.mode_timer = 0
            # Flip direction immediately on mode switch
            if self.direction != s.Direction.STOP:
                self.direction = s.Direction((self.direction.value[0] * -1, self.direction.value[1] * -1))

    def _update_pixel_position(self) -> None:
        """ Handles the smooth animation between tiles """
        if not self.moving or self.direction == s.Direction.STOP:
            return

        dx_px = self.direction.value[0] * self.base_speed
        dy_px = self.direction.value[1] * self.base_speed

        self.rect.x += dx_px
        self.rect.y += dy_px
        self.move_progress += abs(dx_px) + abs(dy_px)

        # Snap to grid if we've moved a full tile
        if self.move_progress >= s.TILE_SIZE:
            self.row = self.target_row
            self.col = self.target_col
            self._snap_to_grid()

            self.moving = False
            self.move_progress = 0

    def _snap_to_grid(self) -> None:
        """ Re-centers the sprite visual on the logical grid position """
        sprite_w = self.rect.width
        new_x = self.col * s.TILE_SIZE + (s.TILE_SIZE - sprite_w) // 2
        new_y = self.row * s.TILE_SIZE + (s.TILE_SIZE - sprite_w) // 2
        self.rect.topleft = (new_x, new_y)
