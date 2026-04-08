"""
Ghost entity module for the Pac-Man game.

This module defines the Ghost class and its core logic, including AI state
management (Chase, Scatter, Frightened, Dead), pathfinding tailored to
specific ghost personalities (Blinky, Pinky, Inky, Clyde), grid-based
movement calculation, and sprite rendering via Pygame.
"""
import math
import random

import pygame as pg

import settings as s
from level import Level
from pacman import Pacman
# Import strictly for type hinting if preferred, or just import
import assets


class Ghost:
    """ Class to represent a ghost """
    # pylint: disable=too-many-instance-attributes, too-many-positional-arguments

    def __init__(
            self,
            row: int, col: int,
            ghost_type: s.GhostType,
            level: Level,
            sprite_manager: 'assets.SpriteManager',
            spawn_delay: int = 0,
    ):
        """
        Initialize a new Ghost instance.

        Sets up the ghost's starting position, movement parameters, AI states,
        and calculates its initial collision hitbox based on the grid coordinates.

        Args:
            row (int): The starting grid row.
            col (int): The starting grid column.
            ghost_type (s.GhostType): The specific personality/type of the ghost.
            level (Level): Reference to the level layout for collision detection.
            sprite_manager (assets.SpriteManager): Manager for rendering sprites.
            spawn_delay (int, optional): Time in seconds to wait before spawning. Defaults to 0.
        """
        # pylint: disable=too-many-arguments
        self.row = row
        self.col = col
        self.level = level
        self.start_row = row
        self.start_col = col
        self.color = ghost_type.value
        self.name = ghost_type.name
        self.ghost_type = ghost_type

        self.sprite_manager = sprite_manager

        # movement params
        self.speed_multiplier = s.GHOST_SPEED_MULTIPLIER
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
        self.in_house = (self.row > 7) and (8 <= self.col <= 10)
        self.scatter_duration = 7 * s.FPS
        self.chase_duration = 20 * s.FPS

        self.moving = False
        self.move_progress = 0
        self.target_row = row
        self.target_col = col

        # Hitbox calculation (keeps hitbox slightly smaller than visual tile)
        sprite_size = max(4, s.TILE_SIZE - 4)
        x = col * s.TILE_SIZE + (s.TILE_SIZE - sprite_size) // 2
        y = row * s.TILE_SIZE + (s.TILE_SIZE - sprite_size) // 2

        self.rect = pg.Rect(x, y, sprite_size, sprite_size)
        self.x: float = float(x)
        self.y: float = float(y)

    @property
    def grid_pos(self) -> tuple[int, int]:
        """Return the current grid position (row, col) of the ghost."""
        return self.row, self.col

    @staticmethod
    def _is_opposite(d1: s.Direction, d2: s.Direction) -> bool:
        return (d1.value[0] + d2.value[0] == 0) and (d1.value[1] + d2.value[1] == 0)

    @staticmethod
    def _wrapped_coords(r: int, c: int) -> tuple[int, int]:
        return r % s.ROWS, c % s.COLS

    def _get_scatter_target(self) -> tuple[int, int]:
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
                raise ValueError("Unknown ghost type")

    def draw(self, screen: pg.Surface) -> None:
        """Render the ghost on the provided screen."""
        if self.dead or self.spawn_delay > 0:
            if self.dead:
                return

        # Determine if we should show 'frightened' or normal sprite
        show_frightened = False

        if self.frightened:
            # Logic for blinking near end of fright time
            is_blinking_phase = self.timer < (s.PILL_FRIGHT_TIME // 3)
            should_blink_normal = is_blinking_phase and (self.timer % 10 in s.GHOST_BLINK_TICKS)

            if not should_blink_normal:
                show_frightened = True

        image = self.sprite_manager.get_ghost_image(self.name, self.direction, show_frightened)

        if image:
            # Draw sprite centered on the hitbox
            img_rect = image.get_rect(center=self.rect.center)
            screen.blit(image, img_rect)
        else:
            # Fallback to rect if image fails
            color = (0, 0, 255) if show_frightened else self.color
            pg.draw.rect(screen, color, self.rect)

    def can_move_to(self, direction: s.Direction) -> bool:
        """Check if the ghost can legally move in the given direction."""
        dx, dy = direction.value
        next_row = self.row + dy
        next_col = self.col + dx
        wrapped_row, wrapped_col = self._wrapped_coords(next_row, next_col)
        tile = self.level.layout[wrapped_row][wrapped_col]

        if tile == "=":
            return self.in_house
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
        possible_directions = []
        for direction in [s.Direction.UP, s.Direction.LEFT, s.Direction.DOWN, s.Direction.RIGHT]:
            if self.can_move_to(direction):
                if (self.direction != s.Direction.STOP and
                        self._is_opposite(direction, self.direction)):
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
        """Update the ghost's AI state, mode, and pixel position."""
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

    def _handle_house_movement(self) -> None:
        """Handle pathing while the ghost is trapped in the center house."""
        target_exit_r, target_exit_c = 7, 9
        if self.row == target_exit_r and self.col == target_exit_c:
            self.in_house = False
            self.direction = s.Direction.LEFT
            return

        if self.col < target_exit_c:
            self._start_move(s.Direction.RIGHT)
        elif self.col > target_exit_c:
            self._start_move(s.Direction.LEFT)
        elif self.row > target_exit_r:
            self._start_move(s.Direction.UP)

    def _update_movement_decision(self, pacman: Pacman) -> None:
        if self.moving:
            return

        if self.in_house:
            self._handle_house_movement()
            return

        if self.frightened:
            possible_directions = []
            for direction in [
                s.Direction.UP,
                s.Direction.LEFT,
                s.Direction.DOWN,
                s.Direction.RIGHT,
            ]:
                if self.can_move_to(direction):
                    if (
                            self.direction != s.Direction.STOP
                            and self._is_opposite(direction, self.direction)
                    ):
                        continue
                    possible_directions.append(direction)

            if possible_directions:
                next_dir = random.choice(possible_directions)
                self._start_move(next_dir)
            return

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
                self.direction = s.Direction((
                    self.direction.value[0] * -1,
                    self.direction.value[1] * -1
                ))

    def _update_pixel_position(self) -> None:
        if not self.moving or self.direction == s.Direction.STOP:
            return

        adjusted_speed = self.base_speed * self.speed_multiplier
        dx_px = self.direction.value[0] * adjusted_speed
        dy_px = self.direction.value[1] * adjusted_speed

        self.x += dx_px
        self.y += dy_px
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.move_progress += abs(dx_px) + abs(dy_px)

        if self.move_progress >= s.TILE_SIZE:
            self.row = self.target_row
            self.col = self.target_col
            self._snap_to_grid()
            self.moving = False
            self.move_progress = 0

    def _snap_to_grid(self) -> None:
        sprite_w = self.rect.width
        new_x = self.col * s.TILE_SIZE + (s.TILE_SIZE - sprite_w) // 2
        new_y = self.row * s.TILE_SIZE + (s.TILE_SIZE - sprite_w) // 2

        self.x = float(new_x)
        self.y = float(new_y)
        self.rect.topleft = (int(self.x), int(self.y))

    def start_death(self) -> None:
        """Trigger the death state for the ghost, returning them to the spawn point."""
        self.dead = True
        self.frightened = False
        self.dead_timer = 5 * s.FPS
        self.moving = False
        self.direction = s.Direction.STOP

    def respawn(self) -> None:
        """Reset the ghost to its initial spawn state and position."""
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
        self.in_house = (self.start_row > 7) and (8 <= self.start_col <= 10)
        self._snap_to_grid()
