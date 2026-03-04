import random
import ghosts
import pacman
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

level = Level()

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

    #Pacman spawned on tiles
    pr, pc = random_empty_tile()
    pacman = pacman.Pacman(pr, pc)

    # ghosts spawned on tiles
    br, bc= random_empty_tile()
    blinky = ghosts.Ghost(br, bc, s.GhostType.BLINKY, level)
    pr, pc = random_empty_tile()
    pinky = ghosts.Ghost(pr, pc, s.GhostType.PINKY, level)
    ir, ic = random_empty_tile()
    inky = ghosts.Ghost(ir, ic, s.GhostType.INKY, level)
    cr, cc = random_empty_tile()
    clyde = ghosts.Ghost(cr, cc, s.GhostType.CLYDE, level)

    ghosts_list = [blinky, pinky, inky, clyde]

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
        # 1. LOGIC PROCESSING
        pacman.update(s.LAYOUT, level)
        
        blinky.update(pacman)
        pinky.update(pacman)
        inky.update(pacman)
        clyde.update(pacman)

        # Collision check
        pacman.check_ghost_collision([blinky, pinky, inky, clyde])
        
        if not pacman.alive:
            print("Pacman DIED")
            state = s.STATE_MENU      # Return to the menu
            pacman.alive = True

        # 2. DRAWING
        screen.fill(s.WALL_COLOR) # Background (color from settings)
        level.draw(screen)
        
        pacman.draw(screen)
        
        blinky.draw(screen)
        pinky.draw(screen)
        inky.draw(screen)
        clyde.draw(screen)

        level.draw_ui(screen)


    pg.display.flip()
    clock.tick(s.FPS)

pg.quit()
