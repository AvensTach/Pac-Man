import os
import pygame as pg
import settings as s
import ghosts
from pacman import Pacman
from level import Level
from menu import MainMenuScreen, SettingsScreen
from assets import SpriteManager  # <--- Import new class


class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()

        self.screen = pg.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        pg.display.set_caption("Pacman")
        self.clock = pg.time.Clock()
        self.running = True
        self.state = s.STATE_MENU
        self.play_start_time = 0
        self.current_bg_sound = None

        # --- Load Sounds ---
        self.sounds = {}
        self._analyze_sounds()

        # --- Load Sprites ---
        self.sprite_manager = SpriteManager()  # <--- Initialize here

        # --- Menu Screens ---
        self.menu_screen = MainMenuScreen(
            on_play=self._start_game,
            on_exit=self._quit_game,
            on_settings=self._open_settings
        )
        self.settings_screen = SettingsScreen(on_back=self._open_menu)

        self.level = None
        self.pacman = None
        self.ghosts_list = []
        self.blinky = self.pinky = self.inky = self.clyde = None

    def _analyze_sounds(self):
        dummy_sound = pg.mixer.Sound(buffer=bytearray([0] * 100))
        for key, filename in s.sound_files.items():
            path = os.path.join("assets/sounds", filename)
            if os.path.exists(path):
                self.sounds[key] = pg.mixer.Sound(path)
            else:
                path_alt = os.path.join("assets", filename)
                if os.path.exists(path_alt):
                    self.sounds[key] = pg.mixer.Sound(path_alt)
                else:
                    print(f"Warning: Sound {filename} not found.")
                    self.sounds[key] = dummy_sound

    def stop_bg_sounds(self):
        if self.current_bg_sound:
            self.sounds[self.current_bg_sound].stop()
            self.current_bg_sound = None

    def _start_game(self):
        self._reset_game()
        self.state = s.STATE_PLAYING
        self.stop_bg_sounds()
        self.sounds["intro"].play()
        self.play_start_time = pg.time.get_ticks()

    def _open_settings(self):
        self.state = s.STATE_SETTINGS

    def _open_menu(self):
        self.stop_bg_sounds()
        self.state = s.STATE_MENU

    def _quit_game(self):
        self.running = False

    def _reset_game(self):
        """Initializes a fresh game state."""
        self.level = Level()
        self.pacman = Pacman(15, 9)

        # Pass sprite_manager to ghosts
        self.blinky = ghosts.Ghost(7, 9, s.GhostType.BLINKY, self.level, self.sprite_manager, spawn_delay=0)
        self.pinky = ghosts.Ghost(9, 9, s.GhostType.PINKY, self.level, self.sprite_manager, spawn_delay=2)
        self.inky = ghosts.Ghost(9, 8, s.GhostType.INKY, self.level, self.sprite_manager, spawn_delay=4)
        self.clyde = ghosts.Ghost(9, 10, s.GhostType.CLYDE, self.level, self.sprite_manager, spawn_delay=6)

        self.ghosts_list = [self.blinky, self.pinky, self.inky, self.clyde]

    # ... (Rest of Game class handling events, updates, drawing remains identical) ...
    def _handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                return
            if self.state == s.STATE_MENU:
                self.menu_screen.handle_event(event)
            elif self.state == s.STATE_SETTINGS:
                self.settings_screen.handle_event(event)
            elif self.state == s.STATE_PLAYING:
                if self.pacman:
                    self.pacman.handle_input(event)

    def _update(self):
        if self.state == s.STATE_PLAYING:
            if pg.time.get_ticks() - self.play_start_time < 4500:
                return

            prev_level_score = self.level.score

            for ghost in self.ghosts_list:
                ghost.update(self.pacman)

            self.pacman.update(s.LAYOUT, self.level)
            self.level.check_pills(self.pacman, self.ghosts_list)

            self.pacman.check_ghost_collision(self.ghosts_list, self.level)

            score_diff = self.level.score - prev_level_score

            if score_diff >= 200:
                self.sounds["eat_ghost"].play()
            elif score_diff > 0:
                self.sounds["munch"].play()

            any_frightened = any(g.frightened for g in self.ghosts_list)
            target_sound = "frightened" if any_frightened else "siren"

            if self.current_bg_sound != target_sound:
                if self.current_bg_sound:
                    self.sounds[self.current_bg_sound].stop()
                self.sounds[target_sound].play(-1)
                self.current_bg_sound = target_sound

            if not self.pacman.alive:
                self.stop_bg_sounds()
                self.sounds["death"].play()
                print("Pacman DIED")
                self.state = s.STATE_MENU
                self.pacman.alive = True

    def _draw(self):
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
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(s.FPS)
        pg.quit()
