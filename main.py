import pygame
import sys
import os
import asyncio
import platform
from santa_vs_grunch import Game as SantaGame

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Game States
MENU = "menu"
SPACE_GAME = "space"
SANTA_GAME = "santa"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
HIGHLIGHT = (150, 150, 255)

# For Pygbag web deployment
canvas = pygame.display.set_mode(
    [SCREEN_WIDTH, SCREEN_HEIGHT], pygame.SCALED | pygame.RESIZABLE
)
pygame.display.set_caption("Arcade Games")


def is_web():
    return platform.system() == "Emscripten"


async def handle_resize():
    """Handle window resize events"""
    if is_web():
        import javascript

        canvas = pygame.display.get_surface()
        w = javascript.window.innerWidth
        h = javascript.window.innerHeight
        pygame.display.set_mode([w, h], pygame.SCALED | pygame.RESIZABLE)


async def load_game():
    """Simulate loading process and update the loading screen"""
    if is_web():
        try:
            import javascript

            steps = [
                (20, "Loading game engine..."),
                (40, "Loading assets..."),
                (60, "Initializing games..."),
                (80, "Preparing menu..."),
                (100, "Ready to play!"),
            ]

            for progress, message in steps:
                await asyncio.sleep(0.3)
                javascript.eval(f'window.updateLoading({progress}, "{message}")')
        except ImportError:
            pass  # Not in web environment

    return True


class GameButton:
    def __init__(self, x, y, width, height, text, description):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.description = description
        self.hovered = False

    def draw(self, screen):
        color = HIGHLIGHT if self.hovered else GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

        font = pygame.font.Font(None, 48)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

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
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_game = MENU

        button_width = 300
        button_height = 100
        spacing = 50
        total_width = (button_width * 2) + spacing
        start_x = (SCREEN_WIDTH - total_width) // 2

        space_desc = "Navigate through dangerous asteroid fields\nin the year 2157 as an elite Space Defense pilot."
        santa_desc = "Help Santa deliver presents while avoiding\nthe Grunch in this festive platformer!"

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
        await handle_resize()  # Handle window resizing
        self.screen = pygame.display.get_surface()  # Update screen reference
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return True

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, button in enumerate(self.buttons):
                    if button.rect.collidepoint(mouse_pos):
                        if i == 0:  # Space game
                            self.current_game = SPACE_GAME
                            import adventures_in_space

                            await adventures_in_space.main()
                            self.current_game = MENU
                        else:  # Santa game
                            self.current_game = SANTA_GAME
                            game = SantaGame()
                            await game.run()
                            self.current_game = MENU

                        # Reset display after game ends
                        pygame.display.set_mode(
                            [SCREEN_WIDTH, SCREEN_HEIGHT],
                            pygame.SCALED | pygame.RESIZABLE,
                        )
                        pygame.display.set_caption("Arcade Games")

        # Update button hover states only in menu
        if self.current_game == MENU:
            for button in self.buttons:
                button.hovered = button.rect.collidepoint(mouse_pos)

        return False

    def draw(self):
        if self.current_game == MENU:
            self.screen.fill(BLACK)

            font = pygame.font.Font(None, 74)
            title = font.render("Arcade Games", True, WHITE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
            self.screen.blit(title, title_rect)

            for button in self.buttons:
                button.draw(self.screen)

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
            if self.current_game == MENU:
                self.draw()
            await asyncio.sleep(0)


async def main():
    # Wait for loading screen
    await load_game()

    # Create and run menu
    menu = ArcadeMenu()
    await menu.run()
    return 0  # Explicit return for Pygbag


# Handle both desktop and web contexts properly
if __name__ == "__main__":
    asyncio.run(main())
else:
    # For web deployment
    loop = asyncio.get_event_loop()
    if not loop.is_running():
        loop.create_task(main())
        try:
            loop.run_forever()
        except RuntimeError:
            pass  # Handle case where loop is already running
