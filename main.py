import random
import ghosts
import PacMan
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

#Pacman spawned on tiles
pr, pc = random_empty_tile()
pacman = PacMan.Pacman(pr, pc)

# ghosts spawned on tiles
br, bc= random_empty_tile()
blinky = ghosts.Ghost(br, bc, s.GhostType.BLINKY, level)
pr, pc = random_empty_tile()
pinky = ghosts.Ghost(pr, pc, s.GhostType.PINKY, level)
ir, ic = random_empty_tile()
inky = ghosts.Ghost(ir, ic, s.GhostType.INKY, level)
cr, cc = random_empty_tile()
clyde = ghosts.Ghost(cr, cc, s.GhostType.CLYDE, level)

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
    blinky.update()
    pinky.update()
    inky.update()
    clyde.update()

    # update pacman
    pacman.update(s.LAYOUT)

    pacman.check_ghost_collision([blinky, pinky, inky, clyde])
    if not pacman.alive:
        print("Pacman DIED")
        running = False


    pg.display.flip()
    clock.tick(s.FPS)

pg.quit()
