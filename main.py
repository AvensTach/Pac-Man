import pygame as pg
from level import Level

level = Level()
print(len(level.walls), len(level.floors))

pg.init()

SCREEN_WIDTH = 760
SCREEN_HEIGHT = 760

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Pacman")

clock = pg.time.Clock()
running = True

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill((0, 0, 0))
    pg.display.flip()
    clock.tick(60)

pg.quit()

