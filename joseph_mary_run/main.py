"""
Main game loop and initialization
PYGBAG_REQUIRE=pygame,asyncio,platform,json,math,random,time,os
"""

import pygame
import asyncio
from config import *
from sprites import Player
from level import Level, LEVELS
from camera import Camera

# Initialize Pygame and its sound mixer
pygame.init()
pygame.mixer.init()


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Journey to Egypt")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU
        self.current_level = 1
        self.reset_game()

    def reset_game(self):
        self.level = Level(LEVELS[self.current_level]["map"])
        self.player = Player(*self.level.player_start)
        self.camera = Camera()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.state == MENU:
                        self.state = PLAYING
                        self.reset_game()
                    elif self.state == GAME_OVER:
                        self.state = MENU
                    elif self.state == LEVEL_COMPLETE:
                        self.current_level += 1
                        if self.current_level > len(LEVELS):
                            self.state = MENU
                            self.current_level = 1
                        else:
                            self.state = PLAYING
                            self.reset_game()

    def update(self):
        if self.state == PLAYING:
            # Handle movement
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_LEFT]:
                dx = -1
            elif keys[pygame.K_RIGHT]:
                dx = 1
            if keys[pygame.K_UP]:
                dy = -1
            elif keys[pygame.K_DOWN]:
                dy = 1

            # Get new position
            new_pos = self.player.move(dx, dy)

            # Check for collisions with walls and obstacles
            can_move = True
            for check_x in [new_pos[0], new_pos[0] + self.player.width]:
                for check_y in [new_pos[1], new_pos[1] + self.player.height]:
                    if self.level.is_wall(check_x, check_y):
                        can_move = False
                    elif self.level.is_obstacle(check_x, check_y):
                        if not self.level.can_pass_obstacle(
                            check_x, check_y, self.player.tools
                        ):
                            can_move = False

            if can_move:
                self.player.x = new_pos[0]
                self.player.y = new_pos[1]

            # Check for tool collection
            player_center_x = self.player.x + self.player.width / 2
            player_center_y = self.player.y + self.player.height / 2

            # Create a copy of the tools list to avoid modifying while iterating
            tools_to_remove = []
            for tool in self.level.tools:
                tool_x = tool["pos"][0] + TILE_SIZE / 2
                tool_y = tool["pos"][1] + TILE_SIZE / 2
                if (
                    abs(tool_x - player_center_x) < TILE_SIZE
                    and abs(tool_y - player_center_y) < TILE_SIZE
                ):
                    if self.player.collect_tool(tool["type"]):
                        tools_to_remove.append(tool)

            # Remove collected tools
            for tool in tools_to_remove:
                self.level.tools.remove(tool)

            # Update level (guards, etc.)
            self.level.update()

            # Check for collisions with guards
            for guard in self.level.guards:
                if (
                    abs(guard.x - self.player.x) < TILE_SIZE
                    and abs(guard.y - self.player.y) < TILE_SIZE
                ):
                    if not (self.player.has_tool("cloak") and self.player.is_hidden):
                        self.state = GAME_OVER

            # Update camera to follow player
            self.camera.update(self.player)

            # Check for level exit
            if (
                self.level.get_tile(
                    self.player.x + TILE_SIZE / 2, self.player.y + TILE_SIZE / 2
                )
                == "E"
            ):
                # Check if player has all required tools for the level
                required_tools = LEVELS[self.current_level]["required_tools"]
                has_all_tools = all(
                    self.player.has_tool(tool) for tool in required_tools
                )
                if has_all_tools:
                    self.state = LEVEL_COMPLETE

    def draw_menu(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        title = font.render("Journey to Egypt", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 200))

        font = pygame.font.Font(None, 36)
        prompt = font.render("Press ENTER to Start", True, WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH / 2 - prompt.get_width() / 2, 400))

        font = pygame.font.Font(None, 24)
        instructions = [
            "Use Arrow Keys to move",
            "Avoid the Roman guards",
            "Find the exit to complete each level",
            "Stay in the shadows to remain hidden",
        ]
        for i, text in enumerate(instructions):
            instruction = font.render(text, True, WHITE)
            self.screen.blit(
                instruction,
                (SCREEN_WIDTH / 2 - instruction.get_width() / 2, 450 + i * 30),
            )

    def draw_game(self):
        self.screen.fill(BLACK)
        self.level.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)

        # Draw HUD
        font = pygame.font.Font(None, 36)
        level_text = font.render(
            f"Level {self.current_level}: {LEVELS[self.current_level]['name']}",
            True,
            WHITE,
        )
        self.screen.blit(level_text, (10, 10))

        # Draw level description
        font = pygame.font.Font(None, 24)
        desc_text = font.render(LEVELS[self.current_level]["description"], True, WHITE)
        self.screen.blit(desc_text, (10, 40))

        # Draw required tools
        required_tools = LEVELS[self.current_level]["required_tools"]
        font = pygame.font.Font(None, 20)
        tools_text = font.render("Required Tools:", True, WHITE)
        self.screen.blit(tools_text, (10, SCREEN_HEIGHT - 60))

        for i, tool in enumerate(required_tools):
            tool_text = font.render(
                tool, True, GREEN if self.player.has_tool(tool) else RED
            )
            self.screen.blit(tool_text, (100 + i * 80, SCREEN_HEIGHT - 60))

    def draw_game_over(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        title = font.render("Caught by Guards!", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 200))

        font = pygame.font.Font(None, 36)
        prompt = font.render("Press ENTER to Try Again", True, WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH / 2 - prompt.get_width() / 2, 400))

    def draw_level_complete(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        title = font.render("Level Complete!", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 200))

        if self.current_level < len(LEVELS):
            font = pygame.font.Font(None, 36)
            prompt = font.render("Press ENTER for Next Level", True, WHITE)
            self.screen.blit(prompt, (SCREEN_WIDTH / 2 - prompt.get_width() / 2, 400))
        else:
            font = pygame.font.Font(None, 36)
            prompt = font.render(
                "Congratulations! You've completed the game!", True, WHITE
            )
            self.screen.blit(prompt, (SCREEN_WIDTH / 2 - prompt.get_width() / 2, 400))

    def draw(self):
        if self.state == MENU:
            self.draw_menu()
        elif self.state == PLAYING:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game_over()
        elif self.state == LEVEL_COMPLETE:
            self.draw_level_complete()

        pygame.display.flip()

    async def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            await asyncio.sleep(0)
            self.clock.tick(FPS)


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
