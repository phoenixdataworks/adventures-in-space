"""
Game configuration and constants
"""

# Screen and tile settings
TILE_SIZE = 32
MAP_WIDTH = 40  # tiles
MAP_HEIGHT = 30  # tiles
SCREEN_WIDTH = TILE_SIZE * 20  # Show 20 tiles horizontally
SCREEN_HEIGHT = TILE_SIZE * 15  # Show 15 tiles vertically
FPS = 60

# Game physics
GRAVITY = 0.5
MOVE_SPEED = 4
STAMINA_MAX = 100
STAMINA_DRAIN = 0.2
STAMINA_REGEN = 0.1

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
SAND_COLOR = (194, 178, 128)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Game States
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
LEVEL_COMPLETE = "level_complete"

# Tile types
TILE_TYPES = {
    ".": "floor",  # Empty floor
    "#": "wall",  # Wall
    "G": "guard",  # Roman guard
    "T": "tree",  # Tree/obstacle
    "D": "door",  # Door/passage
    "E": "exit",  # Level exit
    "P": "player",  # Player start position
    "W": "water",  # Water obstacle
    "R": "rock",  # Movable rock
    "L": "locked",  # Locked door
    "K": "key",  # Key for locked doors
    "H": "hiding",  # Hiding spot (bush/shadow)
    "C": "climbable",  # Climbable wall
    "S": "scroll",  # Scroll with hints/story
    "M": "market",  # Market stall to hide in
    "B": "boat",  # Boat for water crossing
}

# Tools and their effects
TOOLS = {
    "key": {"color": YELLOW, "use": "Opens locked doors", "symbol": "K"},
    "rope": {"color": BROWN, "use": "Climb certain walls", "symbol": "R"},
    "water_skin": {"color": BLUE, "use": "Cross desert areas", "symbol": "W"},
    "cloak": {"color": PURPLE, "use": "Better hiding in shadows", "symbol": "C"},
    "map": {"color": SAND_COLOR, "use": "Shows guard patrol routes", "symbol": "M"},
}

# Obstacle types and required tools
OBSTACLES = {
    "locked_door": {"required_tool": "key", "symbol": "L"},
    "high_wall": {"required_tool": "rope", "symbol": "C"},
    "desert": {"required_tool": "water_skin", "symbol": "D"},
    "guard_post": {"required_tool": "cloak", "symbol": "G"},
    "maze": {"required_tool": "map", "symbol": "M"},
}
