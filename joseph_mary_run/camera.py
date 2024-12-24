"""
Camera management for screen scrolling
"""

from config import *


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def update(self, target):
        # Center the camera on the target
        self.x = target.x - SCREEN_WIDTH // 2
        self.y = target.y - SCREEN_HEIGHT // 2

        # Keep camera within bounds
        self.x = max(0, min(self.x, MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH))
        self.y = max(0, min(self.y, MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT))
