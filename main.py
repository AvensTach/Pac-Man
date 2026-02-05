import random
import ghosts
import pygame as pg
import settings as s
from level import Level

level = Level()
print(len(level.walls), len(level.floors))

pg.init()

screen = pg.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
pg.display.set_caption("Pacman")

clock = pg.time.Clock()
running = True

# ghosts
# coordinates are random for tets
blinky = ghosts.Ghost(random.randint(0, 760), random.randint(0, 760), s.GhostType.BLINKY)
pinky = ghosts.Ghost(random.randint(0, 760), random.randint(0, 760), s.GhostType.PINKY)
inky = ghosts.Ghost(random.randint(0, 760), random.randint(0, 760), s.GhostType.INKY)
clyde = ghosts.Ghost(random.randint(0, 760), random.randint(0, 760), s.GhostType.CLYDE)

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill((0, 0, 0))

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

    pg.display.flip()
    clock.tick(60)

pg.quit()
