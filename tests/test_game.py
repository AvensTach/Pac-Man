# pylint: disable=missing-docstring, redefined-outer-name, protected-access, too-many-positional-arguments, too-many-arguments
import os
import pytest
import pygame as pg
from game import Game
import settings as s

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

@pytest.fixture
def game_instance():
    # creates a clean game object for each test
    pg.display.set_mode((1, 1))  # Creating a microwindow for tests
    return Game()


# Initial State
def test_game_initial_state(game_instance):
    assert game_instance.state == s.STATE_MENU
    assert game_instance.running is True


# State Transitions
def test_game_settings_navigation(game_instance):
    game_instance._open_settings()
    assert game_instance.state == s.STATE_SETTINGS

    game_instance._open_menu()
    assert game_instance.state == s.STATE_MENU


# Reset Logic
def test_game_reset_creates_objects(game_instance):
    # no objects or they are old
    game_instance._reset_game()
    assert game_instance.pacman is not None
    assert len(game_instance.ghosts_list) == 4
    assert game_instance.state == s.STATE_MENU  # Check that reset does not change the state by itself
