import pygame
import random
import math
import os

# Initialize Pygame and its sound mixer
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
CAMERA_SLACK = 200  # Distance from player to edge before camera moves
CAMERA_LERP = 0.1  # Camera smoothing factor (0 = no smoothing, 1 = instant)

# Game States
MENU = "menu"
MODE_SELECT = "mode_select"  # New state for mode selection
PLAYING = "playing"
GAME_OVER = "game_over"

# Game Modes
AUTO_SCROLL = "auto_scroll"
FREE_MOVE = "free_move"

# Points
PRESENT_POINTS = 10  # Points per present when delivered via chimney

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Game settings
SCROLL_SPEED = 2
PLATFORM_SPACING = 150
MIN_PLATFORM_WIDTH = 300
MAX_PLATFORM_WIDTH = 400
SAFE_SPAWN_HEIGHT = SCREEN_HEIGHT - 200
INITIAL_PLATFORM_WIDTH = 600
INITIAL_PLATFORM_HEIGHT = SCREEN_HEIGHT - 150
JUMP_POWER = -7  # Reduced from -10 for lower jumps
GRAVITY = 0.4  # Reduced from 0.5 for more floaty feel
CHIMNEY_WIDTH = 40
CHIMNEY_HEIGHT = 60
SLEIGH_WIDTH = 80
SLEIGH_HEIGHT = 40
BRICK_COLOR = (139, 69, 19)
STAR_SIZE = 20
STAR_COLOR = (255, 255, 0)
GRUNCH_CHASE_SPEED = 1.7  # Increased from 1
STOLEN_PRESENT_FLOAT_SPEED = 2  # Slower float for better visibility
STOLEN_PRESENT_DURATION = 60  # frames the stolen present animation lasts
POINTS_STOLEN = 10  # How many points the Grunch steals when no presents
MAX_PRESENTS = 15  # Maximum presents Santa can carry
SNOW_PARTICLES = 100  # Number of snowflakes
HOUSE_HEIGHT = 150  # Height of houses below platforms
FRICTION = 0.93  # Reduced from 0.98 for more slippery movement
ACCELERATION = 0.15  # Increased from 0.1 for better control with slippery movement
MAX_SPEED = 3  # Increased from 2 to compensate for slippery movement
RETREAT_DISTANCE = 400  # Distance to retreat (about 1 house length)


# Placeholder for assets (to be replaced with actual sprites)
def load_sprite(name, scale=1):
    sizes = {
        "santa": (50, 50),
        "grunch": (40, 60),  # Renamed from grinch
        "present": (20, 20),
        "platform": (100, 20),
        "chimney": (CHIMNEY_WIDTH, CHIMNEY_HEIGHT),
        "star": (STAR_SIZE, STAR_SIZE),
        "sleigh": (SLEIGH_WIDTH, SLEIGH_HEIGHT),
    }
    surf = pygame.Surface(sizes[name])
    surf.set_colorkey(BLACK)  # Make black color transparent
    surf.fill(BLACK)  # Fill with transparent color

    if name == "santa":
        # Body (red coat)
        pygame.draw.rect(surf, RED, (15, 20, 20, 25))
        # Head
        pygame.draw.circle(surf, (255, 220, 180), (25, 15), 10)  # Flesh color
        # Hat
        pygame.draw.rect(surf, RED, (15, 0, 20, 12))  # Hat base
        pygame.draw.circle(surf, RED, (35, 8), 4)  # Hat ball
        pygame.draw.ellipse(surf, WHITE, (13, 10, 24, 4))  # Hat trim
        # Beard
        pygame.draw.ellipse(surf, WHITE, (20, 12, 10, 10))
        # Arms
        pygame.draw.rect(surf, RED, (10, 25, 5, 15))  # Left arm
        pygame.draw.rect(surf, RED, (35, 25, 5, 15))  # Right arm
        # Legs
        pygame.draw.rect(surf, (0, 0, 100), (15, 45, 8, 5))  # Left leg (blue pants)
        pygame.draw.rect(surf, (0, 0, 100), (27, 45, 8, 5))  # Right leg
        # Boots
        pygame.draw.rect(surf, BLACK, (13, 48, 10, 2))  # Left boot
        pygame.draw.rect(surf, BLACK, (27, 48, 10, 2))  # Right boot
        # Belt
        pygame.draw.rect(surf, BLACK, (15, 35, 20, 3))
        pygame.draw.rect(surf, (255, 215, 0), (23, 35, 4, 3))  # Gold buckle

    elif name == "chimney":
        # Create a brick pattern
        brick_height = 10
        brick_rows = CHIMNEY_HEIGHT // brick_height
        for row in range(brick_rows):
            offset = 10 if row % 2 == 0 else 0
            for x in range(0, CHIMNEY_WIDTH - 10, 20):
                pygame.draw.rect(
                    surf, BRICK_COLOR, (x + offset, row * brick_height, 18, 8)
                )
        for row in range(brick_rows + 1):
            pygame.draw.line(
                surf,
                (100, 50, 0),
                (0, row * brick_height),
                (CHIMNEY_WIDTH, row * brick_height),
            )

    elif name == "sleigh":
        # Create a sleigh shape
        pygame.draw.ellipse(
            surf, GREEN, (0, SLEIGH_HEIGHT // 2, SLEIGH_WIDTH, SLEIGH_HEIGHT // 2)
        )
        pygame.draw.rect(surf, GREEN, (5, 5, SLEIGH_WIDTH - 10, SLEIGH_HEIGHT // 2))
        pygame.draw.arc(surf, GREEN, (0, 0, 20, 20), 0, 3.14, 3)
        pygame.draw.arc(surf, GREEN, (SLEIGH_WIDTH - 20, 0, 20, 20), 0, 3.14, 3)

    elif name == "star":
        # Create a star shape
        points = []
        for i in range(5):
            angle = (i * 72 - 90) * math.pi / 180
            points.append(
                (
                    STAR_SIZE / 2 + math.cos(angle) * STAR_SIZE / 2,
                    STAR_SIZE / 2 + math.sin(angle) * STAR_SIZE / 2,
                )
            )
            angle = (i * 72 - 90 + 36) * math.pi / 180
            points.append(
                (
                    STAR_SIZE / 2 + math.cos(angle) * STAR_SIZE / 4,
                    STAR_SIZE / 2 + math.sin(angle) * STAR_SIZE / 4,
                )
            )
        pygame.draw.polygon(surf, STAR_COLOR, points)

    elif name == "present":
        # Create a present shape
        box_color = (200, 0, 0)  # Dark red for the box
        ribbon_color = (255, 215, 0)  # Gold for the ribbon
        pygame.draw.rect(surf, box_color, (0, 0, 20, 20))
        pygame.draw.rect(surf, ribbon_color, (8, 0, 4, 20))  # Vertical ribbon
        pygame.draw.rect(surf, ribbon_color, (0, 8, 20, 4))  # Horizontal ribbon
        pygame.draw.circle(surf, ribbon_color, (10, 10), 3)  # Ribbon center

    elif name == "grunch":  # Create a more detailed Grunch shape
        # Body (green coat)
        pygame.draw.rect(surf, GREEN, (15, 20, 20, 30))
        # Head
        pygame.draw.circle(surf, (144, 238, 144), (25, 15), 10)  # Light green face
        # Evil grin
        pygame.draw.arc(surf, BLACK, (20, 12, 10, 10), 0, math.pi, 2)
        # Eyes
        pygame.draw.circle(surf, RED, (22, 13), 2)  # Left eye
        pygame.draw.circle(surf, RED, (28, 13), 2)  # Right eye
        # Hat
        pygame.draw.polygon(surf, GREEN, [(15, 10), (25, 0), (35, 10)])  # Pointed hat
        # Arms
        pygame.draw.rect(surf, GREEN, (10, 25, 5, 15))  # Left arm
        pygame.draw.rect(surf, GREEN, (35, 25, 5, 15))  # Right arm
        # Legs
        pygame.draw.rect(surf, (0, 100, 0), (15, 50, 8, 10))  # Left leg (darker green)
        pygame.draw.rect(surf, (0, 100, 0), (27, 50, 8, 10))  # Right leg
        # Fingers (claw-like)
        pygame.draw.line(surf, BLACK, (10, 40), (5, 35), 2)
        pygame.draw.line(surf, BLACK, (40, 40), (45, 35), 2)

    else:
        surf.fill(
            {
                "grunch": GREEN,
                "platform": WHITE,
            }[name]
        )

    if scale != 1:
        new_size = (int(surf.get_width() * scale), int(surf.get_height() * scale))
        surf = pygame.transform.scale(surf, new_size)
    return surf


# Sound Manager for handling game audio
class SoundManager:
    def __init__(self):
        self.sounds = {}
        # Placeholder for sound effects
        # In a real game, you would load actual sound files like this:
        # self.sounds["jump"] = pygame.mixer.Sound("assets/sounds/jump.wav")
        # self.sounds["collect"] = pygame.mixer.Sound("assets/sounds/collect.wav")
        # self.sounds["deliver"] = pygame.mixer.Sound("assets/sounds/deliver.wav")
        # self.sounds["hit"] = pygame.mixer.Sound("assets/sounds/hit.wav")

    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()


class Camera:
    def __init__(self):
        self.x = 0
        self.target_x = 0
        self.last_update = pygame.time.get_ticks()

    def update(self, target):
        # Get delta time in seconds
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_update) / 1000.0
        self.last_update = current_time

        # Calculate target position (center player)
        self.target_x = target.world_x - SCREEN_WIDTH // 3

        # Smoothly move camera towards target
        dx = self.target_x - self.x
        self.x += dx * CAMERA_LERP * (60 * dt)  # Scale with delta time

    def apply(self, entity):
        # Convert world coordinates to screen coordinates
        screen_x = (
            entity.world_x - self.x if hasattr(entity, "world_x") else entity.x - self.x
        )
        return (
            int(screen_x),
            int(entity.y),
        )  # Integer positions for smoother rendering


class Santa:
    def __init__(self, game_mode=AUTO_SCROLL):
        self.width = 50
        self.height = 50
        self.world_x = 50
        self.x = self.world_x
        self.y = INITIAL_PLATFORM_HEIGHT - 60
        self.velocity_x = SCROLL_SPEED if game_mode == AUTO_SCROLL else 0
        self.velocity_y = 0
        self.jump_power = JUMP_POWER
        self.gravity = GRAVITY
        self.presents = 0
        self.on_ground = False
        self.sprite = load_sprite("santa")
        self.facing_right = True
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.game_mode = game_mode
        self.move_speed = 2  # Reduced from 5

    def move(self, direction):
        if self.game_mode == FREE_MOVE:
            self.velocity_x = direction * self.move_speed
            if direction != 0:
                self.facing_right = direction > 0
        elif self.game_mode == AUTO_SCROLL:
            self.velocity_x = SCROLL_SPEED
            self.facing_right = True

    def jump(self, sound_manager):
        if self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False
            sound_manager.play("jump")

    def update(self, platforms):
        # Update position based on game mode
        if self.game_mode == AUTO_SCROLL:
            self.world_x += SCROLL_SPEED
        else:
            self.world_x += self.velocity_x

        # Handle movement with slippery physics
        keys = pygame.key.get_pressed()
        if self.game_mode == FREE_MOVE:
            if keys[pygame.K_LEFT]:
                self.velocity_x -= ACCELERATION
            if keys[pygame.K_RIGHT]:
                self.velocity_x += ACCELERATION
        else:  # AUTO_SCROLL
            # Maintain constant scroll speed with slight acceleration/deceleration
            if self.velocity_x < SCROLL_SPEED:
                self.velocity_x += ACCELERATION
            elif self.velocity_x > SCROLL_SPEED:
                self.velocity_x -= ACCELERATION

        # Apply friction and speed limits
        self.velocity_x *= FRICTION
        if self.game_mode == FREE_MOVE:
            self.velocity_x = max(min(self.velocity_x, MAX_SPEED), -MAX_SPEED)
        else:
            # Keep speed closer to SCROLL_SPEED in auto-scroll mode
            self.velocity_x = max(
                min(self.velocity_x, SCROLL_SPEED + 1), SCROLL_SPEED - 1
            )

        # Update position with velocity
        self.world_x += self.velocity_x

        # Apply gravity
        self.velocity_y += self.gravity
        next_y = self.y + self.velocity_y

        # Platform collision detection with more precision
        self.on_ground = False
        for platform in platforms:
            # Platform collision
            if (
                self.world_x + self.width > platform.x
                and self.world_x < platform.x + platform.width
            ):

                # Landing on platform
                if (
                    self.velocity_y > 0  # Moving downward
                    and next_y + self.height > platform.y
                    and self.y + self.height <= platform.y + 10
                ):  # Added tolerance
                    self.y = platform.y - self.height
                    self.velocity_y = 0
                    self.on_ground = True
                    break  # Stop checking once we've landed

            # Chimney collision
            if platform.has_chimney:
                chimney_top_y = platform.y - CHIMNEY_HEIGHT
                if (
                    self.world_x + self.width > platform.chimney_x
                    and self.world_x < platform.chimney_x + CHIMNEY_WIDTH
                ):

                    # Landing on chimney
                    if (
                        self.velocity_y > 0
                        and next_y + self.height > chimney_top_y
                        and self.y + self.height <= chimney_top_y + 10
                    ):  # Added tolerance
                        self.y = chimney_top_y - self.height
                        self.velocity_y = 0
                        self.on_ground = True
                        if not platform.star_collected:
                            platform.star_collected = True
                            return "collect_star"
                        break

        # If we didn't hit anything, update y position
        if not self.on_ground:
            self.y = next_y

        # Check if fallen off screen
        if self.y > SCREEN_HEIGHT:
            return "game_over"

        # Check if moved too far left in auto-scroll mode
        if self.game_mode == AUTO_SCROLL and self.world_x < self.x - SCREEN_WIDTH / 2:
            return "game_over"

        # Update invulnerability
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

        # Update position with velocity
        self.world_x += self.velocity_x
        self.y += self.velocity_y

        return "continue"

    def check_platform_collision(self, platform):
        return (
            self.world_x + self.width > platform.x
            and self.world_x < platform.x + platform.width
            and self.y + self.height >= platform.y
            and self.y + self.height <= platform.y + 20
            and self.velocity_y >= 0  # Only collide when moving downward
        )

    def make_invulnerable(self, duration=60):
        self.invulnerable = True
        self.invulnerable_timer = duration

    def draw(self, screen, camera):
        # Blink when invulnerable
        if self.invulnerable and self.invulnerable_timer % 10 >= 5:
            return

        screen_pos = camera.apply(self)
        screen.blit(self.sprite, screen_pos)

        # Draw present count in a more clear way
        if self.presents > 0:
            font = pygame.font.Font(None, 24)
            present_text = font.render(f"Presents: {self.presents}", True, WHITE)
            screen.blit(
                present_text, (screen_pos[0] + self.width / 2 - 30, screen_pos[1] - 20)
            )


class Grunch:
    def __init__(self, target):
        self.width = SLEIGH_WIDTH
        self.height = SLEIGH_HEIGHT
        self.world_x = -500
        self.x = self.world_x
        self.y = INITIAL_PLATFORM_HEIGHT - 200
        self.speed = GRUNCH_CHASE_SPEED
        self.target = target
        self.grunch_sprite = load_sprite("grunch", 0.8)
        self.sleigh_sprite = load_sprite("sleigh")
        self.float_offset = 0
        self.float_speed = 0.03
        self.celebrating = False
        self.celebrate_timer = 0
        self.state = "chasing"
        self.has_passed = False
        self.retreat_x = self.world_x - RETREAT_DISTANCE

    def start_celebration(self):
        self.celebrating = True
        self.celebrate_timer = 30

    def update(self, platforms):
        # Floating motion
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * 20
        self.y = INITIAL_PLATFORM_HEIGHT - 200 + self.float_offset

        if self.state == "chasing":
            # Move towards Santa faster
            self.world_x += self.speed * 2  # Increased from 1.5

            # Check if passed Santa
            if not self.has_passed and self.world_x > self.target.world_x:
                self.has_passed = True
                self.state = "passing"
                self.start_celebration()
                return "steal_points"

        elif self.state == "passing":
            # Move past Santa faster
            self.world_x += self.speed * 3  # Increased from 2
            if self.world_x > self.target.world_x + 100:
                self.state = "retreating"
                self.retreat_x = self.world_x - RETREAT_DISTANCE

        elif self.state == "retreating":
            # Retreat faster
            self.world_x -= self.speed * 4  # Increased from 3
            if self.world_x < self.retreat_x:
                # Reset for next approach
                self.state = "chasing"
                self.has_passed = False

        # Update celebration
        if self.celebrating:
            self.celebrate_timer -= 1
            if self.celebrate_timer <= 0:
                self.celebrating = False

    def draw(self, screen, camera):
        screen_pos = camera.apply(self)
        # Draw sleigh
        screen.blit(self.sleigh_sprite, screen_pos)

        # Draw Grunch with celebration effect
        grunch_pos = (
            screen_pos[0] + 20,
            screen_pos[1]
            - self.grunch_sprite.get_height()
            + 20
            + (math.sin(pygame.time.get_ticks() * 0.2) * 5 if self.celebrating else 0),
        )
        screen.blit(self.grunch_sprite, grunch_pos)

        # Draw celebration text
        if self.celebrating:
            font = pygame.font.Font(None, 24)
            celebrate_text = font.render("Ha Ha Ha!", True, GREEN)
            text_pos = (grunch_pos[0], grunch_pos[1] - 20)
            screen.blit(celebrate_text, text_pos)


class Present:
    def __init__(self, x, y):
        self.world_x = x  # Change x to world_x for consistency
        self.x = x  # Keep x for backwards compatibility
        self.y = y
        self.width = 20
        self.height = 20
        self.collected = False
        self.sprite = load_sprite("present")
        self.float_offset = 0
        self.float_speed = 0.05

    def update(self):
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * 5

    def draw(self, screen, camera):
        if not self.collected:
            screen_pos = camera.apply(self)
            screen.blit(self.sprite, (screen_pos[0], screen_pos[1] + self.float_offset))


class Platform:
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        self.height = 20
        self.has_chimney = random.random() > 0.5
        # Create house directly connected to platform
        self.house = House(x, y, width)
        # Place chimney more towards the middle of platforms
        min_chimney_x = self.x + CHIMNEY_WIDTH
        max_chimney_x = self.x + self.width - 2 * CHIMNEY_WIDTH
        if max_chimney_x > min_chimney_x:
            self.chimney_x = random.randint(int(min_chimney_x), int(max_chimney_x))
        else:
            self.chimney_x = self.x + self.width // 2 - CHIMNEY_WIDTH // 2
        self.sprite = load_sprite("platform")
        self.chimney_sprite = load_sprite("chimney")
        self.star_sprite = load_sprite("star")
        self.star_collected = False

    def draw(self, screen, camera):
        # Draw house first (behind platform)
        self.house.draw(screen, camera)
        screen_x = self.x - camera.x
        # Draw platform
        platform_surface = pygame.transform.scale(
            self.sprite, (self.width, self.height)
        )
        screen.blit(platform_surface, (screen_x, self.y))
        # Draw chimney and star
        if self.has_chimney:
            chimney_screen_pos = (
                screen_x + (self.chimney_x - self.x),
                self.y - CHIMNEY_HEIGHT,
            )
            screen.blit(self.chimney_sprite, chimney_screen_pos)
            if not self.star_collected:
                star_pos = (
                    chimney_screen_pos[0] + CHIMNEY_WIDTH // 2 - STAR_SIZE // 2,
                    chimney_screen_pos[1] - STAR_SIZE - 5,
                )
                screen.blit(self.star_sprite, star_pos)


class StolenPresent:
    def __init__(self, x, y, target_y):
        self.x = x
        self.y = y
        self.target_y = target_y
        self.duration = STOLEN_PRESENT_DURATION
        self.sprite = load_sprite("present")
        self.float_offset = 0
        self.float_speed = 0.1

    def update(self):
        # Float upward to Grunch's sleigh
        self.y -= STOLEN_PRESENT_FLOAT_SPEED
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * 5
        self.duration -= 1
        return self.duration > 0

    def draw(self, screen, camera):
        screen_pos = camera.apply(self)
        screen.blit(self.sprite, (screen_pos[0], screen_pos[1] + self.float_offset))


class StolenScore:
    def __init__(self, x, y, target_y, text):
        self.x = x
        self.y = y
        self.target_y = target_y
        self.duration = STOLEN_PRESENT_DURATION
        self.text = text
        self.float_speed = 0.1
        self.font = pygame.font.Font(None, 36)
        self.color = (255, 0, 0)  # Bright red
        self.follow_present = False  # New flag to follow present
        self.offset_x = 20  # Offset from present

    def update(self):
        # Float upward
        self.y -= STOLEN_PRESENT_FLOAT_SPEED
        self.duration -= 1

        # Fade out near the end
        if self.duration < 20:
            alpha = int(255 * (self.duration / 20))
            self.color = (255, 0, 0, alpha)

        # Add slight horizontal sway if following present
        if self.follow_present:
            self.x += math.sin(pygame.time.get_ticks() * 0.01) * 0.5

        return self.duration > 0

    def draw(self, screen, camera):
        screen_pos = camera.apply(self)
        text_surface = self.font.render(self.text, True, self.color)
        # Center the text on the present if following
        if self.follow_present:
            screen.blit(
                text_surface,
                (
                    screen_pos[0] + self.offset_x - text_surface.get_width() // 2,
                    screen_pos[1],
                ),
            )
        else:
            screen.blit(text_surface, screen_pos)


class Snowflake:
    def __init__(self, x=None, y=None):
        self.reset(x, y)

    def reset(self, x=None, y=None):
        self.x = x if x is not None else random.randint(0, SCREEN_WIDTH)
        self.y = y if y is not None else random.randint(-50, SCREEN_HEIGHT)
        self.speed = random.uniform(1, 3)
        self.size = random.randint(2, 4)
        self.drift = random.uniform(-0.5, 0.5)

    def update(self, camera_dx):
        self.y += self.speed
        self.x += self.drift
        self.x -= camera_dx  # Move with camera

        # Reset if out of bounds
        if self.y > SCREEN_HEIGHT:
            self.reset(y=-10)
        if self.x < -10:
            self.reset(x=SCREEN_WIDTH + 10)
        elif self.x > SCREEN_WIDTH + 10:
            self.reset(x=-10)

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)


class House:
    def __init__(self, platform_x, platform_y, platform_width):
        self.x = platform_x
        self.width = platform_width
        # Height is now dynamic - from platform to bottom of screen
        self.height = (
            SCREEN_HEIGHT - platform_y - 20
        )  # -20 to account for platform height
        self.color = (
            random.randint(150, 255),
            random.randint(150, 255),
            random.randint(150, 255),
        )
        self.windows = []
        # Position house directly below platform
        self.y = platform_y + 20  # Start just below platform

        # Generate windows - now spaced relative to house height
        window_size = 20
        window_margin = 30
        num_windows = (platform_width - window_margin) // (window_size + window_margin)
        num_rows = (self.height - 40) // 50  # Number of window rows that will fit
        num_rows = min(num_rows, 4)  # Maximum 4 rows of windows

        for row in range(num_rows):
            window_y = self.y + 30 + (row * 50)  # Space windows vertically
            for i in range(num_windows):
                window_x = self.x + window_margin + i * (window_size + window_margin)
                self.windows.append((window_x, window_y, window_size))

    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        # Draw house extending to bottom of screen
        house_rect = pygame.Rect(screen_x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.color, house_rect)

        # Draw windows with warm light
        for wx, wy, wsize in self.windows:
            window_x = wx - camera.x
            if 0 <= window_x <= SCREEN_WIDTH:  # Only draw visible windows
                pygame.draw.rect(screen, (255, 255, 200), (window_x, wy, wsize, wsize))
                # Window frame
                pygame.draw.rect(
                    screen, (100, 100, 100), (window_x, wy, wsize, wsize), 2
                )


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Santa vs. The Grunch")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU
        self.game_mode = AUTO_SCROLL
        self.score = 0
        self.high_score = 0
        self.sound_manager = SoundManager()
        self.camera = Camera()
        self.last_platform_x = 0
        self.stolen_presents = []  # Add this line
        self.snowflakes = [Snowflake() for _ in range(SNOW_PARTICLES)]
        self.houses = []  # Remove this line as houses are now part of platforms
        self.last_time = pygame.time.get_ticks()
        self.dt = 0  # Delta time in seconds

        # Initialize game objects
        self.reset_game()

    def reset_game(self):
        # Create starting platform first
        self.platforms = []
        self.presents = []
        self.score = 0
        self.camera = Camera()
        self.last_platform_x = 0
        self.stolen_presents = []  # Add this line
        self.houses = []  # Reset houses list

        # Generate initial platform without chimney
        start_platform = Platform(0, INITIAL_PLATFORM_HEIGHT, INITIAL_PLATFORM_WIDTH)
        start_platform.has_chimney = False
        self.platforms.append(start_platform)
        self.last_platform_x = INITIAL_PLATFORM_WIDTH

        # Create Santa with current game mode
        self.santa = Santa(self.game_mode)
        self.grunch = Grunch(self.santa)  # Renamed from grinch

        self.generate_initial_platforms()

    def generate_initial_platforms(self):
        # Generate a few platforms ahead with smaller gaps initially
        next_x = self.last_platform_x
        for i in range(5):
            gap = random.randint(50, 100)  # Even smaller gaps at the start
            width = random.randint(MIN_PLATFORM_WIDTH, MAX_PLATFORM_WIDTH)
            y = random.randint(
                int(INITIAL_PLATFORM_HEIGHT - 20), int(INITIAL_PLATFORM_HEIGHT + 20)
            )  # Keep platforms very close to initial height

            platform = Platform(next_x + gap, y, width)
            self.platforms.append(platform)

            # Add presents on platforms (more frequently at start)
            if random.random() > 0.3:  # 70% chance for presents at start
                present_x = random.randint(
                    int(next_x + gap), int(next_x + gap + width - 20)
                )
                self.presents.append(Present(present_x, y - 30))

            next_x = next_x + gap + width
            self.last_platform_x = next_x

    def generate_next_platform(self):
        # Create a new platform with a gap from the last one
        gap = random.randint(80, 150)  # Slightly smaller gaps for better playability
        width = random.randint(MIN_PLATFORM_WIDTH, MAX_PLATFORM_WIDTH)
        x = self.last_platform_x + gap

        # Keep platforms within a reasonable height range from the previous platform
        last_platform = self.platforms[-1]
        max_height_change = 60
        min_y = max(last_platform.y - max_height_change, SCREEN_HEIGHT / 2)
        max_y = min(last_platform.y + max_height_change, SCREEN_HEIGHT - 100)
        y = random.randint(int(min_y), int(max_y))

        platform = Platform(x, y, width)
        self.platforms.append(platform)

        # Add presents on platform
        if random.random() > 0.5:
            present_x = random.randint(int(x), int(x + width - 20))
            self.presents.append(Present(present_x, y - 30))

        self.last_platform_x = x + width

        # Remove platforms that are too far behind
        self.platforms = [
            p
            for p in self.platforms
            if p.x + p.width > self.santa.world_x - SCREEN_WIDTH
        ]
        self.presents = [
            p
            for p in self.presents
            if not p.collected and p.x > self.santa.world_x - SCREEN_WIDTH
        ]

        # Remove independent house generation
        if "if random.random() > 0.3:" in locals():
            del locals()["if random.random() > 0.3:"]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == MENU:
                    if event.key == pygame.K_RETURN:
                        self.state = MODE_SELECT
                elif self.state == MODE_SELECT:
                    if event.key == pygame.K_1:
                        self.game_mode = AUTO_SCROLL
                        self.reset_game()
                        self.state = PLAYING
                    elif event.key == pygame.K_2:
                        self.game_mode = FREE_MOVE
                        self.reset_game()
                        self.state = PLAYING
                elif self.state == PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.santa.jump(self.sound_manager)
                elif self.state == GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        self.state = MODE_SELECT

        # Handle movement in playing state
        if self.state == PLAYING:
            keys = pygame.key.get_pressed()
            if self.game_mode == FREE_MOVE:
                direction = 0
                if keys[pygame.K_LEFT]:
                    direction = -1
                elif keys[pygame.K_RIGHT]:
                    direction = 1
                self.santa.move(direction)
            else:
                self.santa.move(1)  # Always move right in auto-scroll mode

    def update(self):
        if self.state != PLAYING:
            return

        # Calculate delta time
        current_time = pygame.time.get_ticks()
        self.dt = (current_time - self.last_time) / 1000.0
        self.last_time = current_time

        # Update snowflakes with delta time
        camera_dx = (self.camera.x - getattr(self, "last_camera_x", self.camera.x)) * (
            60 * self.dt
        )
        self.last_camera_x = self.camera.x
        for snowflake in self.snowflakes:
            snowflake.update(camera_dx)

        # Generate new platforms as needed
        while self.last_platform_x < self.santa.world_x + SCREEN_WIDTH * 2:
            self.generate_next_platform()

        # Update game objects
        update_result = self.santa.update(self.platforms)
        if update_result == "game_over":
            self.state = GAME_OVER
            if self.score > self.high_score:
                self.high_score = self.score
            return
        elif update_result == "collect_star":
            # Points are awarded when collecting star (landing on chimney)
            if self.santa.presents > 0:
                self.score += self.santa.presents * PRESENT_POINTS
                self.santa.presents = 0
            self.sound_manager.play("collect")

        # Update Grunch and handle point stealing
        grunch_result = self.grunch.update(self.platforms)
        if grunch_result == "steal_points":
            if self.santa.presents > 0:
                # Create both present and "-1" animations at the same position
                stolen_present = StolenPresent(
                    self.santa.world_x, self.santa.y, self.grunch.y
                )
                self.stolen_presents.append(stolen_present)

                # Add "-1" text animation that follows the present
                minus_text = StolenScore(
                    self.santa.world_x,  # Same x as present
                    self.santa.y,  # Same y as present
                    self.grunch.y,
                    "-1",  # Simpler text
                )
                minus_text.follow_present = True  # New flag to follow present
                self.stolen_presents.append(minus_text)

                self.santa.presents = max(0, self.santa.presents - 1)
            else:
                # No presents to steal, take points instead
                if self.score >= POINTS_STOLEN:
                    self.score -= POINTS_STOLEN
                    score_text = StolenScore(
                        self.santa.world_x,
                        self.santa.y,
                        self.grunch.y,
                        f"-{POINTS_STOLEN} pts",  # Added "pts" for clarity
                    )
                    self.stolen_presents.append(score_text)
                else:
                    self.state = GAME_OVER
                    if self.score > self.high_score:
                        self.high_score = self.score

        self.camera.update(self.santa)

        # Update presents
        for present in self.presents:
            present.update()

        # Check present collection with limit
        for present in self.presents:
            if not present.collected:
                if (
                    self.santa.world_x < present.x + present.width
                    and self.santa.world_x + self.santa.width > present.x
                    and self.santa.y < present.y + present.height
                    and self.santa.y + self.santa.height > present.y
                ):
                    if self.santa.presents < MAX_PRESENTS:
                        present.collected = True
                        self.santa.presents += 1
                        self.sound_manager.play("collect")

        # Update stolen presents animations
        self.stolen_presents = [p for p in self.stolen_presents if p.update()]

        # Check collision with Grunch
        if not self.santa.invulnerable:
            if (
                self.santa.world_x < self.grunch.world_x + self.grunch.width
                and self.santa.world_x + self.santa.width > self.grunch.world_x
                and self.santa.y < self.grunch.y + self.grunch.height
                and self.santa.y + self.santa.height > self.grunch.y
            ):
                self.sound_manager.play("hit")
                self.santa.make_invulnerable()

                if self.santa.presents > 0:
                    # Create floating stolen present effect
                    stolen_present = StolenPresent(
                        self.santa.world_x, self.santa.y, self.grunch.y
                    )
                    self.stolen_presents.append(stolen_present)
                    self.grunch.start_celebration()
                    self.santa.presents = max(0, self.santa.presents - 1)
                else:
                    # No presents to steal, take points instead
                    if self.score >= POINTS_STOLEN:
                        self.score -= POINTS_STOLEN
                        self.grunch.start_celebration()
                        # Create floating score text effect
                        score_text = StolenScore(
                            self.santa.world_x,
                            self.santa.y,
                            self.grunch.y,
                            f"-{POINTS_STOLEN}",
                        )
                        self.stolen_presents.append(score_text)
                    else:
                        # Not enough points left, game over
                        self.state = GAME_OVER
                        if self.score > self.high_score:
                            self.high_score = self.score

    def draw_menu(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        title = font.render("Santa vs. The Grunch", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 200))

        font = pygame.font.Font(None, 36)
        prompt = font.render("Press ENTER to Start", True, WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH / 2 - prompt.get_width() / 2, 400))

    def draw_game_over(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        title = font.render("Game Over!", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 200))

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(
            score_text, (SCREEN_WIDTH / 2 - score_text.get_width() / 2, 300)
        )

        high_score_text = font.render(f"High Score: {self.high_score}", True, WHITE)
        self.screen.blit(
            high_score_text, (SCREEN_WIDTH / 2 - high_score_text.get_width() / 2, 350)
        )

        prompt = font.render("Press ENTER to Play Again", True, WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH / 2 - prompt.get_width() / 2, 450))

    def draw_mode_select(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        title = font.render("Select Game Mode", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 150))

        font = pygame.font.Font(None, 36)
        mode1 = font.render("1. Auto-Scroll Mode", True, WHITE)
        mode2 = font.render("2. Free Movement Mode", True, WHITE)
        self.screen.blit(mode1, (SCREEN_WIDTH / 2 - mode1.get_width() / 2, 300))
        self.screen.blit(mode2, (SCREEN_WIDTH / 2 - mode2.get_width() / 2, 350))

        # Add scoring instructions
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "How to Score:",
            "1. Collect presents scattered on the rooftops",
            "2. Deliver them to chimneys for points",
            "3. Each delivered present = 100 points",
            "4. Don't let the Grunch steal your presents!",
        ]
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, WHITE)
            self.screen.blit(
                text, (SCREEN_WIDTH / 2 - text.get_width() / 2, 400 + i * 25)
            )

    def draw_game(self):
        self.screen.fill(BLACK)

        # Round camera position to prevent jittering
        camera_x = int(self.camera.x)

        # Only draw visible platforms and houses
        visible_range = (camera_x - 100, camera_x + SCREEN_WIDTH + 100)

        # Draw game objects in order (back to front)
        for platform in self.platforms:
            if (
                platform.x + platform.width > visible_range[0]
                and platform.x < visible_range[1]
            ):
                platform.house.draw(self.screen, self.camera)
                platform.draw(self.screen, self.camera)

        # Only draw visible presents
        for present in self.presents:
            if (
                present.world_x + present.width > visible_range[0]
                and present.world_x < visible_range[1]
            ):
                present.draw(self.screen, self.camera)

        self.santa.draw(self.screen, self.camera)
        self.grunch.draw(self.screen, self.camera)

        # Draw snowflakes on top
        for snowflake in self.snowflakes:
            snowflake.draw(self.screen)

        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        presents_text = font.render(
            f"Presents: {self.santa.presents}/{MAX_PRESENTS}", True, WHITE
        )
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(presents_text, (10, 50))

    def draw(self):
        if self.state == MENU:
            self.draw_menu()
        elif self.state == MODE_SELECT:
            self.draw_mode_select()
        elif self.state == PLAYING:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
