"""
Game sprites including Player and Guard classes
"""

import pygame
import math
from config import *


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.speed = MOVE_SPEED
        self.direction = "down"
        self.moving = False
        self.stamina = STAMINA_MAX
        self.is_hidden = False
        self.tools = []  # List of collected tools
        self.sprites = {
            "down": self.create_sprite("down"),
            "up": self.create_sprite("up"),
            "left": self.create_sprite("left"),
            "right": self.create_sprite("right"),
        }

    def create_sprite(self, direction):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.set_colorkey(BLACK)
        surf.fill(BLACK)

        if direction == "down":
            pygame.draw.circle(
                surf, BROWN, (TILE_SIZE // 2, TILE_SIZE // 3), TILE_SIZE // 6
            )
            pygame.draw.circle(
                surf, BLUE, (TILE_SIZE // 2, 2 * TILE_SIZE // 3), TILE_SIZE // 6
            )
            pygame.draw.circle(
                surf, WHITE, (2 * TILE_SIZE // 3, 2 * TILE_SIZE // 3), TILE_SIZE // 8
            )
        elif direction == "up":
            pygame.draw.circle(
                surf, BLUE, (TILE_SIZE // 2, TILE_SIZE // 3), TILE_SIZE // 6
            )
            pygame.draw.circle(
                surf, BROWN, (TILE_SIZE // 2, 2 * TILE_SIZE // 3), TILE_SIZE // 6
            )
            pygame.draw.circle(
                surf, WHITE, (2 * TILE_SIZE // 3, TILE_SIZE // 3), TILE_SIZE // 8
            )
        elif direction == "left":
            pygame.draw.circle(
                surf, BROWN, (TILE_SIZE // 3, TILE_SIZE // 2), TILE_SIZE // 6
            )
            pygame.draw.circle(
                surf, BLUE, (2 * TILE_SIZE // 3, TILE_SIZE // 2), TILE_SIZE // 6
            )
            pygame.draw.circle(
                surf, WHITE, (2 * TILE_SIZE // 3, TILE_SIZE // 3), TILE_SIZE // 8
            )
        else:  # right
            pygame.draw.circle(
                surf, BLUE, (TILE_SIZE // 3, TILE_SIZE // 2), TILE_SIZE // 6
            )
            pygame.draw.circle(
                surf, BROWN, (2 * TILE_SIZE // 3, TILE_SIZE // 2), TILE_SIZE // 6
            )
            pygame.draw.circle(
                surf, WHITE, (TILE_SIZE // 3, TILE_SIZE // 3), TILE_SIZE // 8
            )
        return surf

    def move(self, dx, dy):
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

        self.moving = dx != 0 or dy != 0
        return (self.x + dx * self.speed, self.y + dy * self.speed)

    def collect_tool(self, tool_type):
        if tool_type not in self.tools:
            self.tools.append(tool_type)
            return True
        return False

    def has_tool(self, tool_type):
        return tool_type in self.tools

    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        screen.blit(self.sprites[self.direction], (screen_x, screen_y))

        # Draw stamina bar
        stamina_width = 50
        stamina_height = 5
        stamina_x = screen_x + (self.width - stamina_width) / 2
        stamina_y = screen_y - 10
        pygame.draw.rect(
            screen, RED, (stamina_x, stamina_y, stamina_width, stamina_height)
        )
        pygame.draw.rect(
            screen,
            GREEN,
            (
                stamina_x,
                stamina_y,
                stamina_width * (self.stamina / STAMINA_MAX),
                stamina_height,
            ),
        )

        # Draw collected tools
        tool_size = 20
        for i, tool in enumerate(self.tools):
            tool_x = 10 + (i * (tool_size + 5))
            tool_y = SCREEN_HEIGHT - tool_size - 10
            pygame.draw.rect(
                screen, TOOLS[tool]["color"], (tool_x, tool_y, tool_size, tool_size)
            )


class Guard:
    def __init__(self, x, y, patrol_route):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.patrol_route = patrol_route
        self.current_point = 0
        self.speed = 2
        self.direction = "right"

    def update(self):
        target = self.patrol_route[self.current_point]
        dx = target[0] - self.x
        dy = target[1] - self.y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance < self.speed:
            self.current_point = (self.current_point + 1) % len(self.patrol_route)
        else:
            dx = dx / distance * self.speed
            dy = dy / distance * self.speed
            self.x += dx
            self.y += dy

            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down" if dy > 0 else "up"

    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y

        pygame.draw.rect(screen, RED, (screen_x, screen_y, self.width, self.height))

        helmet_color = (150, 0, 0)  # Darker red for helmet
        if self.direction == "down":
            pygame.draw.circle(
                screen,
                helmet_color,
                (screen_x + self.width // 2, screen_y + self.height // 4),
                self.width // 4,
            )
        elif self.direction == "up":
            pygame.draw.circle(
                screen,
                helmet_color,
                (screen_x + self.width // 2, screen_y + 3 * self.height // 4),
                self.width // 4,
            )
        elif self.direction == "left":
            pygame.draw.circle(
                screen,
                helmet_color,
                (screen_x + 3 * self.width // 4, screen_y + self.height // 2),
                self.width // 4,
            )
        else:  # right
            pygame.draw.circle(
                screen,
                helmet_color,
                (screen_x + self.width // 4, screen_y + self.height // 2),
                self.width // 4,
            )
