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

LAYOUT = [
    "1111111111111111111",
    "1000000001000000001",
    "1011011101011101101",
    "1000000000000000001",
    "1011010111110101101",
    "1000010001000100001",
    "1111011101011101111",
    "1111010000000101111",
    "111101011=110101111",
    "00000001---10000000",  # '---' is tiles that must be empty (without coins)
    "1111010111110101111",
    "1111010000000101111",
    "1111010111110101111",
    "1000000001000000001",
    "1011011101011101101",
    "1001000000000001001",
    "1101010111110101011",
    "1000010001000100001",
    "1011111101011111101",
    "1000000000000000001",
    "1111111111111111111"
]

TILE_SIZE = 32

ROWS = len(LAYOUT)
COLS = len(LAYOUT[0])

SCREEN_WIDTH = COLS * TILE_SIZE
SCREEN_HEIGHT = ROWS * TILE_SIZE

WALL_COLOR = (0, 0, 0)
BORDER_COLOR = (0, 0, 255)
BORDER_WIDTH = 3
RADIUS = 10
FPS = 60

# coins
COIN_COLOR = (255, 215, 0)
COIN_RADIUS = 3
COIN_SCORE_VALUE = 10

# pills
PILL_COLOR = (255, 255, 255)
PILL_RADIUS = 10
PILL_SCORE_VALUE = 50
PILL_BLINK_SPEED = 10
PILL_FRIGHT_TIME = 300

# score
SCORE_FONT_SIZE = 36
SCORE_COLOR = (255, 255, 255)
SCORE_POSITION = (10, 10)
SCORE_PREFIX = ""

# ghosts
GHOST_BLINK_TICKS = (1, 2, 3, 4, 5)
GHOST_BLINKING_DURATION = PILL_FRIGHT_TIME / 3  # 1/3 of the frightened time
GHOST_SPEED_MULTIPLIER = 0.9

# states
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_SETTINGS = "STATE_SETTINGS"

# UI helpers Menu
SHADOW = (0, 0, 0)
TEXT = (245, 245, 255)
TEXT_MUTED = (180, 180, 210)
PANEL_COLOR = (10, 10, 24)
BTN_FILL = (18, 18, 40)
BTN_FILL_HOVER = (28, 28, 60)
ACCENT = (0, 130, 255)
ACCENT_SOFT = (0, 90, 190)

# Sounds
sound_files = {
    "intro": "intro.wav",
    "munch": "munch.wav",
    "eat_ghost": "eat_ghost.wav",
    "death": "death.wav",
    "siren": "siren.wav",  # Normal ghost movement (loop)
    "frightened": "frightened.wav"  # Blue ghost movement (loop)
}

CONFIG = {
    "MUSIC_ON": True,
    "SFX_ON": True
}