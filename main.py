import random
import ghosts
import pacman
import pygame as pg
import settings as s
from level import Level


pg.init()

screen = pg.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
pg.display.set_caption("Pacman")

clock = pg.time.Clock()
running = True

level = Level()


def random_empty_tile() -> tuple:
    """ helper to find a random empty tile """
    while True:
        r: int = random.randint(0, s.ROWS - 1)
        c: int = random.randint(0, s.COLS - 1)
        if not level.is_wall(r, c):
            return r, c

# --- Pacman Spawn (Standard Position) ---
pacman = pacman.Pacman(15, 9)

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
        pacman.handle_input(event)

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
        running = False

    level.draw_ui(screen)

    pg.display.flip()
    clock.tick(s.FPS)

pg.quit()