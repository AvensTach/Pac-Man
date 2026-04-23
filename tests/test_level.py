import pytest
import pygame as pg
from level import Level

def test_spawn_coins_creates_coins():
    level = Level()

    assert len(level.coins) > 0

def test_coins_only_on_zero_tiles():
    level = Level()

    for r, c in level.coins:
        assert level.layout[r][c] == "0"

def test_is_wall():
    level = Level()

    # find any wall
    for r in range(len(level.layout)):
        for c in range(len(level.layout[r])):
            if level.layout[r][c] == "1":
                assert level.is_wall(r, c) is True
                return
            
def test_is_wall_out_of_bounds():
    level = Level()

    assert level.is_wall(-1, 0) is False
    assert level.is_wall(0, -1) is False
    assert level.is_wall(999, 999) is False

def test_check_pills_calls_pill_collision(mocker):
    level = Level()

    mock_pill = mocker.Mock()
    level.pills = [mock_pill]

    pacman = mocker.Mock()
    ghosts = []

    level.check_pills(pacman, ghosts)

    mock_pill.check_collision.assert_called_once_with(pacman, ghosts, level)

def test_level_keeps_score():
    level = Level(score=100)

    assert level.score == 100