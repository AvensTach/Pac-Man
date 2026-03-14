import math
import pygame as pg
from settings import TILE_SIZE, Direction, BASE_SPEED, ROWS, COLS, COIN_SCORE_VALUE


class Pacman:
    def __init__(self, row: int, col: int) -> None:
        self.row: int = row
        self.col: int = col

        self.x: float = col * TILE_SIZE
        self.y: float = row * TILE_SIZE

        self.alive: bool = True
        self.base_speed: float = BASE_SPEED

        self.direction: Direction = Direction.STOP
        self.next_direction: Direction = Direction.STOP

        self.moving: bool = False
        self.move_progress: float = 0
        self.target_row: int = row
        self.target_col: int = col

        self.radius: int = TILE_SIZE // 2 - 2
        self.color: tuple[int, int, int] = (255, 255, 0)

        self.mouth_angle: float = 0.0
        self.mouth_opening: bool = True
        self.max_mouth_angle: float = math.pi / 4
        self.animation_speed: float = 0.15
        self.facing_angle: float = 0.0

    @property
    def grid_pos(self) -> tuple[int, int]:
        return self.row, self.col

    def _is_tunnel_row(self) -> bool:
        return 8 <= self.row <= 11

    def _handle_teleport(self) -> None:
        if self.col < 0 and self._is_tunnel_row():
            self.col = COLS - 1
            self.x = self.col * TILE_SIZE
        elif self.col >= COLS and self._is_tunnel_row():
            self.col = 0
            self.x = self.col * TILE_SIZE

    def handle_input(self, event: pg.event.Event) -> None:
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

    def can_move_to(self, layout: list[list[str]], direction: Direction) -> bool:
        dx, dy = direction.value
        next_row = self.row + dy
        next_col = self.col + dx

        if next_row < 0 or next_row >= len(layout):
            return False

        if next_col < 0 or next_col >= len(layout[0]):
            return self._is_tunnel_row()

        tile = layout[next_row][next_col]

        if tile == "=":
            return False

        return tile == "0"

    def _start_move(self, layout: list[list[str]], direction: Direction) -> None:
        if self.can_move_to(layout, direction):
            dx, dy = direction.value
            self.direction = direction
            self.moving = True
            self.move_progress = 0
            self.target_row = self.row + dy
            self.target_col = self.col + dx

            if self.direction == Direction.RIGHT:
                self.facing_angle = 0.0
            elif self.direction == Direction.UP:
                self.facing_angle = math.pi * 1.5
            elif self.direction == Direction.LEFT:
                self.facing_angle = math.pi
            elif self.direction == Direction.DOWN:
                self.facing_angle = math.pi * 0.5

    def update(self, layout: list[list[str]], level) -> None:
        if not self.moving:
            if self.next_direction != Direction.STOP:
                self._start_move(layout, self.next_direction)
            elif self.direction != Direction.STOP:
                self._start_move(layout, self.direction)
            else:
                self.mouth_angle = 0
                return

        if self.moving and self.direction != Direction.STOP:
            dx_px, dy_px = self.direction.value
            dx_px *= self.base_speed
            dy_px *= self.base_speed

            self.x += dx_px
            self.y += dy_px
            self.move_progress += abs(dx_px) + abs(dy_px)

            if self.mouth_opening:
                self.mouth_angle += self.animation_speed
                if self.mouth_angle >= self.max_mouth_angle:
                    self.mouth_angle = self.max_mouth_angle
                    self.mouth_opening = False
            else:
                self.mouth_angle -= self.animation_speed
                if self.mouth_angle <= 0:
                    self.mouth_angle = 0
                    self.mouth_opening = True

            if self.move_progress >= TILE_SIZE:
                self.row = self.target_row
                self.col = self.target_col

                self._handle_teleport()

                self.x = self.col * TILE_SIZE
                self.y = self.row * TILE_SIZE
                self.moving = False
                self.move_progress = 0

        pos = (self.row, self.col)

        if pos in level.coins:
            level.coins.remove(pos)
            level.score += COIN_SCORE_VALUE

    def draw(self, screen: pg.Surface) -> None:
        center_x = self.x + TILE_SIZE / 2
        center_y = self.y + TILE_SIZE / 2

        if self.mouth_angle <= 0.01:
            pg.draw.circle(
                screen,
                self.color,
                (int(center_x), int(center_y)),
                self.radius,
            )
        else:
            start_angle = self.facing_angle + self.mouth_angle
            end_angle = self.facing_angle + 2 * math.pi - self.mouth_angle

            points = [(center_x, center_y)]
            segments = 30
            angle_step = (end_angle - start_angle) / segments

            for i in range(segments + 1):
                current_angle = start_angle + i * angle_step
                px = center_x + self.radius * math.cos(current_angle)
                py = center_y + self.radius * math.sin(current_angle)
                points.append((px, py))

            pg.draw.polygon(screen, self.color, points)

    def check_ghost_collision(self, ghosts: list, level) -> None:
        for g in ghosts:
            if g.dead:
                continue

            distance = math.hypot(self.x - g.x, self.y - g.y)
            collision_threshold = TILE_SIZE * 0.7

            if distance < collision_threshold:
                if g.frightened:
                    g.start_death()
                    level.score += 200
                else:
                    self.alive = False