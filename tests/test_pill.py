import pytest
from unittest.mock import MagicMock, patch
import pygame as pg

from pill import Pill
import settings as s


@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr(s, 'TILE_SIZE', 20)
    monkeypatch.setattr(s, 'PILL_BLINK_SPEED', 5)
    monkeypatch.setattr(s, 'PILL_COLOR', (255, 255, 255))
    monkeypatch.setattr(s, 'PILL_RADIUS', 5)
    monkeypatch.setattr(s, 'PILL_SCORE_VALUE', 50)
    monkeypatch.setattr(s, 'PILL_FRIGHT_TIME', 300)


@pytest.fixture
def pill(mock_settings):
    return Pill(row=2, col=3)


class TestPill:
    def test_initialization(self, pill):
        assert pill.row == 2
        assert pill.col == 3
        assert pill.eaten is False
        assert pill.blink_timer == 0
        assert pill.center == (3 * 20 + 10, 2 * 20 + 10)

    @patch('pygame.draw.circle')
    def test_draw_when_eaten(self, mock_draw_circle, pill):
        pill.eaten = True
        screen = MagicMock(spec=pg.Surface)

        pill.draw(screen)

        assert pill.blink_timer == 0
        mock_draw_circle.assert_not_called()

    @patch('pygame.draw.circle')
    def test_draw_blink_visible(self, mock_draw_circle, pill):
        screen = MagicMock(spec=pg.Surface)
        pill.blink_timer = 9

        pill.draw(screen)

        assert pill.blink_timer == 10
        mock_draw_circle.assert_called_once_with(
            screen,
            (255, 255, 255),
            (70, 50),
            5
        )

    @patch('pygame.draw.circle')
    def test_draw_blink_hidden(self, mock_draw_circle, pill):
        screen = MagicMock(spec=pg.Surface)
        pill.blink_timer = 4

        pill.draw(screen)

        assert pill.blink_timer == 5
        mock_draw_circle.assert_not_called()

    def test_check_collision_already_eaten(self, pill):
        pill.eaten = True
        pacman = MagicMock()
        ghosts = [MagicMock()]
        level = MagicMock()
        level.score = 0

        pill.check_collision(pacman, ghosts, level)

        assert level.score == 0
        assert ghosts[0].frightened is not True

    def test_check_collision_no_match(self, pill):
        pacman = MagicMock()
        pacman.grid_pos = (5, 5)
        ghosts = [MagicMock()]
        level = MagicMock()
        level.score = 0

        pill.check_collision(pacman, ghosts, level)

        assert pill.eaten is False
        assert level.score == 0
        assert ghosts[0].frightened is not True

    def test_check_collision_match(self, pill):
        pacman = MagicMock()
        pacman.grid_pos = (2, 3)

        ghost1 = MagicMock()
        ghost1.frightened = False
        ghost1.timer = 0

        ghost2 = MagicMock()
        ghost2.frightened = False
        ghost2.timer = 0

        ghosts = [ghost1, ghost2]

        level = MagicMock()
        level.score = 100

        pill.check_collision(pacman, ghosts, level)

        assert pill.eaten is True
        assert level.score == 150

        assert ghost1.frightened is True
        assert ghost1.timer == 300
        assert ghost2.frightened is True
        assert ghost2.timer == 300