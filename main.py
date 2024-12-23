import pygame
import sys
import os
import asyncio
from santa_vs_grunch import Game as SantaGame

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
HIGHLIGHT = (150, 150, 255)

# For Pygbag web deployment
canvas = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("Arcade Games")


class GameButton:
    def __init__(self, x, y, width, height, text, description):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.description = description
        self.hovered = False

    def draw(self, screen):
        # Draw button background
        color = HIGHLIGHT if self.hovered else GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)  # Border

        # Draw game title
        font = pygame.font.Font(None, 48)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        # Draw description below button
        font = pygame.font.Font(None, 24)
        desc_lines = self.description.split("\n")
        for i, line in enumerate(desc_lines):
            desc_surface = font.render(line, True, WHITE)
            desc_rect = desc_surface.get_rect(
                midtop=(self.rect.centerx, self.rect.bottom + 10 + i * 25)
            )
            screen.blit(desc_surface, desc_rect)


class ArcadeMenu:
    def __init__(self):
        self.screen = canvas  # Use the global canvas for Pygbag
        self.clock = pygame.time.Clock()
        self.running = True

        # Create game buttons
        space_desc = "Navigate through dangerous asteroid fields\nin the year 2157 as an elite Space Defense pilot."
        santa_desc = "Help Santa deliver presents while avoiding\nthe Grunch in this festive platformer!"

        button_width = 300
        button_height = 100
        spacing = 50
        total_width = (button_width * 2) + spacing
        start_x = (SCREEN_WIDTH - total_width) // 2

        self.buttons = [
            GameButton(
                start_x,
                200,
                button_width,
                button_height,
                "Adventures in Space",
                space_desc,
            ),
            GameButton(
                start_x + button_width + spacing,
                200,
                button_width,
                button_height,
                "Santa vs Grunch",
                santa_desc,
            ),
        ]

    async def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for i, button in enumerate(self.buttons):
                        if button.rect.collidepoint(mouse_pos):
                            if i == 0:  # Space game
                                # Import and run space game
                                import adventures_in_space

                                await adventures_in_space.main()
                            else:  # Santa game
                                game = SantaGame()
                                game.run()
                            # After game ends, reset display for menu
                            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                            return False

        # Update button hover states
        for button in self.buttons:
            button.hovered = button.rect.collidepoint(mouse_pos)

        return False

    def draw(self):
        self.screen.fill(BLACK)

        # Draw title
        font = pygame.font.Font(None, 74)
        title = font.render("Arcade Games", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)

        # Draw instructions at bottom
        font = pygame.font.Font(None, 36)
        instructions = font.render("Click a game to play!", True, WHITE)
        instructions_rect = instructions.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        )
        self.screen.blit(instructions, instructions_rect)

        pygame.display.flip()

    async def run(self):
        while self.running:
            self.clock.tick(FPS)
            should_quit = await self.handle_events()
            if should_quit:
                break
            self.draw()
            # Add small delay to prevent browser from freezing
            await asyncio.sleep(0)


async def main():
    # Pygbag requires this function
    menu = ArcadeMenu()
    await menu.run()


# Pygbag entry point
if __name__ == "__main__":
    asyncio.run(main())
