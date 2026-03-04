import math
import random
import settings as s
import pygame as pg
from level import Level
from pacman import Pacman


class Ghost:
    """ Class to represent a ghost """

    def __init__(self, row: int, col: int, ghost_type: s.GhostType, level: Level, spawn_delay: int = 0):
        # grid position
        self.row = row
        self.col = col
        self.level = level

        # Store spawn for respawn
        self.start_row = row
        self.start_col = col

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

        # Frightened State
        self.frightened = False
        self.timer = 0

        # Dead State
        self.dead = False
        self.dead_timer = 0

        # Initial Spawn State
        self.spawn_delay = spawn_delay * s.FPS
        # Determine if starting inside the house (Rows 9-10 are inside, Row 7 is outside)
        self.in_house = (self.row > 7) and (8 <= self.col <= 10)

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
        match self.ghost_type:
            case s.GhostType.BLINKY:
                return -2, s.COLS - 3
            case s.GhostType.PINKY:
                return -2, 2
            case s.GhostType.INKY:
                return s.ROWS + 1, s.COLS - 1
            case s.GhostType.CLYDE:
                return s.ROWS + 1, 0
            case _:
                raise ValueError('Unknown ghost type')

    def _get_chase_target(self, pacman: Pacman) -> tuple[int, int]:
        pr, pc = pacman.grid_pos

        match self.ghost_type:
            case s.GhostType.BLINKY:
                return pr, pc
            case s.GhostType.PINKY:
                dr, dc = pacman.direction.value
                return pr + (dr * 4), pc + (dc * 4)
            case s.GhostType.INKY:
                dr, dc = pacman.direction.value
                return pr + (dr * 2), pc + (dc * 2)
            case s.GhostType.CLYDE:
                dist = math.dist((self.row, self.col), (pr, pc))
                if dist < 8:
                    return self.scatter_target
                return pr, pc
            case _:
                raise ValueError(f"Unknown ghost type: {self.ghost_type}")

    def draw(self, screen: pg.Surface) -> None:
        if self.dead or self.spawn_delay > 0:
            if self.dead:
                return

        color = (0, 0, 255) if self.frightened else self.color
        if self.frightened:
            if self.timer > (s.PILL_FRIGHT_TIME // 3) or (self.timer < (s.PILL_FRIGHT_TIME // 3) and self.timer % 10 in s.GHOST_BLINK_TICKS):
                color = (0, 0, 255)
            else:
                color = self.color
        else:
            color = self.color
        pg.draw.rect(screen, color, self.rect)

    def can_move_to(self, direction: s.Direction) -> bool:
        dx, dy = direction.value
        next_row = self.row + dy
        next_col = self.col + dx
        wrapped_row, wrapped_col = self._wrapped_coords(next_row, next_col)

        # Check for door tile
        tile = self.level.layout[wrapped_row][wrapped_col]
        if tile == "=":
            # Only allow crossing the door if currently marked as in_house (exiting)
            return self.in_house

        # If inside house, ignore walls to get out (drifting alignment)
        if self.in_house:
            return True

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

        for direction in [s.Direction.UP, s.Direction.LEFT, s.Direction.DOWN, s.Direction.RIGHT]:
            if self.can_move_to(direction):
                if self.direction != s.Direction.STOP and self._is_opposite(direction, self.direction):
                    continue
                possible_directions.append(direction)

        if not possible_directions:
            if self.direction == s.Direction.STOP:
                return s.Direction.STOP
            reverse_val = (self.direction.value[0] * -1, self.direction.value[1] * -1)
            reverse_dir = s.Direction(reverse_val)
            if self.can_move_to(reverse_dir):
                return reverse_dir
            return s.Direction.STOP

        def dist_sq(d: s.Direction) -> float:
            dx, dy = d.value
            return (self.row + dy - target_row) ** 2 + (self.col + dx - target_col) ** 2

        return min(possible_directions, key=dist_sq)

    def update(self, pacman: Pacman) -> None:
        """ Update position and AI logic """
        if self.dead:
            self.dead_timer -= 1
            if self.dead_timer <= 0:
                self.respawn()
            return

        if self.spawn_delay > 0:
            self.spawn_delay -= 1
            return

        self._update_mode()
        self._update_frightened_state()
        self._update_movement_decision(pacman)
        self._update_pixel_position()

    def _update_frightened_state(self) -> None:
        if self.frightened:
            self.timer -= 1
            if self.timer <= 0:
                self.frightened = False

    def _update_movement_decision(self, pacman: Pacman) -> None:
        """ If not currently moving, pick the next best direction """
        if self.moving:
            return

        # --- SPAWN HOUSE EXIT LOGIC ---
        if self.in_house:
            target_exit_r, target_exit_c = 7, 9

            # If we reached the exit point (outside the box door)
            if self.row == target_exit_r and self.col == target_exit_c:
                self.in_house = False
                self.direction = s.Direction.LEFT  # Force a move to start normal logic
                return

            # Logic to navigate out
            if self.col < target_exit_c:
                self._start_move(s.Direction.RIGHT)
            elif self.col > target_exit_c:
                self._start_move(s.Direction.LEFT)
            elif self.row > target_exit_r:
                self._start_move(s.Direction.UP)
            return
        # ------------------------------

        if self.frightened:
            # Random movement for frightened ghosts
            possible_directions = []
            for direction in [s.Direction.UP, s.Direction.LEFT, s.Direction.DOWN, s.Direction.RIGHT]:
                if self.can_move_to(direction):
                    if self.direction != s.Direction.STOP and self._is_opposite(direction, self.direction):
                        continue
                    possible_directions.append(direction)

            if possible_directions:
                next_dir = random.choice(possible_directions)
                self._start_move(next_dir)
            return

        # Normal target selection
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
        if self.frightened:
            return

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

    def start_death(self) -> None:
        """ Puts the ghost in a dead/cooldown state """
        self.dead = True
        self.frightened = False
        self.dead_timer = 5 * s.FPS  # 5 Seconds wait
        self.moving = False
        self.direction = s.Direction.STOP

    def respawn(self) -> None:
        """ Resets ghost to starting position and state """
        self.row = self.start_row
        self.col = self.start_col
        self.target_row = self.start_row
        self.target_col = self.start_col
        self.frightened = False
        self.timer = 0
        self.dead = False
        self.dead_timer = 0
        self.moving = False
        self.direction = s.Direction.STOP

        # Reset relative to start position
        self.in_house = (self.start_row > 7) and (8 <= self.start_col <= 10)

        self._snap_to_grid()
