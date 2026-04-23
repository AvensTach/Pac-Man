import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
import pytest
from menu import Button, MainMenuScreen, SettingsScreen


@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    pg.init()
    pg.font.init()
    yield
    pg.quit()

def test_button_click_calls_callback(mocker):
    callback = mocker.Mock()

    btn = Button(pg.Rect(0, 0, 100, 50), "TEST", pg.font.SysFont(None, 24), callback)

    # натискання
    btn.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, {"pos": (10, 10), "button": 1}))
    btn.handle_event(pg.event.Event(pg.MOUSEBUTTONUP, {"pos": (10, 10), "button": 1}))

    callback.assert_called_once()

def test_button_hover():
    btn = Button(pg.Rect(0, 0, 100, 50), "TEST", pg.font.SysFont(None, 24), lambda: None)

    btn.handle_event(pg.event.Event(pg.MOUSEMOTION, {"pos": (10, 10)}))

    assert btn.hovered is True

def test_button_not_clicked_outside(mocker):
    callback = mocker.Mock()

    btn = Button(pg.Rect(0, 0, 100, 50), "TEST", pg.font.SysFont(None, 24), callback)

    btn.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, {"pos": (200, 200), "button": 1}))
    btn.handle_event(pg.event.Event(pg.MOUSEBUTTONUP, {"pos": (200, 200), "button": 1}))

    callback.assert_not_called()

def test_main_menu_play_button(mocker):
    on_play = mocker.Mock()
    on_exit = mocker.Mock()
    on_settings = mocker.Mock()

    menu = MainMenuScreen(on_play, on_exit, on_settings)

    # симулюємо клік
    pos = menu.play_btn.rect.center

    menu.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, {"pos": pos, "button": 1}))
    menu.handle_event(pg.event.Event(pg.MOUSEBUTTONUP, {"pos": pos, "button": 1}))

    on_play.assert_called_once()

import settings as s

def test_toggle_music():
    screen = SettingsScreen(lambda: None)

    initial = s.CONFIG["MUSIC_ON"]

    screen._toggle_music()

    assert s.CONFIG["MUSIC_ON"] != initial

def test_toggle_sfx():
    screen = SettingsScreen(lambda: None)

    initial = s.CONFIG["SFX_ON"]

    screen._toggle_sfx()

    assert s.CONFIG["SFX_ON"] != initial

def test_back_button_calls_callback(mocker):
    callback = mocker.Mock()

    screen = SettingsScreen(callback)

    pos = screen.back_btn.rect.center

    screen.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, {"pos": pos, "button": 1}))
    screen.handle_event(pg.event.Event(pg.MOUSEBUTTONUP, {"pos": pos, "button": 1}))

    callback.assert_called_once()