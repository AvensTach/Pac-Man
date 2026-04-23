"""Tests for Level class."""

from level import Level
from unittest.mock import Mock


def test_spawn_coins_creates_coins():
    """Test that coins are created."""
    level = Level()
    assert len(level.coins) > 0


def test_coins_only_on_zero_tiles():
    """Test that coins are placed only on '0' tiles."""
    level = Level()

    for r, row in enumerate(level.layout):
        for c, _ in enumerate(row):
            if (r, c) in level.coins:
                assert level.layout[r][c] == "0"


def test_is_wall():
    """Test wall detection."""
    level = Level()

    for r, row in enumerate(level.layout):
        for c, tile in enumerate(row):
            if tile == "1":
                assert level.is_wall(r, c)
                return


def test_is_wall_out_of_bounds():
    """Test out of bounds wall check."""
    level = Level()

    assert not level.is_wall(-1, 0)
    assert not level.is_wall(0, -1)
    assert not level.is_wall(999, 999)


def test_check_pills_calls_pill_collision():
    """Test that pill collision is triggered."""
    level = Level()

    mock_pill = Mock()
    level.pills = [mock_pill]

    pacman = Mock()
    ghosts = []

    level.check_pills(pacman, ghosts)

    mock_pill.check_collision.assert_called_once_with(pacman, ghosts, level)


def test_level_keeps_score():
    """Test that score is preserved."""
    level = Level(score=100)
    assert level.score == 100