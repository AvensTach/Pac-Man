# pylint: disable=missing-docstring, redefined-outer-name, protected-access, too-many-positional-arguments, too-many-arguments
from unittest.mock import MagicMock

import pytest
import pygame as pg

from pacman import Pacman
from settings import TILE_SIZE, Direction, COLS, COIN_SCORE_VALUE


@pytest.fixture
def mock_level():
    level = MagicMock()
    level.coins = set()
    level.score = 0
    return level


@pytest.fixture
def pacman():
    return Pacman(row=5, col=5)


@pytest.fixture
def dummy_layout():
    return [
        ["=", "=", "="],
        ["=", "0", "="],
        ["=", "0", "0"],
        ["=", "=", "="]
    ]


class TestPacman:
    def test_initial_state(self, pacman):
        assert pacman.row == 5
        assert pacman.col == 5
        assert pacman.x == 5 * TILE_SIZE
        assert pacman.y == 5 * TILE_SIZE
        assert pacman.alive is True
        assert pacman.moving is False
        assert pacman.grid_pos == (5, 5)

    def test_is_tunnel_row(self, pacman):
        pacman.row = 9
        assert pacman._is_tunnel_row() is True

        pacman.row = 5
        assert pacman._is_tunnel_row() is False

    def test_handle_teleport_left(self, pacman):
        pacman.row = 9
        pacman.col = -1
        pacman._handle_teleport()

        assert pacman.col == COLS - 1
        assert pacman.x == (COLS - 1) * TILE_SIZE

    def test_handle_teleport_right(self, pacman):
        pacman.row = 9
        pacman.col = COLS
        pacman._handle_teleport()

        assert pacman.col == 0
        assert pacman.x == 0

    def test_handle_input(self, pacman):
        event_right = pg.event.Event(pg.KEYDOWN, {'key': pg.K_RIGHT})
        pacman.handle_input(event_right)
        assert pacman.next_direction == Direction.RIGHT

        event_up = pg.event.Event(pg.KEYDOWN, {'key': pg.K_w})
        pacman.handle_input(event_up)
        assert pacman.next_direction == Direction.UP

    def test_can_move_to_valid_tile(self, pacman, dummy_layout):
        pacman.row = 2
        pacman.col = 1
        direction_mock = MagicMock()
        direction_mock.value = (1, 0)

        assert pacman.can_move_to(dummy_layout, direction_mock) is True

    def test_can_move_to_wall(self, pacman, dummy_layout):
        pacman.row = 1
        pacman.col = 1
        direction_mock = MagicMock()
        direction_mock.value = (1, 0)

        assert pacman.can_move_to(dummy_layout, direction_mock) is False

    def test_eat_coin(self, pacman, mock_level, dummy_layout):
        pacman.row = 2
        pacman.col = 2

        pacman.x = pacman.col * TILE_SIZE
        pacman.y = pacman.row * TILE_SIZE

        if hasattr(pacman, 'rect'):
            pacman.rect.x = pacman.x
            pacman.rect.y = pacman.y

        pacman.moving = True

        mock_level.coins = {(2, 2)}
        initial_score = mock_level.score

        pacman.update(dummy_layout, mock_level)

        assert len(mock_level.coins) == 0
        assert mock_level.score == initial_score + COIN_SCORE_VALUE

    def test_ghost_collision_dies(self, pacman, mock_level):
        ghost = MagicMock()
        ghost.dead = False
        ghost.frightened = False
        ghost.x = pacman.x
        ghost.y = pacman.y

        pacman.check_ghost_collision([ghost], mock_level)

        assert pacman.alive is False

    def test_ghost_collision_eats_ghost(self, pacman, mock_level):
        ghost = MagicMock()
        ghost.dead = False
        ghost.frightened = True
        ghost.x = pacman.x
        ghost.y = pacman.y

        initial_score = mock_level.score

        pacman.check_ghost_collision([ghost], mock_level)

        assert pacman.alive is True
        ghost.start_death.assert_called_once()
        assert mock_level.score == initial_score + 200

    def test_ghost_collision_ignores_dead_ghost(self, pacman, mock_level):
        ghost = MagicMock()
        ghost.dead = True
        ghost.x = pacman.x
        ghost.y = pacman.y

        pacman.check_ghost_collision([ghost], mock_level)

        assert pacman.alive is True
