import pytest
from unittest.mock import MagicMock
import pygame as pg

import settings as s
from ghosts import Ghost
from level import Level
from pacman import Pacman


@pytest.fixture
def mock_level():
    """Fixture providing a mock implementation of the level."""
    level = MagicMock(spec=Level)
    # Simulate an empty 3x3 layout by default, where everything is non-wall '0'
    level.layout = [["0", "0", "0"] for _ in range(3)]
    level.is_wall.return_value = False
    return level


@pytest.fixture
def mock_sprite_manager():
    """Fixture to provide a mocked SpriteManager to prevent loading real assets."""
    sprite_manager = MagicMock()
    sprite_manager.get_ghost_image.return_value = MagicMock(spec=pg.Surface)
    return sprite_manager


@pytest.fixture
def mock_pacman():
    """Fixture to provide a standard pacman with fixed positioning and direction."""
    pacman = MagicMock(spec=Pacman)
    pacman.grid_pos = (5, 5)
    pacman.direction = s.Direction.LEFT
    return pacman


@pytest.fixture
def default_ghost(mock_level, mock_sprite_manager):
    """Fixture providing a generic Ghost instance (Blinky at 1,1) for testing general methods."""
    return Ghost(1, 1, s.GhostType.BLINKY, mock_level, mock_sprite_manager)


class TestGhostTargets:
    """Group of tests for finding ghost targets (Data-Driven Tests)."""

    @pytest.mark.parametrize("ghost_type, expected_target", [
        (s.GhostType.BLINKY, (-2, s.COLS - 3)),
        (s.GhostType.PINKY, (-2, 2)),
        (s.GhostType.INKY, (s.ROWS + 1, s.COLS - 1)),
        (s.GhostType.CLYDE, (s.ROWS + 1, 0)),
    ])
    def test_get_scatter_target(self, mock_level, mock_sprite_manager, ghost_type, expected_target):
        # Arrange
        ghost = Ghost(5, 5, ghost_type, mock_level, mock_sprite_manager)

        # Act
        target = ghost._get_scatter_target()

        # Assert
        assert target == expected_target

    @pytest.mark.parametrize("ghost_type, expected_target", [
        (s.GhostType.BLINKY, (5, 5)),  # Pacman's exact position
        (s.GhostType.PINKY, (5 + (-1 * 4), 5 + (0 * 4))),  # 4 tiles ahead of Pacman (LEFT path)
        (s.GhostType.INKY, (5 + (-1 * 2), 5 + (0 * 2))),  # 2 tiles ahead of Pacman
    ])
    def test_get_chase_target_non_clyde(self, mock_level, mock_sprite_manager, mock_pacman, ghost_type,
                                        expected_target):
        # Arrange
        ghost = Ghost(10, 10, ghost_type, mock_level, mock_sprite_manager)

        # Act
        target = ghost._get_chase_target(mock_pacman)

        # Assert
        assert target == expected_target

    def test_get_chase_target_clyde_far(self, mock_level, mock_sprite_manager, mock_pacman):
        # Arrange
        # Clyde is far (> 8 tiles) - acts like Blinky
        ghost = Ghost(15, 15, s.GhostType.CLYDE, mock_level, mock_sprite_manager)

        # Act
        target = ghost._get_chase_target(mock_pacman)

        # Assert
        assert target == (5, 5)

    def test_get_chase_target_clyde_close(self, mock_level, mock_sprite_manager, mock_pacman):
        # Arrange
        # Clyde is close (< 8 tiles) - scatters
        ghost = Ghost(5, 6, s.GhostType.CLYDE, mock_level, mock_sprite_manager)

        # Act
        target = ghost._get_chase_target(mock_pacman)

        # Assert
        assert target == ghost.scatter_target


class TestGhostMovement:

    @pytest.mark.parametrize("direction, dy, dx, is_wall_result, will_move", [
        (s.Direction.UP, -1, 0, False, True),
        (s.Direction.UP, -1, 0, True, False),
        (s.Direction.RIGHT, 0, 1, False, True)
    ])
    def test_can_move_to_standard(self, default_ghost, mock_level, direction, dy, dx, is_wall_result, will_move):
        # Arrange
        mock_level.is_wall.return_value = is_wall_result

        # Act
        result = default_ghost.can_move_to(direction)

        # Assert
        assert result == will_move
        # Verify it queries the wrapped position
        expected_wrapped_row, expected_wrapped_col = default_ghost._wrapped_coords(1 + dy, 1 + dx)
        if not is_wall_result and default_ghost.level.layout[expected_wrapped_row][expected_wrapped_col] != "=":
            mock_level.is_wall.assert_called_with(expected_wrapped_row, expected_wrapped_col)

    def test_start_move(self, default_ghost):
        # Act
        default_ghost._start_move(s.Direction.DOWN)

        # Assert
        assert default_ghost.direction == s.Direction.DOWN
        assert default_ghost.moving is True
        assert default_ghost.move_progress == 0
        expected_r, expected_c = default_ghost._wrapped_coords(1 + 1, 1 + 0)
        assert default_ghost.target_row == expected_r
        assert default_ghost.target_col == expected_c


class TestGhostStateTransitions:
    """Group of tests focused on state transitions like Death, Frightened Mode, Respawn, etc."""

    def test_start_death(self, default_ghost):
        # Arrange
        default_ghost.frightened = True
        default_ghost.moving = True
        default_ghost.direction = s.Direction.LEFT

        # Act
        default_ghost.start_death()

        # Assert
        assert default_ghost.dead is True
        assert default_ghost.frightened is False
        assert default_ghost.dead_timer == 5 * s.FPS
        assert default_ghost.moving is False
        assert default_ghost.direction == s.Direction.STOP

    def test_respawn(self, default_ghost):
        # Arrange
        default_ghost.start_row = 1
        default_ghost.start_col = 1
        default_ghost.row = 15
        default_ghost.col = 15
        default_ghost.frightened = True
        default_ghost.timer = 100
        default_ghost.dead = True
        default_ghost.dead_timer = 50

        # Act
        default_ghost.respawn()

        # Assert
        assert default_ghost.row == 1
        assert default_ghost.col == 1
        assert default_ghost.target_row == 1
        assert default_ghost.target_col == 1
        assert default_ghost.frightened is False
        assert default_ghost.timer == 0
        assert default_ghost.dead is False
        assert default_ghost.dead_timer == 0
        assert default_ghost.direction == s.Direction.STOP

    def test_update_frightened_state(self, default_ghost):
        # Arrange
        default_ghost.frightened = True
        default_ghost.timer = 2

        # Act - Tick 1
        default_ghost._update_frightened_state()
        assert default_ghost.timer == 1
        assert default_ghost.frightened is True

        # Act - Tick 2
        default_ghost._update_frightened_state()
        assert default_ghost.timer == 0
        assert default_ghost.frightened is False
