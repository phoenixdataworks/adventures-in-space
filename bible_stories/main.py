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
STAMINA_REGEN = 0.15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
SAND_COLOR = (194, 178, 128)
GOLD = (255, 215, 0)
DARK_BLUE = (20, 20, 50)
DESERT_TAN = (210, 180, 140)
MOUNTAIN_GRAY = (105, 105, 105)
WATER_BLUE = (65, 105, 225)
NILE_GREEN = (50, 120, 80)

# Game States
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
LEVEL_COMPLETE = "level_complete"
VICTORY = "victory"

# Level Definitions
LEVELS = {
    1: {
        "name": "Escape from Bethlehem",
        "background": "night_city",
        "obstacles": ["patrol", "crate", "market_stall"],
        "mechanics": ["stealth"],
        "width_multiplier": 3,
    },
    2: {
        "name": "Wilderness of Judea",
        "background": "desert",
        "obstacles": ["ravine", "rock", "scorpion"],
        "mechanics": ["stamina"],
        "width_multiplier": 3.5,
    },
    3: {
        "name": "Mountain Pass",
        "background": "mountains",
        "obstacles": ["falling_rock", "cliff", "patrol"],
        "mechanics": ["wind"],
        "width_multiplier": 3,
    },
    4: {
        "name": "Coastal Route",
        "background": "coast",
        "obstacles": ["patrol", "crate", "tide_pool"],
        "mechanics": ["tides"],
        "width_multiplier": 3.5,
    },
    5: {
        "name": "Nile Delta",
        "background": "river",
        "obstacles": ["crocodile", "quicksand", "reeds"],
        "mechanics": ["swimming"],
        "width_multiplier": 4,
    },
}


# ============================================================================
# PARTICLE SYSTEM
# ============================================================================

class Particle:
    """Individual particle with physics and visual properties."""

    def __init__(self, x, y, vx=0, vy=0, lifetime=60, color=(255, 255, 255),
                 size=5, gravity=0.1, fade=True, shrink=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
        self.initial_size = size
        self.gravity = gravity
        self.fade = fade
        self.shrink = shrink
        self.active = True

    def update(self):
        if not self.active:
            return

        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.98
        self.vy *= 0.98

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
            return

        progress = 1 - (self.lifetime / self.max_lifetime)
        if self.shrink:
            self.size = self.initial_size * (1 - progress)

    def draw(self, surface, camera):
        if not self.active or self.size < 1:
            return

        screen_x = int(self.x - camera.x)
        screen_y = int(self.y)

        if self.fade:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            size = max(1, int(self.size * 2))
            particle_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            color_with_alpha = (*self.color[:3], alpha)
            pygame.draw.circle(particle_surf, color_with_alpha, (size // 2, size // 2), max(1, int(self.size)))
            surface.blit(particle_surf, (screen_x - size // 2, screen_y - size // 2))
        else:
            pygame.draw.circle(surface, self.color, (screen_x, screen_y), max(1, int(self.size)))


class ParticleSystem:
    """Manages all particles in the game."""

    def __init__(self):
        self.particles = []

    def emit(self, x, y, count=10, color=(255, 200, 50), speed_range=(2, 5),
             size_range=(3, 6), lifetime_range=(20, 40), gravity=0.1, 
             angle_range=(0, 360), fade=True, shrink=True):
        for _ in range(count):
            angle = math.radians(random.uniform(*angle_range))
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.randint(*lifetime_range)
            size = random.uniform(*size_range)

            particle = Particle(x, y, vx, vy, lifetime, color, size, gravity, fade, shrink)
            self.particles.append(particle)

    def create_dust(self, x, y):
        """Create dust particles when running."""
        self.emit(x, y, count=3, color=SAND_COLOR, speed_range=(0.5, 2),
                  size_range=(2, 4), lifetime_range=(10, 20), gravity=0.02,
                  angle_range=(200, 340))

    def create_jump_dust(self, x, y):
        """Create dust burst when jumping."""
        self.emit(x, y, count=8, color=SAND_COLOR, speed_range=(1, 3),
                  size_range=(3, 6), lifetime_range=(15, 30), gravity=0.05,
                  angle_range=(180, 360))

    def create_damage(self, x, y):
        """Create damage particles when hit."""
        self.emit(x, y, count=15, color=RED, speed_range=(3, 7),
                  size_range=(4, 8), lifetime_range=(15, 30), gravity=0.15)

    def create_collect(self, x, y):
        """Create sparkle particles when collecting."""
        self.emit(x, y, count=12, color=GOLD, speed_range=(2, 5),
                  size_range=(3, 6), lifetime_range=(20, 35), gravity=-0.05)

    def create_splash(self, x, y):
        """Create water splash particles."""
        self.emit(x, y, count=10, color=WATER_BLUE, speed_range=(2, 5),
                  size_range=(3, 6), lifetime_range=(15, 30), gravity=0.2,
                  angle_range=(200, 340))

    def update(self):
        for p in self.particles[:]:
            p.update()
            if not p.active:
                self.particles.remove(p)

    def draw(self, surface, camera):
        for p in self.particles:
            p.draw(surface, camera)

    def clear(self):
        self.particles.clear()


# ============================================================================
# SCREEN SHAKE
# ============================================================================

class ScreenShake:
    """Handles screen shake effects."""

    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.offset_x = 0
        self.offset_y = 0

    def trigger(self, intensity=10, duration=10):
        self.intensity = intensity
        self.duration = duration

    def update(self):
        if self.duration > 0:
            self.offset_x = random.uniform(-self.intensity, self.intensity)
            self.offset_y = random.uniform(-self.intensity, self.intensity)
            self.intensity *= 0.9
            self.duration -= 1
        else:
            self.offset_x = 0
            self.offset_y = 0


# ============================================================================
# CAMERA
# ============================================================================

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.shake = ScreenShake()

    def apply(self, entity):
        return (entity.x - self.x + self.shake.offset_x, entity.y + self.shake.offset_y)

    def apply_point(self, x, y):
        return (x - self.x + self.shake.offset_x, y + self.shake.offset_y)

    def update(self, target, level_width):
        # Smooth follow at 1/3 of screen
        target_x = target.x - (SCREEN_WIDTH // 3)

        # Only scroll after passing the start area
        if target.x > 200:
            self.target_x = max(0, min(target_x, level_width - SCREEN_WIDTH))

        # Smooth interpolation
        self.x += (self.target_x - self.x) * 0.1

        # Update shake
        self.shake.update()

    def trigger_shake(self, intensity=10, duration=10):
        self.shake.trigger(intensity, duration)


# ============================================================================
# SPRITE LOADING
# ============================================================================

def load_sprite(name, scale=1):
    sizes = {
        "joseph": (60, 80),
        "mary": (60, 80),
        "soldier": (50, 80),
        "donkey": (80, 60),
        "manna": (30, 30),
        "scroll": (25, 35),
        "water_jug": (25, 35),
        "crate": (50, 50),
        "market_stall": (80, 60),
        "rock": (50, 40),
        "scorpion": (40, 30),
        "crocodile": (80, 35),
        "reeds": (40, 80),
    }

    surf = pygame.Surface(sizes.get(name, (50, 50)), pygame.SRCALPHA)

    if name == "joseph":
        # Body (brown robe)
        pygame.draw.rect(surf, BROWN, (20, 30, 20, 45))
        # Head
        pygame.draw.circle(surf, (205, 155, 125), (30, 20), 10)
        # Beard
        pygame.draw.ellipse(surf, BROWN, (25, 15, 10, 15))
        # Arms
        pygame.draw.rect(surf, BROWN, (15, 35, 5, 20))
        pygame.draw.rect(surf, BROWN, (40, 35, 5, 20))
        # Legs
        pygame.draw.rect(surf, (139, 69, 19), (20, 75, 8, 5))
        pygame.draw.rect(surf, (139, 69, 19), (32, 75, 8, 5))
        # Staff
        pygame.draw.line(surf, (139, 69, 19), (45, 30), (45, 80), 3)

    elif name == "mary":
        # Body (blue robe)
        pygame.draw.rect(surf, BLUE, (20, 30, 20, 45))
        # Head covering (white)
        pygame.draw.ellipse(surf, WHITE, (15, 5, 30, 25))
        # Face
        pygame.draw.circle(surf, (225, 198, 153), (30, 20), 8)
        # Baby Jesus (wrapped in white cloth)
        pygame.draw.ellipse(surf, WHITE, (35, 35, 15, 20))
        # Arms holding baby
        pygame.draw.rect(surf, BLUE, (15, 35, 25, 5))
        # Legs
        pygame.draw.rect(surf, BLUE, (20, 75, 8, 5))
        pygame.draw.rect(surf, BLUE, (32, 75, 8, 5))

    elif name == "soldier":
        # Body (red armor)
        pygame.draw.rect(surf, RED, (15, 25, 20, 40))
        # Helmet
        pygame.draw.rect(surf, (192, 192, 192), (15, 5, 20, 20))
        pygame.draw.arc(surf, RED, (15, 0, 20, 20), 0, math.pi, 3)
        # Face
        pygame.draw.circle(surf, (205, 155, 125), (25, 15), 7)
        # Shield
        pygame.draw.rect(surf, (192, 192, 192), (10, 30, 15, 25))
        # Spear
        pygame.draw.line(surf, BROWN, (40, 10), (40, 60), 2)
        pygame.draw.polygon(surf, (192, 192, 192), [(38, 10), (42, 10), (40, 5)])
        # Legs with armor
        pygame.draw.rect(surf, (192, 192, 192), (15, 65, 8, 15))
        pygame.draw.rect(surf, (192, 192, 192), (27, 65, 8, 15))

    elif name == "donkey":
        # Body
        pygame.draw.ellipse(surf, (128, 128, 128), (20, 20, 40, 25))
        # Head
        pygame.draw.ellipse(surf, (128, 128, 128), (10, 15, 20, 15))
        # Ears
        pygame.draw.polygon(surf, (128, 128, 128), [(15, 15), (20, 5), (25, 15)])
        pygame.draw.polygon(surf, (128, 128, 128), [(20, 15), (25, 5), (30, 15)])
        # Legs
        pygame.draw.rect(surf, (128, 128, 128), (25, 45, 5, 15))
        pygame.draw.rect(surf, (128, 128, 128), (50, 45, 5, 15))
        # Tail
        pygame.draw.line(surf, (128, 128, 128), (60, 25), (65, 35), 2)

    elif name == "manna":
        # Golden bread/manna
        pygame.draw.ellipse(surf, GOLD, (5, 10, 20, 15))
        pygame.draw.ellipse(surf, (255, 235, 100), (8, 12, 14, 10))
        # Sparkle
        pygame.draw.line(surf, WHITE, (15, 5), (15, 10), 2)
        pygame.draw.line(surf, WHITE, (10, 7), (20, 7), 2)

    elif name == "scroll":
        # Scroll
        pygame.draw.rect(surf, (245, 222, 179), (5, 5, 15, 25))
        pygame.draw.circle(surf, BROWN, (7, 5), 4)
        pygame.draw.circle(surf, BROWN, (17, 5), 4)
        pygame.draw.circle(surf, BROWN, (7, 30), 4)
        pygame.draw.circle(surf, BROWN, (17, 30), 4)

    elif name == "water_jug":
        # Clay jug
        pygame.draw.ellipse(surf, (180, 120, 60), (5, 10, 15, 20))
        pygame.draw.rect(surf, (180, 120, 60), (8, 5, 9, 8))
        pygame.draw.ellipse(surf, (100, 60, 30), (7, 2, 11, 6))

    elif name == "crate":
        # Wooden crate
        pygame.draw.rect(surf, BROWN, (0, 0, 50, 50))
        pygame.draw.rect(surf, (100, 50, 10), (5, 5, 40, 40))
        # Wood grain
        pygame.draw.line(surf, (80, 40, 5), (5, 15), (45, 15), 2)
        pygame.draw.line(surf, (80, 40, 5), (5, 35), (45, 35), 2)
        pygame.draw.line(surf, (80, 40, 5), (25, 5), (25, 45), 2)

    elif name == "market_stall":
        # Stall structure
        pygame.draw.rect(surf, BROWN, (0, 20, 80, 40))
        # Canopy
        pygame.draw.polygon(surf, (200, 50, 50), [(0, 20), (40, 0), (80, 20)])
        # Goods
        for i in range(5):
            pygame.draw.circle(surf, (200, 100, 50), (10 + i * 15, 40), 8)

    elif name == "rock":
        # Boulder
        pygame.draw.ellipse(surf, (100, 100, 100), (0, 5, 50, 35))
        pygame.draw.ellipse(surf, (130, 130, 130), (5, 10, 35, 20))
        # Cracks
        pygame.draw.line(surf, (70, 70, 70), (15, 15), (25, 30), 2)

    elif name == "scorpion":
        # Scorpion body
        pygame.draw.ellipse(surf, (50, 30, 10), (15, 15, 15, 10))
        # Tail
        pygame.draw.arc(surf, (50, 30, 10), (25, 0, 15, 20), 0, math.pi, 3)
        pygame.draw.circle(surf, (80, 40, 10), (32, 5), 3)
        # Claws
        pygame.draw.ellipse(surf, (50, 30, 10), (0, 12, 12, 8))
        pygame.draw.ellipse(surf, (50, 30, 10), (5, 18, 12, 8))

    elif name == "crocodile":
        # Body
        pygame.draw.ellipse(surf, (0, 100, 50), (10, 10, 50, 20))
        # Snout
        pygame.draw.polygon(surf, (0, 100, 50), [(55, 15), (80, 12), (80, 23), (55, 20)])
        # Eye
        pygame.draw.circle(surf, (255, 255, 0), (70, 14), 3)
        pygame.draw.circle(surf, BLACK, (70, 14), 1)
        # Teeth
        for i in range(4):
            pygame.draw.polygon(surf, WHITE, [(60 + i * 5, 20), (62 + i * 5, 27), (64 + i * 5, 20)])
        # Tail
        pygame.draw.polygon(surf, (0, 100, 50), [(10, 15), (0, 20), (10, 20)])
        # Legs
        pygame.draw.rect(surf, (0, 80, 40), (20, 28, 8, 7))
        pygame.draw.rect(surf, (0, 80, 40), (45, 28, 8, 7))

    elif name == "reeds":
        # Tall reeds for hiding
        for i in range(5):
            x = 5 + i * 8
            pygame.draw.line(surf, (80, 120, 40), (x, 80), (x + random.randint(-3, 3), 10), 3)
            pygame.draw.ellipse(surf, (100, 80, 40), (x - 2, 5, 6, 12))

    elif name == "gateway":
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(surf, (169, 169, 169), (0, 0, 120, 120))
        pygame.draw.rect(surf, BLACK, (30, 20, 60, 100))
        pygame.draw.rect(surf, (192, 192, 192), (0, 0, 30, 120))
        pygame.draw.rect(surf, (192, 192, 192), (90, 0, 30, 120))

    elif name == "desert_cave":
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(surf, (139, 101, 8), (0, 0, 120, 120))
        pygame.draw.ellipse(surf, BLACK, (20, 10, 80, 100))

    elif name == "mountain_pass":
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (105, 105, 105),
                            [(0, 120), (0, 40), (30, 20), (60, 0), (90, 20), (120, 40), (120, 120)])
        pygame.draw.polygon(surf, BLACK, [(40, 120), (50, 60), (70, 60), (80, 120)])
        pygame.draw.polygon(surf, WHITE, [(25, 25), (30, 20), (60, 0), (90, 20), (95, 25)])

    elif name == "coastal_dock":
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(surf, (139, 69, 19), (0, 80, 120, 40))
        for i in range(4):
            pygame.draw.rect(surf, (101, 67, 33), (i * 40, 60, 10, 60))
        pygame.draw.rect(surf, BROWN, (20, 40, 80, 30))
        pygame.draw.polygon(surf, WHITE, [(60, 0), (60, 40), (100, 40)])

    elif name == "pyramid":
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (255, 223, 186), [(0, 120), (60, 0), (120, 120)])
        for y in range(20, 120, 20):
            pygame.draw.line(surf, (139, 69, 19), (y * 0.5, y), (120 - y * 0.5, y), 2)
        pygame.draw.polygon(surf, BLACK, [(50, 120), (60, 100), (70, 120)])

    if scale != 1:
        new_size = (int(surf.get_width() * scale), int(surf.get_height() * scale))
        surf = pygame.transform.scale(surf, new_size)
    return surf


# ============================================================================
# COLLECTIBLE
# ============================================================================

class Collectible:
    def __init__(self, x, y, ctype="manna"):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.type = ctype
        self.active = True
        self.bob_offset = random.uniform(0, math.pi * 2)
        self.sprite = load_sprite(ctype)
        self.base_y = y

        # Points by type
        self.points = {"manna": 50, "scroll": 100, "water_jug": 75}.get(ctype, 50)

    def update(self, time_tick):
        # Bob up and down
        self.y = self.base_y + math.sin(time_tick * 0.1 + self.bob_offset) * 5

    def draw(self, screen, camera):
        if not self.active:
            return
        screen_pos = camera.apply(self)
        if -self.width < screen_pos[0] < SCREEN_WIDTH + self.width:
            screen.blit(self.sprite, screen_pos)


# ============================================================================
# OBSTACLE
# ============================================================================

class Obstacle:
    def __init__(self, x, y, width, height, obstacle_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obstacle_type
        self.active = True
        self.sprite = None
        self.is_hazard = obstacle_type in ["patrol", "scorpion", "crocodile", "quicksand", "falling_rock"]
        self.is_hiding_spot = obstacle_type in ["crate", "market_stall", "reeds"]
        self.is_platform = obstacle_type in ["crate", "rock"]

        # Patrol-specific
        if self.type == "patrol":
            self.direction = 1
            self.patrol_speed = 2
            self.patrol_distance = 150
            self.start_x = x
            self.sprite = load_sprite("soldier")
            self.vision_range = 200
            self.vision_angle = 60

        # Crocodile-specific
        elif self.type == "crocodile":
            self.direction = 1
            self.patrol_speed = 1.5
            self.patrol_distance = 100
            self.start_x = x
            self.sprite = load_sprite("crocodile")
            self.snap_timer = 0

        # Scorpion-specific
        elif self.type == "scorpion":
            self.direction = 1
            self.patrol_speed = 1
            self.patrol_distance = 80
            self.start_x = x
            self.sprite = load_sprite("scorpion")

        # Falling rock specific
        elif self.type == "falling_rock":
            self.sprite = load_sprite("rock")
            self.falling = False
            self.fall_speed = 0
            self.start_y = y
            self.reset_timer = 0

        # Quicksand
        elif self.type == "quicksand":
            self.sink_rate = 0.5

        # Static obstacles
        elif self.type in ["crate", "market_stall", "rock", "reeds"]:
            self.sprite = load_sprite(self.type)

    def update(self, player=None):
        if self.type == "patrol":
            self.x += self.direction * self.patrol_speed
            if abs(self.x - self.start_x) > self.patrol_distance:
                self.direction *= -1

        elif self.type == "crocodile":
            self.x += self.direction * self.patrol_speed
            if abs(self.x - self.start_x) > self.patrol_distance:
                self.direction *= -1
            # Snap animation timer
            self.snap_timer = (self.snap_timer + 1) % 120

        elif self.type == "scorpion":
            self.x += self.direction * self.patrol_speed
            if abs(self.x - self.start_x) > self.patrol_distance:
                self.direction *= -1

        elif self.type == "falling_rock":
            if player and not self.falling:
                # Check if player is below
                if abs(player.x + player.width / 2 - self.x - self.width / 2) < 80:
                    if player.y > self.y:
                        self.falling = True

            if self.falling:
                self.fall_speed += 0.5
                self.y += self.fall_speed
                if self.y > SCREEN_HEIGHT:
                    # Reset
                    self.reset_timer += 1
                    if self.reset_timer > 120:
                        self.y = self.start_y
                        self.falling = False
                        self.fall_speed = 0
                        self.reset_timer = 0

    def can_see_player(self, player):
        """Check if patrol can see the player."""
        if self.type != "patrol":
            return False
        if player.is_hidden:
            return False

        # Distance check
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > self.vision_range:
            return False

        # Direction check (must be facing player)
        if self.direction > 0 and dx < 0:
            return False
        if self.direction < 0 and dx > 0:
            return False

        return True

    def draw(self, screen, camera):
        screen_pos = camera.apply(self)

        if -self.width < screen_pos[0] < SCREEN_WIDTH + self.width:
            if self.sprite:
                if hasattr(self, 'direction') and self.direction < 0:
                    screen.blit(pygame.transform.flip(self.sprite, True, False), screen_pos)
                else:
                    screen.blit(self.sprite, screen_pos)
            elif self.type == "quicksand":
                # Animated quicksand
                pygame.draw.rect(screen, (180, 150, 100), (*screen_pos, self.width, self.height))
                # Bubbles
                for i in range(3):
                    bx = screen_pos[0] + 10 + i * 20 + math.sin(pygame.time.get_ticks() * 0.01 + i) * 5
                    by = screen_pos[1] + 5 + math.sin(pygame.time.get_ticks() * 0.02 + i * 2) * 3
                    pygame.draw.circle(screen, (160, 130, 80), (int(bx), int(by)), 4)
            elif self.type == "tide_pool":
                # Animated water
                wave = math.sin(pygame.time.get_ticks() * 0.005) * 3
                pygame.draw.ellipse(screen, WATER_BLUE, 
                                    (screen_pos[0], screen_pos[1] + wave, self.width, self.height))
            else:
                color = {
                    "platform": BROWN,
                    "cliff": (80, 80, 80),
                }.get(self.type, WHITE)
                pygame.draw.rect(screen, color, (*screen_pos, self.width, self.height))


# ============================================================================
# PLAYER
# ============================================================================

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
        self.lives = 3
        self.score = 0
        self.invincible_timer = 0

        # Animation
        self.animation_frame = 0
        self.animation_timer = 0

        # Sprites
        self.joseph_sprite = load_sprite("joseph")
        self.mary_sprite = load_sprite("mary")
        self.donkey_sprite = load_sprite("donkey")

    def move(self, direction, wind_force=0):
        if self.stamina > 0:
            self.vel_x = direction * MOVE_SPEED + wind_force
            if direction != 0:
                self.facing_right = direction > 0
                self.stamina = max(0, self.stamina - STAMINA_DRAIN)
        else:
            self.vel_x = direction * (MOVE_SPEED * 0.5) + wind_force

    def jump(self):
        if self.on_ground and self.stamina > 15:
            self.vel_y = JUMP_POWER
            self.on_ground = False
            self.stamina = max(0, self.stamina - 15)
            return True
        return False

    def duck(self):
        if not self.is_ducking:
            self.is_ducking = True
            self.height = 40

    def stand(self):
        if self.is_ducking:
            self.is_ducking = False
            self.height = 80

    def take_damage(self):
        if self.invincible_timer > 0:
            return False
        self.lives -= 1
        self.invincible_timer = 90  # 1.5 seconds of invincibility
        return True

    def update(self, platforms, obstacles):
        # Invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        # Apply gravity
        self.vel_y += GRAVITY

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        # Screen boundaries
        self.x = max(0, self.x)

        # Reset ground state
        self.on_ground = False

        # Platform collisions
        for platform in platforms:
            if self.check_platform_collision(platform):
                if self.vel_y > 0:
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.on_ground = True

        # Obstacle platform collisions
        for obstacle in obstacles:
            if obstacle.is_platform and self.check_platform_collision(obstacle):
                if self.vel_y > 0:
                    self.y = obstacle.y - self.height
                    self.vel_y = 0
                    self.on_ground = True

        # Check hiding
        self.is_hidden = False
        for obstacle in obstacles:
            if obstacle.is_hiding_spot and self.check_collision(obstacle):
                self.is_hidden = True
                break

        # Regenerate stamina when on ground and not moving
        if self.on_ground and abs(self.vel_x) < 0.1:
            self.stamina = min(STAMINA_MAX, self.stamina + STAMINA_REGEN * 2)
        elif self.on_ground:
            self.stamina = min(STAMINA_MAX, self.stamina + STAMINA_REGEN)

        # Animation
        if abs(self.vel_x) > 0.5:
            self.animation_timer += 1
            if self.animation_timer > 8:
                self.animation_frame = (self.animation_frame + 1) % 4
                self.animation_timer = 0
        else:
            self.animation_frame = 0

    def check_collision(self, obj):
        return (
            self.x + self.width > obj.x
            and self.x < obj.x + obj.width
            and self.y + self.height > obj.y
            and self.y < obj.y + obj.height
        )

    def check_platform_collision(self, platform):
        # Only collide if falling onto platform
        return (
            self.x + self.width > platform.x
            and self.x < platform.x + platform.width
            and self.y + self.height >= platform.y
            and self.y + self.height <= platform.y + platform.height + self.vel_y + 5
            and self.vel_y >= 0
        )

    def draw(self, screen, camera):
        screen_pos = camera.apply(self)

        # Flicker when invincible
        if self.invincible_timer > 0 and self.invincible_timer % 10 < 5:
            return

        # Walking bob effect
        bob = 0
        if abs(self.vel_x) > 0.5 and self.on_ground:
            bob = math.sin(self.animation_frame * math.pi / 2) * 3

        if self.facing_right:
            screen.blit(self.joseph_sprite, (screen_pos[0] - 20, screen_pos[1] + bob))
            screen.blit(self.mary_sprite, (screen_pos[0] + 20, screen_pos[1] + bob))
            if not self.is_ducking:
                screen.blit(self.donkey_sprite, (screen_pos[0], screen_pos[1] + 20 + bob))
        else:
            screen.blit(
                pygame.transform.flip(self.joseph_sprite, True, False),
                (screen_pos[0] + 20, screen_pos[1] + bob),
            )
            screen.blit(
                pygame.transform.flip(self.mary_sprite, True, False),
                (screen_pos[0] - 20, screen_pos[1] + bob),
            )
            if not self.is_ducking:
                screen.blit(
                    pygame.transform.flip(self.donkey_sprite, True, False),
                    (screen_pos[0], screen_pos[1] + 20 + bob),
                )

        # Hidden indicator
        if self.is_hidden:
            font = pygame.font.Font(None, 20)
            hidden_text = font.render("HIDDEN", True, GREEN)
            screen.blit(hidden_text, (screen_pos[0] + 10, screen_pos[1] - 25))

        # Stamina bar
        self.draw_stamina_bar(screen, screen_pos)

    def draw_stamina_bar(self, screen, screen_pos):
        bar_width = 50
        bar_height = 5
        bar_x = screen_pos[0] + (self.width - bar_width) / 2
        bar_y = screen_pos[1] - 10

        # Background
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        # Stamina fill
        fill_width = bar_width * (self.stamina / STAMINA_MAX)
        color = GREEN if self.stamina > 30 else (255, 165, 0) if self.stamina > 10 else RED
        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))


# ============================================================================
# LEVEL
# ============================================================================

class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.config = LEVELS[level_num]
        self.platforms = []
        self.obstacles = []
        self.collectibles = []
        self.level_width = int(SCREEN_WIDTH * self.config.get("width_multiplier", 3))
        self.gateway = None
        self.time_tick = 0

        # Level-specific mechanics
        self.wind_strength = 0
        self.tide_offset = 0

        self.generate_level()

    def generate_level(self):
        # Ground platforms with gaps
        platform_y = SCREEN_HEIGHT - 40
        x = 0

        while x < self.level_width - 200:
            # Platform length varies
            platform_width = random.randint(150, 300)
            self.platforms.append(Obstacle(x, platform_y, platform_width, 40, "platform"))

            x += platform_width

            # Add gap (some levels have more gaps)
            if self.level_num >= 2 and random.random() < 0.4:
                gap = random.randint(80, 150)
                x += gap

            x += random.randint(20, 50)

        # Final platform to gateway
        self.platforms.append(Obstacle(self.level_width - 250, platform_y, 250, 40, "platform"))

        # Add level-specific obstacles
        self.generate_obstacles()

        # Add collectibles
        self.generate_collectibles()

        # Add exit gateway
        self.add_gateway()

    def generate_obstacles(self):
        obstacle_types = self.config["obstacles"]
        platform_y = SCREEN_HEIGHT - 40

        # Patrols
        if "patrol" in obstacle_types:
            num_patrols = self.level_num + 1
            for i in range(num_patrols):
                x = 400 + i * (self.level_width // (num_patrols + 1))
                self.obstacles.append(Obstacle(x, platform_y - 80, 50, 80, "patrol"))

        # Crates (hiding spots)
        if "crate" in obstacle_types:
            for i in range(3):
                x = 300 + i * 500 + random.randint(-50, 50)
                self.obstacles.append(Obstacle(x, platform_y - 50, 50, 50, "crate"))

        # Market stalls (hiding spots)
        if "market_stall" in obstacle_types:
            for i in range(2):
                x = 500 + i * 600 + random.randint(-50, 50)
                self.obstacles.append(Obstacle(x, platform_y - 60, 80, 60, "market_stall"))

        # Rocks
        if "rock" in obstacle_types:
            for i in range(4):
                x = 350 + i * 400 + random.randint(-100, 100)
                self.obstacles.append(Obstacle(x, platform_y - 40, 50, 40, "rock"))

        # Scorpions
        if "scorpion" in obstacle_types:
            for i in range(3):
                x = 400 + i * 500 + random.randint(-50, 50)
                self.obstacles.append(Obstacle(x, platform_y - 30, 40, 30, "scorpion"))

        # Falling rocks
        if "falling_rock" in obstacle_types:
            for i in range(3):
                x = 500 + i * 400 + random.randint(-50, 50)
                self.obstacles.append(Obstacle(x, 100, 50, 40, "falling_rock"))

        # Crocodiles
        if "crocodile" in obstacle_types:
            for i in range(3):
                x = 400 + i * 600 + random.randint(-50, 50)
                self.obstacles.append(Obstacle(x, platform_y - 35, 80, 35, "crocodile"))

        # Quicksand
        if "quicksand" in obstacle_types:
            for i in range(2):
                x = 600 + i * 700 + random.randint(-50, 50)
                self.obstacles.append(Obstacle(x, platform_y - 10, 100, 20, "quicksand"))

        # Reeds (hiding spots)
        if "reeds" in obstacle_types:
            for i in range(5):
                x = 300 + i * 400 + random.randint(-50, 50)
                self.obstacles.append(Obstacle(x, platform_y - 80, 40, 80, "reeds"))

        # Tide pools
        if "tide_pool" in obstacle_types:
            for i in range(3):
                x = 400 + i * 500 + random.randint(-50, 50)
                self.obstacles.append(Obstacle(x, platform_y - 20, 80, 30, "tide_pool"))

    def generate_collectibles(self):
        platform_y = SCREEN_HEIGHT - 40
        collectible_types = ["manna", "scroll", "water_jug"]

        for i in range(8 + self.level_num * 2):
            x = 250 + i * (self.level_width // (10 + self.level_num * 2))
            y = platform_y - 80 - random.randint(0, 50)
            ctype = random.choice(collectible_types)
            self.collectibles.append(Collectible(x, y, ctype))

    def add_gateway(self):
        platform_y = SCREEN_HEIGHT - 40
        exit_sprites = {
            1: "gateway",
            2: "desert_cave",
            3: "mountain_pass",
            4: "coastal_dock",
            5: "pyramid",
        }

        sprite_name = exit_sprites.get(self.level_num, "gateway")
        self.gateway = Obstacle(
            self.level_width - 180,
            platform_y - 120,
            120,
            120,
            sprite_name,
        )
        self.gateway.sprite = load_sprite(sprite_name)
        self.gateway.is_hazard = False

    def update(self, player):
        self.time_tick += 1

        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.update(player)

        # Update collectibles
        for collectible in self.collectibles:
            collectible.update(self.time_tick)

        # Level-specific mechanics
        if "wind" in self.config["mechanics"]:
            # Wind changes every few seconds
            if self.time_tick % 180 == 0:
                self.wind_strength = random.uniform(-1.5, 1.5)

        if "tides" in self.config["mechanics"]:
            self.tide_offset = math.sin(self.time_tick * 0.02) * 20

    def get_wind_force(self):
        if "wind" in self.config["mechanics"]:
            return self.wind_strength
        return 0

    def draw(self, screen, camera):
        # Draw background
        self.draw_background(screen, camera)

        # Draw platforms
        for platform in self.platforms:
            self.draw_platform(screen, platform, camera)

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(screen, camera)

        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(screen, camera)

        # Draw gateway
        if self.gateway:
            screen_pos = camera.apply(self.gateway)
            if -self.gateway.width < screen_pos[0] < SCREEN_WIDTH + self.gateway.width:
                self.gateway.draw(screen, camera)
                # Draw hint arrow
                if 0 <= screen_pos[0] <= SCREEN_WIDTH:
                    arrow_x = screen_pos[0] + self.gateway.width // 2
                    arrow_y = screen_pos[1] - 30 + math.sin(self.time_tick * 0.1) * 5
                    points = [
                        (arrow_x, arrow_y + 15),
                        (arrow_x - 10, arrow_y),
                        (arrow_x + 10, arrow_y),
                    ]
                    pygame.draw.polygon(screen, GOLD, points)

    def draw_background(self, screen, camera):
        bg_type = self.config["background"]

        if bg_type == "night_city":
            # Gradient sky
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                color = (int(20 + 30 * ratio), int(20 + 20 * ratio), int(50 + 30 * ratio))
                pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
            # Stars
            for i in range(50):
                sx = (i * 137 + int(camera.x * 0.1)) % SCREEN_WIDTH
                sy = (i * 97) % (SCREEN_HEIGHT // 2)
                brightness = 150 + (i % 5) * 20
                pygame.draw.circle(screen, (brightness, brightness, brightness), (sx, sy), 1)
            # Buildings silhouette
            for i in range(10):
                bx = (i * 100 - int(camera.x * 0.3)) % (SCREEN_WIDTH + 200) - 100
                bh = 100 + (i % 4) * 50
                pygame.draw.rect(screen, (30, 30, 50), (bx, SCREEN_HEIGHT - bh - 40, 80, bh))
                # Windows
                for wy in range(SCREEN_HEIGHT - bh - 30, SCREEN_HEIGHT - 50, 20):
                    for wx in range(bx + 10, bx + 70, 20):
                        if random.random() > 0.3:
                            pygame.draw.rect(screen, (255, 200, 100), (wx, wy, 10, 10))

        elif bg_type == "desert":
            # Sky gradient
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                color = (int(135 + 75 * ratio), int(206 - 70 * ratio), int(235 - 130 * ratio))
                pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
            # Far dunes
            for i in range(5):
                dx = (i * 200 - int(camera.x * 0.1)) % (SCREEN_WIDTH + 400) - 200
                points = [(dx, SCREEN_HEIGHT - 100), (dx + 100, SCREEN_HEIGHT - 180),
                          (dx + 200, SCREEN_HEIGHT - 100)]
                pygame.draw.polygon(screen, (220, 180, 120), points)
            # Near dunes
            for i in range(3):
                dx = (i * 350 - int(camera.x * 0.3)) % (SCREEN_WIDTH + 500) - 200
                points = [(dx, SCREEN_HEIGHT - 40), (dx + 150, SCREEN_HEIGHT - 140),
                          (dx + 300, SCREEN_HEIGHT - 40)]
                pygame.draw.polygon(screen, SAND_COLOR, points)

        elif bg_type == "mountains":
            # Sky
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                color = (int(100 + 50 * ratio), int(150 - 50 * ratio), int(200 - 100 * ratio))
                pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
            # Far mountains
            for i in range(4):
                mx = (i * 250 - int(camera.x * 0.1)) % (SCREEN_WIDTH + 400) - 200
                points = [(mx, SCREEN_HEIGHT - 100), (mx + 125, SCREEN_HEIGHT - 300),
                          (mx + 250, SCREEN_HEIGHT - 100)]
                pygame.draw.polygon(screen, (80, 80, 100), points)
                # Snow cap
                pygame.draw.polygon(screen, WHITE, [(mx + 100, SCREEN_HEIGHT - 260),
                                                     (mx + 125, SCREEN_HEIGHT - 300),
                                                     (mx + 150, SCREEN_HEIGHT - 260)])
            # Wind indicator
            if "wind" in self.config["mechanics"] and abs(self.wind_strength) > 0.5:
                wind_dir = ">>>" if self.wind_strength > 0 else "<<<"
                font = pygame.font.Font(None, 30)
                wind_text = font.render(f"WIND {wind_dir}", True, WHITE)
                screen.blit(wind_text, (SCREEN_WIDTH - 120, 50))

        elif bg_type == "coast":
            # Sky
            for y in range(SCREEN_HEIGHT // 2):
                ratio = y / (SCREEN_HEIGHT // 2)
                color = (int(100 + 80 * ratio), int(180 - 30 * ratio), int(255 - 50 * ratio))
                pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
            # Sea
            for y in range(SCREEN_HEIGHT // 2, SCREEN_HEIGHT):
                ratio = (y - SCREEN_HEIGHT // 2) / (SCREEN_HEIGHT // 2)
                wave = math.sin(y * 0.1 + self.time_tick * 0.05) * 3
                color = (int(30 + 40 * ratio), int(80 + 40 * ratio), int(180 - 30 * ratio))
                pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
            # Waves
            for i in range(5):
                wx = (i * 200 + int(self.time_tick * 2) - int(camera.x * 0.2)) % (SCREEN_WIDTH + 200) - 100
                wy = SCREEN_HEIGHT // 2 + 50 + i * 30
                pygame.draw.arc(screen, (200, 230, 255), (wx, wy, 100, 30), 0, math.pi, 3)

        elif bg_type == "river":
            # Gradient from green to darker
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                color = (int(40 + 20 * ratio), int(100 - 30 * ratio), int(60 - 20 * ratio))
                pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
            # River
            river_y = SCREEN_HEIGHT - 80
            pygame.draw.rect(screen, (50, 100, 120), (0, river_y, SCREEN_WIDTH, 40))
            # River flow animation
            for i in range(20):
                rx = (i * 50 + int(self.time_tick * 3) - int(camera.x * 0.5)) % (SCREEN_WIDTH + 100) - 50
                pygame.draw.ellipse(screen, (70, 130, 150), (rx, river_y + 10, 40, 15))

    def draw_platform(self, screen, platform, camera):
        screen_pos = camera.apply(platform)
        if -platform.width < screen_pos[0] < SCREEN_WIDTH + platform.width:
            # Main platform
            bg_type = self.config["background"]
            if bg_type == "night_city":
                color = (60, 50, 40)
            elif bg_type == "desert":
                color = SAND_COLOR
            elif bg_type == "mountains":
                color = MOUNTAIN_GRAY
            elif bg_type == "coast":
                color = (180, 160, 120)
            else:
                color = NILE_GREEN

            pygame.draw.rect(screen, color, (*screen_pos, platform.width, platform.height))
            # Top edge
            pygame.draw.rect(screen, tuple(min(255, c + 30) for c in color),
                             (screen_pos[0], screen_pos[1], platform.width, 5))


# ============================================================================
# GAME
# ============================================================================

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Journey to Egypt")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU
        self.current_level = 1
        self.camera = Camera()
        self.particles = ParticleSystem()
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.level = Level(self.current_level)
        self.camera.x = 0
        self.camera.target_x = 0
        self.particles.clear()
        self.last_player_x = self.player.x

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == MENU:
                    if event.key == pygame.K_RETURN:
                        self.current_level = 1
                        self.state = PLAYING
                        self.reset_game()
                elif self.state == GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        self.state = MENU
                elif self.state == VICTORY:
                    if event.key == pygame.K_RETURN:
                        self.state = MENU
                elif self.state == LEVEL_COMPLETE:
                    if event.key == pygame.K_RETURN:
                        self.current_level += 1
                        self.state = PLAYING
                        self.reset_game()
                elif self.state == PLAYING:
                    if event.key == pygame.K_SPACE:
                        if self.player.jump():
                            self.particles.create_jump_dust(
                                self.player.x + self.player.width // 2,
                                self.player.y + self.player.height
                            )
                    elif event.key == pygame.K_DOWN:
                        self.player.duck()
            elif event.type == pygame.KEYUP:
                if self.state == PLAYING and event.key == pygame.K_DOWN:
                    self.player.stand()

        if self.state == PLAYING:
            keys = pygame.key.get_pressed()
            direction = 0
            if keys[pygame.K_LEFT]:
                direction = -1
            elif keys[pygame.K_RIGHT]:
                direction = 1
            self.player.move(direction, self.level.get_wind_force())

    def update(self):
        if self.state == PLAYING:
            self.player.update(self.level.platforms, self.level.obstacles)
            self.level.update(self.player)
            self.camera.update(self.player, self.level.level_width)
            self.particles.update()

            # Running dust particles
            if self.player.on_ground and abs(self.player.vel_x) > 2:
                if random.random() < 0.3:
                    self.particles.create_dust(
                        self.player.x + self.player.width // 2,
                        self.player.y + self.player.height
                    )

            # Check hazard collisions
            for obstacle in self.level.obstacles:
                if obstacle.active and obstacle.is_hazard:
                    if obstacle.type == "patrol":
                        if obstacle.can_see_player(self.player):
                            if self.player.check_collision(obstacle):
                                if self.player.take_damage():
                                    self.particles.create_damage(self.player.x, self.player.y)
                                    self.camera.trigger_shake(15, 20)
                                    if self.player.lives <= 0:
                                        self.state = GAME_OVER
                    elif self.player.check_collision(obstacle):
                        if obstacle.type == "quicksand":
                            # Slow sinking
                            self.player.vel_y = min(self.player.vel_y, 0.5)
                            self.player.stamina = max(0, self.player.stamina - 1)
                            if self.player.stamina <= 0:
                                if self.player.take_damage():
                                    self.camera.trigger_shake(10, 15)
                                    if self.player.lives <= 0:
                                        self.state = GAME_OVER
                        else:
                            if self.player.take_damage():
                                self.particles.create_damage(self.player.x, self.player.y)
                                self.camera.trigger_shake(15, 20)
                                if self.player.lives <= 0:
                                    self.state = GAME_OVER

            # Check collectible collisions
            for collectible in self.level.collectibles:
                if collectible.active and self.player.check_collision(collectible):
                    collectible.active = False
                    self.player.score += collectible.points
                    self.particles.create_collect(collectible.x, collectible.y)

            # Check death by falling
            if self.player.y > SCREEN_HEIGHT + 100:
                if self.player.take_damage():
                    self.camera.trigger_shake(20, 25)
                    if self.player.lives <= 0:
                        self.state = GAME_OVER
                    else:
                        # Reset position
                        self.player.x = max(100, self.camera.x + 100)
                        self.player.y = SCREEN_HEIGHT - 200
                        self.player.vel_y = 0

            # Check level completion
            if self.level.gateway and self.player.check_collision(self.level.gateway):
                if self.current_level < len(LEVELS):
                    self.state = LEVEL_COMPLETE
                else:
                    self.state = VICTORY

    def draw_menu(self):
        # Background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = (int(10 + 20 * ratio), int(10 + 15 * ratio), int(30 + 20 * ratio))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        # Stars
        for i in range(100):
            sx = (i * 137) % SCREEN_WIDTH
            sy = (i * 97) % SCREEN_HEIGHT
            pygame.draw.circle(self.screen, (200, 200, 200), (sx, sy), 1)

        # Title
        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 36)

        title = font_large.render("Journey to Egypt", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        subtitle = font_small.render("Guide the Holy Family to Safety", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 230))

        # Draw sprites preview
        joseph = load_sprite("joseph")
        mary = load_sprite("mary")
        donkey = load_sprite("donkey")
        self.screen.blit(joseph, (SCREEN_WIDTH // 2 - 80, 300))
        self.screen.blit(mary, (SCREEN_WIDTH // 2, 300))
        self.screen.blit(donkey, (SCREEN_WIDTH // 2 - 40, 340))

        # Instructions
        prompt = font_small.render("Press ENTER to Start", True, WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 450))

        controls = pygame.font.Font(None, 24)
        ctrl_text = controls.render("Arrow Keys: Move | Space: Jump | Down: Duck/Hide", True, (150, 150, 150))
        self.screen.blit(ctrl_text, (SCREEN_WIDTH // 2 - ctrl_text.get_width() // 2, 500))

    def draw_game(self):
        self.level.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        self.particles.draw(self.screen, self.camera)

        # HUD
        font = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 28)

        # Level name
        level_text = font.render(
            f"Level {self.current_level}: {self.level.config['name']}", True, WHITE
        )
        self.screen.blit(level_text, (10, 10))

        # Score
        score_text = font_small.render(f"Score: {self.player.score}", True, GOLD)
        self.screen.blit(score_text, (10, 45))

        # Lives
        for i in range(self.player.lives):
            pygame.draw.circle(self.screen, RED, (SCREEN_WIDTH - 30 - i * 30, 25), 10)
            pygame.draw.circle(self.screen, (200, 50, 50), (SCREEN_WIDTH - 30 - i * 30, 25), 7)

    def draw_game_over(self):
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 36)

        title = font_large.render("Game Over", True, RED)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

        level_text = font_small.render(f"Reached: {self.level.config['name']}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 280))

        score_text = font_small.render(f"Final Score: {self.player.score}", True, GOLD)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 320))

        prompt = font_small.render("Press ENTER to Continue", True, WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 400))

    def draw_level_complete(self):
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))

        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 36)

        title = font_large.render("Level Complete!", True, GREEN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

        score_text = font_small.render(f"Score: {self.player.score}", True, GOLD)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 280))

        next_level = LEVELS.get(self.current_level + 1, {}).get("name", "???")
        next_text = font_small.render(f"Next: {next_level}", True, WHITE)
        self.screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2, 330))

        prompt = font_small.render("Press ENTER to Continue", True, WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 400))

    def draw_victory(self):
        # Golden background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = (int(50 + 100 * ratio), int(40 + 80 * ratio), int(10 + 20 * ratio))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        font_large = pygame.font.Font(None, 74)
        font_med = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)

        title = font_large.render("Victory!", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        subtitle = font_med.render("The Holy Family has reached Egypt!", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 230))

        # Draw pyramid
        pyramid = load_sprite("pyramid")
        self.screen.blit(pyramid, (SCREEN_WIDTH // 2 - 60, 280))

        score_text = font_small.render(f"Final Score: {self.player.score}", True, GOLD)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 420))

        prompt = font_small.render("Press ENTER to Play Again", True, WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 470))

    def draw(self):
        if self.state == MENU:
            self.draw_menu()
        elif self.state == PLAYING:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game()
            self.draw_game_over()
        elif self.state == LEVEL_COMPLETE:
            self.draw_game()
            self.draw_level_complete()
        elif self.state == VICTORY:
            self.draw_victory()

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
