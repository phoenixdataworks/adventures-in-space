"""
Level management and map data
"""

import pygame
from config import *
from sprites import Guard

# Define the five progressive levels
LEVEL_1_MAP = [
    "########################################",
    "#..P.........#.......#................#",
    "#............#.......#................#",
    "#............#...G...#................#",
    "#............#.......#................#",
    "#............#.......#................#",
    "#####..######.......#................#",
    "#####..######.......#................#",
    "#........................#...........#",
    "#........................#....G......#",
    "#........................#...........#",
    "#........................L...........#",
    "#........................#...........#",
    "#####...##################...........#",
    "#......................................#",
    "#......................................#",
    "#.........G............................#",
    "#......................................#",
    "#...................K..................#",
    "#......................................#",
    "#......................................#",
    "#......................................#",
    "#.......................G.............#",
    "#......................................#",
    "#......................................#",
    "#......................................#",
    "#....................................E#",
    "#....................................E#",
    "########################################",
]

LEVEL_2_MAP = [
    "########################################",
    "#..P...............#..................#",
    "#..................#..................#",
    "#..................#........G........#",
    "#..................#..................#",
    "######..########...#..................#",
    "######C.########...#..................#",
    "#..................#..................#",
    "#........G.........#...........G....#",
    "#..................#..................#",
    "#..................#..................#",
    "#.........R........#..................#",
    "######..##########.#..................#",
    "#..................#..................#",
    "#..................#..................#",
    "#.................###.................#",
    "#........G...........................#",
    "#...................r...............E#",
    "#.................................E..#",
    "########################################",
]

LEVEL_3_MAP = [
    "########################################",
    "#P.....................................#",
    "#......................................#",
    "#......................................#",
    "###W##W##W##W##........................#",
    "#......................................#",
    "#...............G......................#",
    "#......................................#",
    "#....................###W##W##W##W###.#",
    "#....................s..................#",
    "#...................G..................#",
    "#......................................#",
    "#......................................#",
    "#.###W##W##W##W###....................#",
    "#......................................#",
    "#......................................#",
    "#...............G......................#",
    "#....................................E#",
    "#....................................E#",
    "########################################",
]

LEVEL_4_MAP = [
    "########################################",
    "#P.................#...................#",
    "#..................#...................#",
    "#........G........#...................#",
    "#..................L...................#",
    "#..................#...................#",
    "######..########..##...................#",
    "######H.########..#...................#",
    "#..................#...................#",
    "#........G........#..........G.......#",
    "#..................#...................#",
    "#..................#...................#",
    "#........c........#...................#",
    "######..##########.#...................#",
    "#..................#...................#",
    "#..................#...................#",
    "#..................#...................#",
    "#........G........###................E#",
    "#.....................................E#",
    "########################################",
]

LEVEL_5_MAP = [
    "########################################",
    "#P.....................................#",
    "#......................................#",
    "#...............#####..................#",
    "#...............#...#..................#",
    "#...............#.K.#..................#",
    "#...............#...#..................#",
    "#...............#...#..................#",
    "####L##########.#...#..................#",
    "#...............#...#..................#",
    "#...............#...#.........G.......#",
    "#........G......#...#..................#",
    "#...............#...#..................#",
    "#...............#...#..................#",
    "#...............#.m.#..................#",
    "####L##########.#...#..................#",
    "#...............#...#................E#",
    "#...............#...#................E#",
    "########################################",
]

# Level Definitions with progressive complexity
LEVELS = {
    1: {
        "name": "Streets of Bethlehem",
        "description": "Find the key to unlock the gate. Watch out for guards!",
        "mechanics": ["key_doors"],
        "map": LEVEL_1_MAP,
        "required_tools": ["key"],
    },
    2: {
        "name": "City Walls",
        "description": "Use the rope to climb walls and move rocks to create paths.",
        "mechanics": ["climbing", "pushing"],
        "map": LEVEL_2_MAP,
        "required_tools": ["rope"],
    },
    3: {
        "name": "Desert Crossing",
        "description": "Cross the desert carefully. Water skins are essential.",
        "mechanics": ["water_management"],
        "map": LEVEL_3_MAP,
        "required_tools": ["water_skin"],
    },
    4: {
        "name": "Guard Posts",
        "description": "Use the cloak to hide in shadows and avoid detection.",
        "mechanics": ["stealth", "hiding"],
        "map": LEVEL_4_MAP,
        "required_tools": ["cloak"],
    },
    5: {
        "name": "Palace Maze",
        "description": "Navigate the complex maze. The map will reveal guard patterns.",
        "mechanics": ["maze", "timing"],
        "map": LEVEL_5_MAP,
        "required_tools": ["map", "key"],
    },
}


class Level:
    def __init__(self, level_data):
        self.tiles = []
        self.guards = []
        self.tools = []  # List of available tools in the level
        self.obstacles = []  # List of obstacles in the level
        self.player_start = (0, 0)
        self.load_map(level_data)

    def load_map(self, level_data):
        for y, row in enumerate(level_data):
            tile_row = []
            for x, tile in enumerate(row):
                pos = (x * TILE_SIZE, y * TILE_SIZE)
                if tile == "P":
                    self.player_start = pos
                    tile_row.append(".")
                elif tile == "G":
                    patrol_route = [
                        pos,
                        (x * TILE_SIZE, (y + 4) * TILE_SIZE),
                        ((x + 4) * TILE_SIZE, (y + 4) * TILE_SIZE),
                        ((x + 4) * TILE_SIZE, y * TILE_SIZE),
                    ]
                    self.guards.append(Guard(pos[0], pos[1], patrol_route))
                    tile_row.append(".")
                elif tile == "K":  # Special handling for key
                    self.tools.append({"type": "key", "pos": pos})
                    tile_row.append(".")
                elif tile == "r":  # Special handling for rope
                    self.tools.append({"type": "rope", "pos": pos})
                    tile_row.append(".")
                elif tile == "s":  # Special handling for water skin
                    self.tools.append({"type": "water_skin", "pos": pos})
                    tile_row.append(".")
                elif tile == "c":  # Special handling for cloak
                    self.tools.append({"type": "cloak", "pos": pos})
                    tile_row.append(".")
                elif tile == "m":  # Special handling for map
                    self.tools.append({"type": "map", "pos": pos})
                    tile_row.append(".")
                elif tile == "R":  # Rock obstacle
                    self.obstacles.append({"type": "rock", "pos": pos})
                    tile_row.append("R")
                elif tile in TOOLS:
                    self.tools.append({"type": tile, "pos": pos})
                    tile_row.append(".")
                elif tile in [obs["symbol"] for obs in OBSTACLES.values()]:
                    self.obstacles.append({"type": tile, "pos": pos})
                    tile_row.append(tile)
                else:
                    tile_row.append(tile)
            self.tiles.append(tile_row)

    def get_tile(self, x, y):
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        if 0 <= tile_x < len(self.tiles[0]) and 0 <= tile_y < len(self.tiles):
            return self.tiles[tile_y][tile_x]
        return "#"  # Treat out of bounds as walls

    def is_wall(self, x, y):
        return self.get_tile(x, y) == "#"

    def is_obstacle(self, x, y):
        tile = self.get_tile(x, y)
        return tile in [obs["symbol"] for obs in OBSTACLES.values()]

    def can_pass_obstacle(self, x, y, player_tools):
        tile = self.get_tile(x, y)
        for obs_type, obs_data in OBSTACLES.items():
            if obs_data["symbol"] == tile:
                return obs_data["required_tool"] in player_tools
        return True

    def update(self):
        for guard in self.guards:
            guard.update()

    def draw(self, screen, camera):
        # Draw tiles
        start_x = max(0, int(camera.x // TILE_SIZE))
        end_x = min(
            len(self.tiles[0]) if self.tiles else 0,
            int((camera.x + SCREEN_WIDTH) // TILE_SIZE + 1),
        )
        start_y = max(0, int(camera.y // TILE_SIZE))
        end_y = min(
            len(self.tiles) if self.tiles else 0,
            int((camera.y + SCREEN_HEIGHT) // TILE_SIZE + 1),
        )

        for y in range(start_y, end_y):
            if 0 <= y < len(self.tiles):
                for x in range(start_x, end_x):
                    if 0 <= x < len(self.tiles[y]):
                        screen_x = x * TILE_SIZE - camera.x
                        screen_y = y * TILE_SIZE - camera.y
                        tile = self.tiles[y][x]

                        # Draw base tiles
                        if tile == "#":
                            pygame.draw.rect(
                                screen, GRAY, (screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                            )
                        elif tile == ".":
                            pygame.draw.rect(
                                screen,
                                (200, 200, 200),
                                (screen_x, screen_y, TILE_SIZE, TILE_SIZE),
                            )
                        elif tile == "E":
                            pygame.draw.rect(
                                screen,
                                GREEN,
                                (screen_x, screen_y, TILE_SIZE, TILE_SIZE),
                            )

                        # Draw special tiles
                        if tile in TOOLS:
                            tool_data = TOOLS[tile]
                            pygame.draw.rect(
                                screen,
                                tool_data["color"],
                                (
                                    screen_x + 4,
                                    screen_y + 4,
                                    TILE_SIZE - 8,
                                    TILE_SIZE - 8,
                                ),
                            )
                        elif tile in [obs["symbol"] for obs in OBSTACLES.values()]:
                            pygame.draw.rect(
                                screen,
                                RED,
                                (
                                    screen_x + 2,
                                    screen_y + 2,
                                    TILE_SIZE - 4,
                                    TILE_SIZE - 4,
                                ),
                            )

        # Draw guards
        for guard in self.guards:
            guard.draw(screen, camera)

        # Draw tools
        for tool in self.tools:
            screen_x = tool["pos"][0] - camera.x
            screen_y = tool["pos"][1] - camera.y
            tool_data = TOOLS[tool["type"]]
            pygame.draw.rect(
                screen,
                tool_data["color"],
                (screen_x + 4, screen_y + 4, TILE_SIZE - 8, TILE_SIZE - 8),
            )
