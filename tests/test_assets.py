# pylint: disable=missing-docstring, redefined-outer-name, protected-access, too-many-positional-arguments, too-many-arguments
from unittest.mock import patch, MagicMock

import pytest
import pygame as pg

import settings as s
from assets import SpriteManager


@pytest.fixture
@patch('os.path.exists', return_value=False)
def manager(mock_exists):  # pylint: disable=unused-argument
    """
    Creates a SpriteManager where all file checks return False.
    This safely forces the manager to generate its dummy magenta Pygame Surfaces
    instead of crashing if real image files are missing during testing.
    """
    return SpriteManager()


class TestSpriteManager:

    def test_fallback_creation_when_files_missing(self, manager):
        # We know blinky and UP exist because we define them based on the Enums
        sprite = manager.ghost_sprites['blinky'][s.Direction.UP]

        # Verify the fallback is a Pygame surface
        assert isinstance(sprite, pg.Surface)

        # Verify it uses the un-scaled TILE_SIZE for the fallback
        assert sprite.get_size() == (s.TILE_SIZE, s.TILE_SIZE)

        # Verify it is filled with the magenta error color (150, 0, 150)
        # Pygame colors include an alpha channel by default (255)
        assert sprite.get_at((0, 0)) == (150, 0, 150, 255)

    @patch('os.path.exists', return_value=True)
    @patch('pygame.image.load')
    @patch('pygame.transform.scale')
    def test_successful_sprite_loading(self, mock_scale, mock_load, mock_exists):  # pylint: disable=unused-argument
        # Mock the loaded image and its convert() method
        mock_image = MagicMock()
        mock_load.return_value = mock_image
        mock_image.convert.return_value = mock_image

        # Mock the scaled image that gets returned at the end
        mock_scaled = MagicMock()
        mock_scale.return_value = mock_scaled

        # Initialize the manager
        sm = SpriteManager()

        # Assertions to ensure Pygame processes the image correctly
        assert mock_load.called
        mock_image.convert.assert_called()
        mock_image.set_colorkey.assert_called_with((0, 0, 0))

        # Ensure scaling logic was triggered with the correct math (-4)
        mock_scale.assert_called_with(mock_image, (s.TILE_SIZE - 4, s.TILE_SIZE - 4))

        # Verify the final stored sprite is the mocked scaled image
        assert sm.frightened_sprite == mock_scaled

    def test_get_ghost_image_frightened(self, manager):
        img = manager.get_ghost_image('blinky', s.Direction.UP, frightened=True)
        assert img == manager.frightened_sprite

    def test_get_ghost_image_normal(self, manager):
        img = manager.get_ghost_image('blinky', s.Direction.UP, frightened=False)
        assert img == manager.ghost_sprites['blinky'][s.Direction.UP]

    def test_get_ghost_image_stop_direction(self, manager):
        # When STOP is passed, the manager should default to the RIGHT facing sprite
        img = manager.get_ghost_image('blinky', s.Direction.STOP, frightened=False)
        assert img == manager.ghost_sprites['blinky'][s.Direction.RIGHT]

    def test_get_ghost_image_invalid_name(self, manager):
        # Passing a ghost name that isn't in the enum should safely return None
        img = manager.get_ghost_image('fake_ghost', s.Direction.UP, frightened=False)
        assert img is None

    def test_get_ghost_image_case_insensitive(self, manager):
        # The manager should handle uppercase strings safely via .lower()
        img = manager.get_ghost_image('BLINKY', s.Direction.UP, frightened=False)
        assert img == manager.ghost_sprites['blinky'][s.Direction.UP]
