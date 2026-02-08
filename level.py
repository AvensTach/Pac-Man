import pygame as pg
from settings import (
    LAYOUT,
    TILE_SIZE,
    WALL_COLOR,
    BORDER_COLOR,
    BORDER_WIDTH,
    COIN_COLOR,
    COIN_RADIUS,
    SCORE_FONT_SIZE,
    SCORE_PREFIX,
    SCORE_COLOR,
    SCORE_POSITION
)

class Level:
    def __init__(self):
        self.layout = LAYOUT
        self.coins = set()
        self.score = 0
        self.spawn_coins()

    def is_wall(self, r, c):
        if r < 0 or c < 0:
            return False
        if r >= len(self.layout) or c >= len(self.layout[0]):
            return False
        return self.layout[r][c] == "1"

    def draw_wall(self, screen, row, col):
        x = col * TILE_SIZE
        y = row * TILE_SIZE
        r = TILE_SIZE
    
        # wall background
        pg.draw.rect(screen, WALL_COLOR, (x, y, r, r))
    
        # left
        if not self.is_wall(row, col - 1):
            pg.draw.line(screen, BORDER_COLOR, (x, y), (x, y + r), BORDER_WIDTH)
    
        # right
        if not self.is_wall(row, col + 1):
            pg.draw.line(screen, BORDER_COLOR, (x + r, y), (x + r, y + r), BORDER_WIDTH)
    
        # top
        if not self.is_wall(row - 1, col):
            pg.draw.line(screen, BORDER_COLOR, (x, y), (x + r, y), BORDER_WIDTH)
    
        # bottom
        if not self.is_wall(row + 1, col):
            pg.draw.line(screen, BORDER_COLOR, (x, y + r), (x + r, y + r), BORDER_WIDTH)
    
    def spawn_coins(self):
        for r in range(len(self.layout)):
            for c in range(len(self.layout[r])):
                if self.layout[r][c] == "0":
                    self.coins.add((r, c))        

    def draw_coins(self, screen):
        for r, c in self.coins:
            cx = c * TILE_SIZE + TILE_SIZE // 2
            cy = r * TILE_SIZE + TILE_SIZE // 2
            pg.draw.circle(screen, COIN_COLOR, (cx, cy), COIN_RADIUS)

    def draw(self, screen):
        for r in range(len(self.layout)):
            for c in range(len(self.layout[r])):
                if self.layout[r][c] == "1":
                    self.draw_wall(screen, r, c)
                    
        self.draw_coins(screen)
    
    def draw_ui(self, screen):
        font = pg.font.SysFont(None, SCORE_FONT_SIZE)
        score_text = font.render(
            f"{SCORE_PREFIX}{self.score}",
            True,
            SCORE_COLOR
        )
        screen.blit(score_text, SCORE_POSITION)
    

 