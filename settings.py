from enum import Enum

class GhostType(Enum):
    BLINKY = (255, 0, 0)  # Red
    PINKY = (255, 182, 255)  # Pink
    INKY = (0, 255, 255)  # Cyan
    CLYDE = (255, 182, 85)  # Orange

class Direction(Enum):
    STOP = (0, 0)
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


BASE_SPEED = 2

SCREEN_WIDTH = 760
SCREEN_HEIGHT = 760