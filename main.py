import random
import ghosts
from pacman import Pacman
import pygame as pg
import settings as s
from level import Level
from menu import MainMenuScreen, SettingsScreen

pg.init()

screen = pg.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
pg.display.set_caption("Pacman")

clock = pg.time.Clock()
running = True

state = s.STATE_MENU

# --- State management functions ---
def start_game():
    global state
    reset_game()
    state = s.STATE_PLAYING

def open_settings():
    global state
    state = s.STATE_SETTINGS

def open_menu():
    global state
    state = s.STATE_MENU

def quit_game():
    global running
    running = False

# --- menu screens ---
menu_screen = MainMenuScreen(on_play=start_game, on_exit=quit_game, on_settings=open_settings)
settings_screen = SettingsScreen(on_back=open_menu)



def random_empty_tile() -> tuple:
    """ helper to find a random empty tile """
    while True:
        r: int = random.randint(0, s.ROWS - 1)
        c: int = random.randint(0, s.COLS - 1)
        if not level.is_wall(r, c):
            return r, c
def reset_game():
    global pacman, blinky, pinky, inky, clyde, ghosts_list, level
    
    # Create a new level
    level = Level()
    # --- Pacman Spawn (Standard Position) ---
    pacman = Pacman(15, 9)

    # --- Ghost Spawns (Ghost House) ---
    # Blinky: Outside house, active immediately
    blinky = ghosts.Ghost(7, 9, s.GhostType.BLINKY, level, spawn_delay=0)

    # Pinky: Center of house, 2 second delay
    pinky = ghosts.Ghost(9, 9, s.GhostType.PINKY, level, spawn_delay=2)

    # Inky: Left side of house, 4 second delay
    inky = ghosts.Ghost(9, 8, s.GhostType.INKY, level, spawn_delay=4)

    # Clyde: Right side of house, 6 second delay
    clyde = ghosts.Ghost(9, 10, s.GhostType.CLYDE, level, spawn_delay=6)

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        # Distribution of events depending on the state
        if state == s.STATE_MENU:
            menu_screen.handle_event(event)
        elif state == s.STATE_SETTINGS:
            settings_screen.handle_event(event)
        elif state == s.STATE_PLAYING:
            pacman.handle_input(event)

    if state == s.STATE_MENU:
        menu_screen.draw(screen)
        
    elif state == s.STATE_SETTINGS:
        settings_screen.draw(screen)
        
    elif state == s.STATE_PLAYING:
        # Level drawing
        screen.fill(s.WALL_COLOR)
        level.draw(screen)

        # draw pacman
        pacman.draw(screen)

        # draw ghosts
        blinky.draw(screen)
        pinky.draw(screen)
        inky.draw(screen)
        clyde.draw(screen)

        # update ghosts' position
        blinky.update(pacman)
        pinky.update(pacman)
        inky.update(pacman)
        clyde.update(pacman)

        # update pacman
        pacman.update(s.LAYOUT, level)
        ghosts_list = [blinky, pinky, inky, clyde]

        level.check_pills(pacman, ghosts_list)

        pacman.check_ghost_collision([blinky, pinky, inky, clyde])
        if not pacman.alive:
            print("Pacman DIED")
            state = s.STATE_MENU      # Return to the menu
            pacman.alive = True

        level.draw_ui(screen)

    pg.display.flip()
    clock.tick(s.FPS)

pg.quit()