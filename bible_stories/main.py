"""
PYGBAG_REQUIRE=pygame,asyncio,platform,json,math,random,time,os
"""

import pygame
import random
import math
import os
import asyncio

# Initialize Pygame and its sound mixer
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_POWER = -12
MOVE_SPEED = 5
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

# Game States
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
LEVEL_COMPLETE = "level_complete"

# Level Definitions
LEVELS = {
    1: {
        "name": "Escape from Bethlehem",
        "background": "night_city",
        "obstacles": ["patrol", "crate", "market_stall"],
        "mechanics": ["stealth"],
    },
    2: {
        "name": "Wilderness of Judea",
        "background": "desert",
        "obstacles": ["ravine", "cave", "rock"],
        "mechanics": ["stamina"],
    },
    3: {
        "name": "Mountain Pass",
        "background": "mountains",
        "obstacles": ["falling_rock", "bridge", "cliff"],
        "mechanics": ["wind"],
    },
    4: {
        "name": "Coastal Route",
        "background": "coast",
        "obstacles": ["patrol_boat", "beach_guard", "tide"],
        "mechanics": ["tides"],
    },
    5: {
        "name": "Nile Delta",
        "background": "river",
        "obstacles": ["crocodile", "quicksand", "reeds"],
        "mechanics": ["stealth", "swimming"],
    },
}


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT

    def apply(self, entity):
        return (entity.x - self.x, entity.y)

    def update(self, target):
        # Keep the target (player) at 1/3 of the screen when moving right
        target_x = target.x - (SCREEN_WIDTH // 3)

        # Only scroll after passing the first soldier (at x=300)
        if target.x > 300:
            self.x = max(0, target_x)


def load_sprite(name, scale=1):
    sizes = {
        "joseph": (60, 80),
        "mary": (60, 80),
        "soldier": (50, 80),
        "donkey": (80, 60),
    }

    surf = pygame.Surface(sizes.get(name, (50, 50)))
    surf.set_colorkey(BLACK)  # Make black color transparent
    surf.fill(BLACK)  # Fill with transparent color

    if name == "joseph":
        # Body (brown robe)
        pygame.draw.rect(surf, BROWN, (20, 30, 20, 45))
        # Head
        pygame.draw.circle(surf, (205, 155, 125), (30, 20), 10)  # Flesh color
        # Beard
        pygame.draw.ellipse(surf, BROWN, (25, 15, 10, 15))
        # Arms
        pygame.draw.rect(surf, BROWN, (15, 35, 5, 20))  # Left arm
        pygame.draw.rect(surf, BROWN, (40, 35, 5, 20))  # Right arm
        # Legs
        pygame.draw.rect(surf, (139, 69, 19), (20, 75, 8, 5))  # Left leg
        pygame.draw.rect(surf, (139, 69, 19), (32, 75, 8, 5))  # Right leg
        # Staff
        pygame.draw.line(surf, (139, 69, 19), (45, 30), (45, 80), 3)

    elif name == "mary":
        # Body (blue robe)
        pygame.draw.rect(surf, BLUE, (20, 30, 20, 45))
        # Head covering (white)
        pygame.draw.ellipse(surf, WHITE, (15, 5, 30, 25))
        # Face
        pygame.draw.circle(surf, (225, 198, 153), (30, 20), 8)  # Lighter flesh color
        # Baby Jesus (wrapped in white cloth)
        pygame.draw.ellipse(surf, WHITE, (35, 35, 15, 20))
        # Arms holding baby
        pygame.draw.rect(surf, BLUE, (15, 35, 25, 5))  # Arms
        # Legs
        pygame.draw.rect(surf, BLUE, (20, 75, 8, 5))  # Left leg
        pygame.draw.rect(surf, BLUE, (32, 75, 8, 5))  # Right leg

    elif name == "soldier":
        # Body (red armor)
        pygame.draw.rect(surf, RED, (15, 25, 20, 40))
        # Helmet
        pygame.draw.rect(surf, (192, 192, 192), (15, 5, 20, 20))  # Silver helmet
        pygame.draw.arc(surf, RED, (15, 0, 20, 20), 0, math.pi, 3)  # Red plume
        # Face
        pygame.draw.circle(surf, (205, 155, 125), (25, 15), 7)
        # Shield
        pygame.draw.rect(surf, (192, 192, 192), (10, 30, 15, 25))
        # Spear
        pygame.draw.line(surf, BROWN, (40, 10), (40, 60), 2)
        pygame.draw.polygon(surf, (192, 192, 192), [(38, 10), (42, 10), (40, 5)])
        # Legs with armor
        pygame.draw.rect(surf, (192, 192, 192), (15, 65, 8, 15))  # Left leg
        pygame.draw.rect(surf, (192, 192, 192), (27, 65, 8, 15))  # Right leg

    elif name == "donkey":
        # Body
        pygame.draw.ellipse(surf, (128, 128, 128), (20, 20, 40, 25))  # Gray body
        # Head
        pygame.draw.ellipse(surf, (128, 128, 128), (10, 15, 20, 15))
        # Ears
        pygame.draw.polygon(surf, (128, 128, 128), [(15, 15), (20, 5), (25, 15)])
        pygame.draw.polygon(surf, (128, 128, 128), [(20, 15), (25, 5), (30, 15)])
        # Legs
        pygame.draw.rect(surf, (128, 128, 128), (25, 45, 5, 15))  # Front leg
        pygame.draw.rect(surf, (128, 128, 128), (50, 45, 5, 15))  # Back leg
        # Tail
        pygame.draw.line(surf, (128, 128, 128), (60, 25), (65, 35), 2)

    elif name == "gateway":
        # Stone archway
        pygame.draw.rect(surf, (169, 169, 169), (0, 0, 120, 120))  # Main structure
        pygame.draw.rect(surf, BLACK, (30, 20, 60, 100))  # Gateway opening
        # Stone details
        for i in range(6):
            pygame.draw.rect(surf, (128, 128, 128), (i * 20, 0, 20, 20))  # Top stones
            pygame.draw.rect(
                surf, (128, 128, 128), (i * 20, 100, 20, 20)
            )  # Bottom stones
        # Side pillars
        pygame.draw.rect(surf, (192, 192, 192), (0, 0, 30, 120))  # Left pillar
        pygame.draw.rect(surf, (192, 192, 192), (90, 0, 30, 120))  # Right pillar

    elif name == "desert_cave":
        # Desert cave exit for level 2
        pygame.draw.rect(surf, (139, 101, 8), (0, 0, 120, 120))  # Cave exterior
        pygame.draw.ellipse(surf, BLACK, (20, 10, 80, 100))  # Cave opening
        # Add rock details
        for i in range(6):
            pygame.draw.polygon(
                surf, (101, 67, 33), [(i * 20, 0), ((i + 1) * 20, 0), (i * 20 + 10, 20)]
            )  # Top rocks
            pygame.draw.polygon(
                surf,
                (101, 67, 33),
                [(i * 20, 120), ((i + 1) * 20, 120), (i * 20 + 10, 100)],
            )  # Bottom rocks

    elif name == "mountain_pass":
        # Mountain pass exit for level 3
        # Mountain silhouette
        pygame.draw.polygon(
            surf,
            (105, 105, 105),
            [(0, 120), (0, 40), (30, 20), (60, 0), (90, 20), (120, 40), (120, 120)],
        )
        # Pass opening
        pygame.draw.polygon(surf, BLACK, [(40, 120), (50, 60), (70, 60), (80, 120)])
        # Snow caps
        pygame.draw.polygon(
            surf, WHITE, [(25, 25), (30, 20), (60, 0), (90, 20), (95, 25)]
        )

    elif name == "coastal_dock":
        # Coastal dock exit for level 4
        # Dock structure
        pygame.draw.rect(surf, (139, 69, 19), (0, 80, 120, 40))  # Main dock
        # Posts
        for i in range(4):
            pygame.draw.rect(surf, (101, 67, 33), (i * 40, 60, 10, 60))
        # Water
        for i in range(6):
            pygame.draw.arc(surf, BLUE, (i * 20 - 10, 70, 40, 40), 0, math.pi)
        # Boat
        pygame.draw.rect(surf, BROWN, (20, 40, 80, 30))
        pygame.draw.polygon(surf, WHITE, [(60, 0), (60, 40), (100, 40)])  # Sail

    elif name == "pyramid":
        # Egyptian pyramid exit for final level
        # Main pyramid shape
        pygame.draw.polygon(surf, (255, 223, 186), [(0, 120), (60, 0), (120, 120)])
        # Stone lines
        for y in range(20, 120, 20):
            pygame.draw.line(surf, (139, 69, 19), (y * 0.5, y), (120 - y * 0.5, y), 2)
        # Entrance
        pygame.draw.polygon(surf, BLACK, [(50, 120), (60, 100), (70, 120)])
        # Add some hieroglyphics
        for i in range(3):
            pygame.draw.rect(surf, (139, 69, 19), (40 + i * 20, 60, 5, 10))
            pygame.draw.circle(surf, (139, 69, 19), (43 + i * 20, 80), 3)

    if scale != 1:
        new_size = (int(surf.get_width() * scale), int(surf.get_height() * scale))
        surf = pygame.transform.scale(surf, new_size)
    return surf


class Player:
    def __init__(self):
        self.width = 60
        self.height = 80
        self.x = 100
        self.y = SCREEN_HEIGHT - self.height - 50
        self.vel_x = 0
        self.vel_y = 0
        self.stamina = STAMINA_MAX
        self.is_ducking = False
        self.is_hidden = False
        self.on_ground = False
        self.facing_right = True
        # Add sprites
        self.joseph_sprite = load_sprite("joseph")
        self.mary_sprite = load_sprite("mary")
        self.donkey_sprite = load_sprite("donkey")

    def move(self, direction):
        if self.stamina > 0:
            self.vel_x = direction * MOVE_SPEED
            if direction != 0:
                self.facing_right = direction > 0
                self.stamina = max(0, self.stamina - STAMINA_DRAIN)
        else:
            self.vel_x = direction * (MOVE_SPEED * 0.5)  # Slower when tired

    def jump(self):
        if self.on_ground and self.stamina > 20:
            self.vel_y = JUMP_POWER
            self.on_ground = False
            self.stamina = max(0, self.stamina - 20)  # Jump costs stamina

    def duck(self):
        if not self.is_ducking:
            self.is_ducking = True
            self.height = 40  # Half height while ducking

    def stand(self):
        if self.is_ducking:
            self.is_ducking = False
            self.height = 80  # Return to normal height

    def update(self, platforms):
        # Apply gravity
        self.vel_y += GRAVITY

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        # Screen boundaries - only prevent moving left of screen
        self.x = max(0, self.x)  # Remove the right boundary limit

        # Ground collision
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True

        # Platform collisions
        for platform in platforms:
            if self.check_collision(platform):
                if self.vel_y > 0:  # Landing on platform
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.on_ground = True

        # Regenerate stamina when on ground and not moving
        if self.on_ground and abs(self.vel_x) < 0.1:
            self.stamina = min(STAMINA_MAX, self.stamina + STAMINA_REGEN)

    def check_collision(self, platform):
        return (
            self.x + self.width > platform.x
            and self.x < platform.x + platform.width
            and self.y + self.height > platform.y
            and self.y < platform.y + platform.height
        )

    def draw(self, screen, camera):
        screen_pos = camera.apply(self)

        if self.facing_right:
            screen.blit(self.joseph_sprite, (screen_pos[0] - 20, screen_pos[1]))
            screen.blit(self.mary_sprite, (screen_pos[0] + 20, screen_pos[1]))
            if not self.is_ducking:
                screen.blit(self.donkey_sprite, (screen_pos[0], screen_pos[1] + 20))
        else:
            screen.blit(
                pygame.transform.flip(self.joseph_sprite, True, False),
                (screen_pos[0] + 20, screen_pos[1]),
            )
            screen.blit(
                pygame.transform.flip(self.mary_sprite, True, False),
                (screen_pos[0] - 20, screen_pos[1]),
            )
            if not self.is_ducking:
                screen.blit(
                    pygame.transform.flip(self.donkey_sprite, True, False),
                    (screen_pos[0], screen_pos[1] + 20),
                )

        # Draw stamina bar
        stamina_width = 50
        stamina_height = 5
        stamina_x = screen_pos[0] + (self.width - stamina_width) / 2
        stamina_y = screen_pos[1] - 10
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


class Obstacle:
    def __init__(self, x, y, width, height, obstacle_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obstacle_type
        self.active = True
        self.sprite = None

        if self.type == "patrol":
            self.direction = 1
            self.patrol_speed = 2
            self.patrol_distance = 200
            self.start_x = x
            self.sprite = load_sprite("soldier")

    def update(self):
        if self.type == "patrol":
            self.x += self.direction * self.patrol_speed
            if abs(self.x - self.start_x) > self.patrol_distance:
                self.direction *= -1

    def draw(self, screen, camera=None):
        screen_pos = camera.apply(self) if camera else (self.x, self.y)

        if self.type == "patrol" and self.sprite:
            if self.direction > 0:
                screen.blit(self.sprite, screen_pos)
            else:
                screen.blit(pygame.transform.flip(self.sprite, True, False), screen_pos)
        else:
            color = {
                "patrol": RED,
                "crate": BROWN,
                "rock": SAND_COLOR,
                "quicksand": (194, 178, 128, 128),
            }.get(self.type, WHITE)
            pygame.draw.rect(screen, color, (*screen_pos, self.width, self.height))


class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.config = LEVELS[level_num]
        self.platforms = []
        self.obstacles = []
        self.collectibles = []
        self.level_width = SCREEN_WIDTH * 3  # Make level 3 screens wide
        self.gateway = None  # Add gateway property
        self.generate_level()

    def generate_level(self):
        # Add basic platforms
        platform_y = SCREEN_HEIGHT - 40
        platform_width = 200
        gap = 150

        x = 0
        while x < self.level_width:
            self.platforms.append(
                Obstacle(x, platform_y, platform_width, 40, "platform")
            )
            x += platform_width + gap

        # Add level-specific obstacles
        if "patrol" in self.config["obstacles"]:
            # First soldier at x=300
            self.obstacles.append(Obstacle(300, platform_y - 60, 40, 60, "patrol"))
            # Add more soldiers throughout the level
            self.obstacles.append(Obstacle(800, platform_y - 60, 40, 60, "patrol"))
            self.obstacles.append(Obstacle(1300, platform_y - 60, 40, 60, "patrol"))

        # Add level-specific exit
        exit_sprites = {
            1: "gateway",
            2: "desert_cave",
            3: "mountain_pass",
            4: "coastal_dock",
            5: "pyramid",
        }

        if self.level_num in exit_sprites:
            self.gateway = Obstacle(
                self.level_width - 200,
                platform_y - 120,
                120,
                120,
                exit_sprites[self.level_num],
            )
            self.gateway.sprite = load_sprite(exit_sprites[self.level_num])

    def update(self):
        for obstacle in self.obstacles:
            obstacle.update()

    def draw(self, screen, camera):
        # Draw background
        bg_colors = {
            "night_city": (20, 20, 50),
            "desert": (194, 178, 128),
            "mountains": (100, 100, 100),
            "coast": (100, 149, 237),
            "river": (50, 100, 50),
        }
        screen.fill(bg_colors.get(self.config["background"], BLACK))

        # Draw platforms and obstacles
        for platform in self.platforms:
            screen_pos = camera.apply(platform)
            if -platform.width < screen_pos[0] < SCREEN_WIDTH:
                platform.draw(screen, camera)

        for obstacle in self.obstacles:
            screen_pos = camera.apply(obstacle)
            if -obstacle.width < screen_pos[0] < SCREEN_WIDTH:
                obstacle.draw(screen, camera)

        # Draw gateway with a subtle hint arrow
        if self.gateway:
            screen_pos = camera.apply(self.gateway)
            if -self.gateway.width < screen_pos[0] < SCREEN_WIDTH:
                self.gateway.draw(screen, camera)
                # Draw arrow pointing to exit when it's first visible
                if 0 <= screen_pos[0] <= SCREEN_WIDTH:
                    arrow_x = screen_pos[0] + self.gateway.width // 2
                    arrow_y = screen_pos[1] - 40
                    points = [
                        (arrow_x, arrow_y),
                        (arrow_x - 10, arrow_y - 20),
                        (arrow_x + 10, arrow_y - 20),
                    ]
                    pygame.draw.polygon(screen, WHITE, points)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Journey to Egypt")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU
        self.current_level = 1
        self.score = 0
        self.camera = Camera()
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.level = Level(self.current_level)
        self.camera.x = 0  # Reset camera position
        self.camera.y = 0  # Reset camera position

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == MENU:
                    if event.key == pygame.K_RETURN:  # ENTER key
                        self.state = PLAYING
                        self.reset_game()
                elif self.state == GAME_OVER:
                    if event.key == pygame.K_RETURN:  # ENTER key
                        self.state = MENU
                elif self.state == LEVEL_COMPLETE:
                    if event.key == pygame.K_RETURN:  # ENTER key
                        self.state = PLAYING
                        self.reset_game()
                elif self.state == PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    elif event.key == pygame.K_DOWN:
                        self.player.duck()
            elif event.type == pygame.KEYUP:
                if self.state == PLAYING and event.key == pygame.K_DOWN:
                    self.player.stand()

        # Only handle movement keys when in PLAYING state
        if self.state == PLAYING:
            keys = pygame.key.get_pressed()
            direction = 0
            if keys[pygame.K_LEFT]:
                direction = -1
            elif keys[pygame.K_RIGHT]:
                direction = 1
            self.player.move(direction)

    def update(self):
        if self.state == PLAYING:
            self.player.update(self.level.platforms)
            self.level.update()
            self.camera.update(self.player)

            # Check collisions with obstacles
            for obstacle in self.level.obstacles:
                if (
                    obstacle.active
                    and not self.player.is_hidden
                    and self.player.check_collision(obstacle)
                ):
                    if obstacle.type == "patrol":
                        self.state = GAME_OVER

            # Check for level completion (reaching the gateway)
            if self.level.gateway and self.player.check_collision(self.level.gateway):
                if self.current_level < len(LEVELS):
                    self.current_level += 1
                    self.state = LEVEL_COMPLETE
                else:
                    self.state = GAME_OVER  # Game completed

    def draw_menu(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        title = font.render("Journey to Egypt", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 200))

        font = pygame.font.Font(None, 36)
        prompt = font.render("Press ENTER to Start", True, WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH / 2 - prompt.get_width() / 2, 400))

    def draw_game(self):
        self.level.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)

        # Draw HUD (fixed position, not affected by camera)
        font = pygame.font.Font(None, 36)
        level_text = font.render(
            f"Level {self.current_level}: {self.level.config['name']}", True, WHITE
        )
        self.screen.blit(level_text, (10, 10))

    def draw_game_over(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        title = font.render("Game Over", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 200))

        font = pygame.font.Font(None, 36)
        prompt = font.render("Press ENTER to Try Again", True, WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH / 2 - prompt.get_width() / 2, 400))

    def draw_level_complete(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        title = font.render("Level Complete!", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 200))

        font = pygame.font.Font(None, 36)
        prompt = font.render("Press ENTER to Continue", True, WHITE)
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
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            await asyncio.sleep(0)


async def main():
    game = Game()
    await game.run()
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
