import os
import pygame as pg
import settings as s
import ghosts
from pacman import Pacman
from level import Level
from menu import MainMenuScreen, SettingsScreen


class Game:
    def __init__(self):
        pg.init()
        # Initialize mixer for sound
        pg.mixer.init()

        self.screen = pg.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        pg.display.set_caption("Pacman")
        self.clock = pg.time.Clock()
        self.running = True
        self.state = s.STATE_MENU

        # Track start time for intro delay
        self.play_start_time = 0

        # Track currently playing background loop
        self.current_bg_sound = None

        # --- Load Sounds ---
        self.sounds = {}
        # Define sound file names map
        sound_files = {
            "intro": "intro.wav",
            "munch": "munch.wav",
            "eat_ghost": "eat_ghost.wav",
            "death": "death.wav",
            "siren": "siren.wav",  # Normal ghost movement (loop)
            "frightened": "frightened.wav"  # Blue ghost movement (loop)
        }

        # Load safely (uses dummy sound if file missing to prevent crash)
        dummy_sound = pg.mixer.Sound(buffer=bytearray([0] * 100))
        for key, filename in sound_files.items():
            # Check primary path
            path = os.path.join("assets/sounds", filename)
            if os.path.exists(path):
                self.sounds[key] = pg.mixer.Sound(path)
            else:
                # Fallback check (in case user put them directly in assets)
                path_alt = os.path.join("assets", filename)
                if os.path.exists(path_alt):
                    self.sounds[key] = pg.mixer.Sound(path_alt)
                else:
                    print(f"Warning: Sound {filename} not found.")
                    self.sounds[key] = dummy_sound

        # --- Menu Screens ---
        self.menu_screen = MainMenuScreen(
            on_play=self.start_game,
            on_exit=self.quit_game,
            on_settings=self.open_settings
        )
        self.settings_screen = SettingsScreen(on_back=self.open_menu)

        # Game Entities (Initialized in reset_game)
        self.level = None
        self.pacman = None
        self.ghosts_list = []
        self.blinky = None
        self.pinky = None
        self.inky = None
        self.clyde = None

    def stop_bg_sounds(self):
        """Stops the currently playing background loop (siren or frightened)."""
        if self.current_bg_sound:
            self.sounds[self.current_bg_sound].stop()
            self.current_bg_sound = None

    # --- State management callbacks ---
    def start_game(self):
        self.reset_game()
        self.state = s.STATE_PLAYING
        self.stop_bg_sounds()  # Ensure clean sound state
        self.sounds["intro"].play()
        # Record the time when gameplay was triggered
        self.play_start_time = pg.time.get_ticks()

    def open_settings(self):
        self.state = s.STATE_SETTINGS

    def open_menu(self):
        self.stop_bg_sounds()
        self.state = s.STATE_MENU

    def quit_game(self):
        self.running = False

    def reset_game(self):
        """Initializes a fresh game state."""
        self.level = Level()

        # Pacman Spawn
        self.pacman = Pacman(15, 9)

        # Ghost Spawns
        self.blinky = ghosts.Ghost(7, 9, s.GhostType.BLINKY, self.level, spawn_delay=0)
        self.pinky = ghosts.Ghost(9, 9, s.GhostType.PINKY, self.level, spawn_delay=2)
        self.inky = ghosts.Ghost(9, 8, s.GhostType.INKY, self.level, spawn_delay=4)
        self.clyde = ghosts.Ghost(9, 10, s.GhostType.CLYDE, self.level, spawn_delay=6)

        self.ghosts_list = [self.blinky, self.pinky, self.inky, self.clyde]

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                return

            # Delegate events based on state
            if self.state == s.STATE_MENU:
                self.menu_screen.handle_event(event)
            elif self.state == s.STATE_SETTINGS:
                self.settings_screen.handle_event(event)
            elif self.state == s.STATE_PLAYING:
                if self.pacman:
                    self.pacman.handle_input(event)

    def update(self):
        if self.state == s.STATE_PLAYING:
            # Wait for intro music to finish (approx 4.5 seconds)
            if pg.time.get_ticks() - self.play_start_time < 4500:
                return

            # Capture scores before update to detect changes
            prev_level_score = self.level.score
            prev_pacman_score = self.pacman.score

            # Update ghosts
            for ghost in self.ghosts_list:
                ghost.update(self.pacman)

            # Update pacman
            self.pacman.update(s.LAYOUT, self.level)

            # Interactions
            self.level.check_pills(self.pacman, self.ghosts_list)
            self.pacman.check_ghost_collision(self.ghosts_list)

            # --- Sound Logic ---

            # 1. Action Sounds (One-shot)
            if self.level.score > prev_level_score:
                self.sounds["munch"].play()

            if self.pacman.score > prev_pacman_score:
                self.sounds["eat_ghost"].play()

            # 2. Background Loops
            # Check if any ghost is frightened (and not dead)
            any_frightened = any(g.frightened for g in self.ghosts_list)
            target_sound = "frightened" if any_frightened else "siren"

            if self.current_bg_sound != target_sound:
                # Stop currently playing loop
                if self.current_bg_sound:
                    self.sounds[self.current_bg_sound].stop()

                # Start new loop (-1 means loop indefinitely)
                self.sounds[target_sound].play(-1)
                self.current_bg_sound = target_sound

            # Death check
            if not self.pacman.alive:
                self.stop_bg_sounds()  # Silence movement sounds
                self.sounds["death"].play()
                print("Pacman DIED")
                self.state = s.STATE_MENU
                self.pacman.alive = True

    def draw(self):
        if self.state == s.STATE_MENU:
            self.menu_screen.draw(self.screen)

        elif self.state == s.STATE_SETTINGS:
            self.settings_screen.draw(self.screen)

        elif self.state == s.STATE_PLAYING:
            self.screen.fill(s.WALL_COLOR)
            self.level.draw(self.screen)
            self.pacman.draw(self.screen)

            for ghost in self.ghosts_list:
                ghost.draw(self.screen)

            self.level.draw_ui(self.screen)

        pg.display.flip()

    def run(self):
        """Main Game Loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(s.FPS)

        pg.quit()