"""
Asset management module for game sprites.

This module provides the SpriteManager class, which is responsible for handling
the loading, scaling, and retrieval of graphical assets (sprites) for the game.
It specifically manages directional and state-based sprites for ghost entities,
processes transparency (colorkeying), scales images to fit the game's tile size,
and includes a fallback rendering mechanism for missing files.
"""
import os
import pygame as pg
import settings as s


class SpriteManager:
    """Manages loading, scaling, and retrieving usage sprites."""

    def __init__(self):
        self.ghost_sprites = {}
        self.frightened_sprite = None
        self._load_and_process_sprites()

    def _load_and_process_sprites(self):
        # Helper to load and scale
        def load_sprite(filename):
            path = os.path.join("assets", "sprites", filename)

            # Fallback: create a colored block if file is missing
            if not os.path.exists(path):
                print(f"Sprite missing: {filename}")
                surf = pg.Surface((s.TILE_SIZE, s.TILE_SIZE))
                surf.fill((150, 0, 150))  # Error/Magenta
                return surf

            img = pg.image.load(path).convert()
            # Make black color transparent
            img.set_colorkey((0, 0, 0))

            # Scale 16x16 -> 32x32
            return pg.transform.scale(img, (s.TILE_SIZE - 4, s.TILE_SIZE - 4))

        directions = {
            s.Direction.UP: "up",
            s.Direction.DOWN: "down",
            s.Direction.LEFT: "left",
            s.Direction.RIGHT: "right"
        }

        # 1. Load Normal Ghost Sprites
        # Expects files: blinky_up.png, pinky_left.png, etc.
        for g_type in s.GhostType:
            name_key = g_type.name.lower()  # blinky, pinky...
            self.ghost_sprites[name_key] = {}

            for d_enum, d_str in directions.items():
                filename = f"{name_key}_{d_str}.png"
                self.ghost_sprites[name_key][d_enum] = load_sprite(filename)

        # 2. Load Frightened Sprite
        self.frightened_sprite = load_sprite("frightened.png")

    def get_ghost_image(self, ghost_name: str, direction: s.Direction, frightened: bool):
        """Returns the correct surface based on state."""
        if frightened:
            return self.frightened_sprite

        # Default to RIGHT if stationary, otherwise use current direction
        lookup_dir = direction if direction != s.Direction.STOP else s.Direction.RIGHT

        # Safe lookup
        g_images = self.ghost_sprites.get(ghost_name.lower())
        if g_images:
            return g_images.get(lookup_dir)
        return None
