# /// script
# dependencies = [
#   "pygame",
#   "asyncio",
#   "platform",
#   "json",
#   "math",
#   "random",
#   "time",
#   "os",
#   "python-dotenv",
#   "supabase"
# ]
# ///

"""
Adventures in Space - Space shooter with particle effects and parallax stars
Enhanced version with improved gameplay, power-ups, and leaderboard integration
"""

import asyncio
import pygame
import random
import math
import time
import json
import os
import sys
import platform

# Try to import shared engine modules, provide fallbacks for web builds
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from engine import (
        ScreenShake,
        SpatialGrid,
        check_circle_collision,
        check_circle_rect_collision,
        ObjectPool,
        clamp,
        lerp,
        distance,
    )
except ImportError:
    # Fallback implementations for web builds
    class ScreenShake:
        def __init__(self):
            self.offset_x = 0
            self.offset_y = 0
            self.intensity = 0
            self.duration = 0
        
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
    
    class SpatialGrid:
        def __init__(self, cell_size=64):
            self.cell_size = cell_size
            self.cells = {}
        
        def clear(self):
            self.cells.clear()
        
        def insert(self, obj):
            cx = int(obj.x // self.cell_size)
            cy = int(obj.y // self.cell_size)
            key = (cx, cy)
            if key not in self.cells:
                self.cells[key] = []
            self.cells[key].append(obj)
        
        def get_nearby(self, x, y, radius=1):
            cx = int(x // self.cell_size)
            cy = int(y // self.cell_size)
            nearby = []
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    key = (cx + dx, cy + dy)
                    if key in self.cells:
                        nearby.extend(self.cells[key])
            return nearby
    
    class ObjectPool:
        def __init__(self, cls, size):
            self.cls = cls
            self.pool = [cls() for _ in range(size)]
            self.active = []
        
        def acquire(self):
            if self.pool:
                obj = self.pool.pop()
                self.active.append(obj)
                return obj
            return None
        
        def release(self, obj):
            if obj in self.active:
                self.active.remove(obj)
                self.pool.append(obj)
        
        def release_all(self):
            self.pool.extend(self.active)
            self.active.clear()
    
    def check_circle_collision(x1, y1, r1, x2, y2, r2):
        dx = x1 - x2
        dy = y1 - y2
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < r1 + r2
    
    def check_circle_rect_collision(cx, cy, cr, rx, ry, rw, rh):
        closest_x = max(rx, min(cx, rx + rw))
        closest_y = max(ry, min(cy, ry + rh))
        dx = cx - closest_x
        dy = cy - closest_y
        return (dx * dx + dy * dy) < (cr * cr)
    
    def clamp(value, min_val, max_val):
        return max(min_val, min(max_val, value))
    
    def lerp(a, b, t):
        return a + (b - a) * t
    
    def distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Try to import Supabase configuration, provide fallbacks for web builds
try:
    from supabase_config import save_score, get_leaderboard
except ImportError:
    # Fallback for web builds - no leaderboard functionality
    async def save_score(name, score, level):
        print(f"Score saved locally: {name} - {score} (Level {level})")
        return True
    
    async def get_leaderboard(limit=10):
        return []

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# ============================================================================
# CONFIGURATION
# ============================================================================
class Config:
    """Game configuration constants"""
    # Display
    WIDTH = 800
    HEIGHT = 600
    FPS = 60
    
    # Player
    PLAYER_WIDTH = 50
    PLAYER_HEIGHT = 50
    PLAYER_MAX_SPEED = 8
    PLAYER_ACCELERATION = 0.5
    PLAYER_FRICTION = 0.98
    PLAYER_INITIAL_HEALTH = 100
    PLAYER_INITIAL_AMMO = 15
    PLAYER_INVULNERABLE_FRAMES = 60
    PLAYER_KNOCKBACK_FRAMES = 10
    
    # Bullet
    BULLET_SPEED = 10
    BULLET_RADIUS = 5
    
    # Asteroid
    ASTEROID_BASE_SPEED = 3
    ASTEROID_BASE_SPAWN_RATE = 60
    ASTEROID_MIN_SPAWN_RATE = 15
    ASTEROID_RADIUS = 20
    
    # Pickups
    CARE_PACKAGE_AMMO = 5
    HEALTH_PACK_HEAL = 10
    CARE_PACKAGE_SPAWN_RATE = 300
    HEALTH_PACK_SPAWN_RATE = 240
    
    # Power-ups
    SHIELD_DURATION = 300  # 5 seconds at 60fps
    RAPID_FIRE_DURATION = 300
    RAPID_FIRE_COOLDOWN = 5  # frames between shots
    
    # Level progression
    LEVEL_DURATION = 60  # seconds
    LEVEL_SPEED_MULTIPLIER = 1.2
    
    # Scoring
    SCORE_ASTEROID_DESTROY = 10
    SCORE_HOMING_DESTROY = 25
    SCORE_FAST_DESTROY = 15
    SCORE_SPLITTING_DESTROY = 20


# Global config instance
CFG = Config()


def is_web():
    return platform.system().lower() == "emscripten"


def get_canvas():
    if is_web():
        try:
            import __EMSCRIPTEN__
            from javascript import document
            return document.getElementById("canvas")
        except ImportError:
            print("Running outside web context")
        except Exception as e:
            print(f"Error getting canvas: {e}")
    return None


def init_display():
    canvas = get_canvas()
    if canvas:
        try:
            CFG.WIDTH = canvas.width
            CFG.HEIGHT = canvas.height
            canvas.style.imageRendering = "pixelated"
        except Exception as e:
            print(f"Error setting canvas properties: {e}")
    return pygame.display.set_mode((CFG.WIDTH, CFG.HEIGHT))


# Initialize display
screen = init_display()
pygame.display.set_caption("Adventures in Space")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
BLUE = (0, 191, 255)
YELLOW = (255, 255, 0)
DARK_RED = (139, 0, 0)
PURPLE = (128, 0, 255)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
MAGENTA = (255, 0, 255)


# ============================================================================
# FONTS - Cached for performance
# ============================================================================
class Fonts:
    small = None
    medium = None
    large = None
    title = None
    
    @classmethod
    def init(cls):
        cls.small = pygame.font.Font(None, 24)
        cls.medium = pygame.font.Font(None, 36)
        cls.large = pygame.font.Font(None, 48)
        cls.title = pygame.font.Font(None, 64)


Fonts.init()


# ============================================================================
# PARTICLE SYSTEM (Lightweight inline version)
# ============================================================================
class Particle:
    __slots__ = ['x', 'y', 'vx', 'vy', 'lifetime', 'max_lifetime', 
                 'color', 'size', 'initial_size', 'gravity', 'active']
    
    def __init__(self, x, y, vx, vy, lifetime, color, size, gravity=0):
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
        self.size = self.initial_size * (1 - progress * 0.8)
    
    def draw(self, surface):
        if not self.active or self.size < 1:
            return
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = max(1, int(self.size))
        
        if alpha < 255:
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color[:3], alpha)
            pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
            surface.blit(particle_surf, (int(self.x) - size, int(self.y) - size))
        else:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)


class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def create_explosion(self, x, y, color=ORANGE, count=25, speed=5, size=6):
        """Create an explosion effect"""
        colors = [
            color,
            (min(255, color[0] + 50), max(0, color[1] - 30), max(0, color[2] - 30)),
            YELLOW,
            WHITE
        ]
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            velocity = random.uniform(speed * 0.3, speed)
            vx = math.cos(angle) * velocity
            vy = math.sin(angle) * velocity
            lifetime = random.randint(15, 35)
            particle_color = random.choice(colors)
            particle_size = random.uniform(size * 0.4, size)
            
            self.particles.append(Particle(
                x, y, vx, vy, lifetime, particle_color, particle_size, gravity=0.05
            ))
    
    def create_thrust(self, x, y):
        """Create engine thrust particles"""
        for _ in range(2):
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(2, 4)
            color = random.choice([ORANGE, YELLOW, RED])
            self.particles.append(Particle(
                x + random.uniform(-5, 5), y, vx, vy, 
                random.randint(8, 15), color, random.uniform(3, 6)
            ))
    
    def create_hit(self, x, y, color=RED):
        """Create damage hit effect"""
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            velocity = random.uniform(2, 6)
            vx = math.cos(angle) * velocity
            vy = math.sin(angle) * velocity
            self.particles.append(Particle(
                x, y, vx, vy, random.randint(10, 25), color, random.uniform(3, 7)
            ))
    
    def create_collect(self, x, y, color=GREEN):
        """Create collect/pickup effect"""
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            velocity = random.uniform(1, 3)
            vx = math.cos(angle) * velocity
            vy = math.sin(angle) * velocity - 1
            self.particles.append(Particle(
                x, y, vx, vy, random.randint(15, 30), color, random.uniform(2, 5), gravity=-0.05
            ))
    
    def create_bullet_trail(self, x, y):
        """Create bullet trail"""
        self.particles.append(Particle(
            x + random.uniform(-2, 2), y + 5, 0, 0.5,
            8, (200, 200, 255), 3
        ))
    
    def create_shield_sparkle(self, x, y, radius):
        """Create shield sparkle effect"""
        angle = random.uniform(0, 2 * math.pi)
        px = x + math.cos(angle) * radius
        py = y + math.sin(angle) * radius
        self.particles.append(Particle(
            px, py, random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5),
            random.randint(10, 20), CYAN, random.uniform(2, 4)
        ))
    
    def create_bomb_wave(self, x, y):
        """Create bomb explosion wave"""
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            velocity = random.uniform(8, 15)
            vx = math.cos(angle) * velocity
            vy = math.sin(angle) * velocity
            color = random.choice([WHITE, YELLOW, ORANGE, RED])
            self.particles.append(Particle(
                x, y, vx, vy, random.randint(20, 40), color, random.uniform(4, 10), gravity=0
            ))
    
    def update(self):
        self.particles = [p for p in self.particles if p.active]
        for particle in self.particles:
            particle.update()
    
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)
    
    def clear(self):
        self.particles.clear()


# ============================================================================
# PARALLAX STAR FIELD
# ============================================================================
class ParallaxStar:
    __slots__ = ['x', 'y', 'speed', 'size', 'twinkle', 'twinkle_offset', 
                 'base_brightness', 'color_tint']
    
    def __init__(self, layer_speed, size, twinkle=False):
        self.x = random.randint(0, CFG.WIDTH)
        self.y = random.randint(0, CFG.HEIGHT)
        self.speed = layer_speed
        self.size = size
        self.twinkle = twinkle
        self.twinkle_offset = random.uniform(0, 2 * math.pi)
        self.base_brightness = random.randint(150, 255)
        self.color_tint = random.choice([
            (255, 255, 255),
            (200, 220, 255),
            (255, 240, 220),
            (255, 200, 200),
        ])
    
    def update(self, dt=1):
        self.y += self.speed * dt
        if self.y > CFG.HEIGHT:
            self.y = -self.size
            self.x = random.randint(0, CFG.WIDTH)
    
    def draw(self, surface, time_offset=0):
        if self.twinkle:
            brightness = self.base_brightness + math.sin(time_offset * 3 + self.twinkle_offset) * 50
            brightness = max(100, min(255, brightness))
        else:
            brightness = self.base_brightness
        
        factor = brightness / 255
        color = (
            int(self.color_tint[0] * factor),
            int(self.color_tint[1] * factor),
            int(self.color_tint[2] * factor)
        )
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class StarField:
    def __init__(self):
        self.layers = []
        layer_configs = [
            {"count": 80, "speed": 0.2, "size": 1, "twinkle": False},
            {"count": 60, "speed": 0.5, "size": 1, "twinkle": True},
            {"count": 40, "speed": 0.8, "size": 2, "twinkle": False},
            {"count": 25, "speed": 1.2, "size": 2, "twinkle": True},
            {"count": 15, "speed": 1.8, "size": 3, "twinkle": True},
        ]
        
        for config in layer_configs:
            layer = [ParallaxStar(config["speed"], config["size"], config["twinkle"]) 
                     for _ in range(config["count"])]
            self.layers.append(layer)
        
        self.nebula_spots = []
        for _ in range(8):
            self.nebula_spots.append({
                "x": random.randint(0, CFG.WIDTH),
                "y": random.randint(0, CFG.HEIGHT),
                "size": random.randint(50, 120),
                "color": random.choice([
                    (30, 20, 60),
                    (20, 30, 50),
                    (40, 20, 30),
                    (20, 40, 40),
                ]),
                "speed": random.uniform(0.1, 0.3)
            })
    
    def update(self, dt=1):
        for layer in self.layers:
            for star in layer:
                star.update(dt)
        
        for spot in self.nebula_spots:
            spot["y"] += spot["speed"] * dt
            if spot["y"] > CFG.HEIGHT + spot["size"]:
                spot["y"] = -spot["size"]
                spot["x"] = random.randint(0, CFG.WIDTH)
    
    def draw(self, surface, time_offset=0):
        for spot in self.nebula_spots:
            nebula_surf = pygame.Surface((spot["size"] * 2, spot["size"] * 2), pygame.SRCALPHA)
            for i in range(spot["size"], 0, -5):
                alpha = int(20 * (i / spot["size"]))
                color_with_alpha = (*spot["color"], alpha)
                pygame.draw.circle(nebula_surf, color_with_alpha, 
                                 (spot["size"], spot["size"]), i)
            surface.blit(nebula_surf, (int(spot["x"] - spot["size"]), int(spot["y"] - spot["size"])))
        
        for layer in self.layers:
            for star in layer:
                star.draw(surface, time_offset)


# ============================================================================
# GAME OBJECTS
# ============================================================================
class Bullet:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.active = False
        self.radius = CFG.BULLET_RADIUS
    
    def reset(self, x=0, y=0):
        self.x = x
        self.y = y
        self.active = True
    
    def update(self):
        self.y -= CFG.BULLET_SPEED
        if self.y < -10:
            self.active = False
    
    def draw(self, surface):
        if self.active:
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)
            glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (100, 150, 255, 80), (10, 10), 8)
            surface.blit(glow_surf, (int(self.x) - 10, int(self.y) - 10))


class Asteroid:
    """Standard asteroid with various movement patterns"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.active = False
        self.radius = CFG.ASTEROID_RADIUS
        self.rotation = 0
        self.spin = 0
        self.speed = 3
        self.points = []
        self.pattern = 'straight'
        self.wave_offset = 0
        self.original_x = 0
        self.asteroid_type = 'normal'
        self.score_value = CFG.SCORE_ASTEROID_DESTROY
    
    def reset(self, x=0, speed=3, pattern='straight', asteroid_type='normal'):
        self.x = x
        self.original_x = x
        self.y = -self.radius
        self.active = True
        self.rotation = random.uniform(0, 360)
        self.spin = random.uniform(-3, 3)
        self.speed = speed
        self.pattern = pattern
        self.wave_offset = random.uniform(0, 2 * math.pi)
        self.asteroid_type = asteroid_type
        
        # Set score based on type
        if asteroid_type == 'fast':
            self.score_value = CFG.SCORE_FAST_DESTROY
            self.radius = 15
        elif asteroid_type == 'homing':
            self.score_value = CFG.SCORE_HOMING_DESTROY
            self.radius = 25
        elif asteroid_type == 'splitting':
            self.score_value = CFG.SCORE_SPLITTING_DESTROY
            self.radius = 30
        else:
            self.score_value = CFG.SCORE_ASTEROID_DESTROY
            self.radius = CFG.ASTEROID_RADIUS
        
        # Generate irregular shape
        self.points = []
        num_points = 8
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            variation = random.uniform(0.7, 1.3)
            self.points.append((angle, self.radius * variation))
    
    def update(self, frame, player_x=None, player_y=None):
        self.y += self.speed
        self.rotation += self.spin
        
        if self.pattern == 'zigzag':
            self.x = self.original_x + math.sin(self.y * 0.05 + self.wave_offset) * 50
        elif self.pattern == 'sine':
            self.x = self.original_x + math.sin(self.y * 0.02 + self.wave_offset) * 100
        elif self.pattern == 'homing' and player_x is not None:
            # Slowly track toward player
            dx = player_x - self.x
            self.x += clamp(dx * 0.02, -2, 2)
        
        # Keep in bounds
        self.x = clamp(self.x, self.radius, CFG.WIDTH - self.radius)
        
        if self.y > CFG.HEIGHT + self.radius:
            self.active = False
    
    def draw(self, surface):
        if not self.active:
            return
        
        # Choose color based on type
        if self.asteroid_type == 'fast':
            fill_color = ORANGE
            outline_color = YELLOW
        elif self.asteroid_type == 'homing':
            fill_color = PURPLE
            outline_color = MAGENTA
        elif self.asteroid_type == 'splitting':
            fill_color = (150, 100, 50)
            outline_color = (100, 70, 30)
        else:
            fill_color = RED
            outline_color = DARK_RED
        
        # Draw irregular asteroid shape
        points = []
        for angle, radius in self.points:
            rot_angle = angle + math.radians(self.rotation)
            px = self.x + math.cos(rot_angle) * radius
            py = self.y + math.sin(rot_angle) * radius
            points.append((int(px), int(py)))
        
        pygame.draw.polygon(surface, fill_color, points)
        pygame.draw.polygon(surface, outline_color, points, 3)
        
        # Draw indicator for special types
        if self.asteroid_type == 'homing':
            # Draw targeting reticle
            pygame.draw.circle(surface, MAGENTA, (int(self.x), int(self.y)), int(self.radius * 0.3), 1)
        elif self.asteroid_type == 'splitting':
            # Draw crack lines
            pygame.draw.line(surface, outline_color, 
                           (int(self.x - self.radius * 0.5), int(self.y)),
                           (int(self.x + self.radius * 0.5), int(self.y)), 2)


class MiniAsteroid:
    """Small asteroid created when splitting asteroids are destroyed"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.active = False
        self.radius = 10
        self.rotation = 0
        self.spin = 0
        self.score_value = 5
    
    def reset(self, x, y, angle):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * 2
        self.vy = math.sin(angle) * 2 + 2
        self.active = True
        self.rotation = random.uniform(0, 360)
        self.spin = random.uniform(-5, 5)
    
    def update(self, frame):
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.spin
        
        if self.y > CFG.HEIGHT + self.radius or self.x < -self.radius or self.x > CFG.WIDTH + self.radius:
            self.active = False
    
    def draw(self, surface):
        if not self.active:
            return
        
        pygame.draw.circle(surface, (150, 100, 50), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (100, 70, 30), (int(self.x), int(self.y)), self.radius, 2)


class CarePackage:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.active = False
        self.size = 30
        self.bob_offset = random.uniform(0, 2 * math.pi)
    
    def reset(self, x=0):
        self.x = x
        self.y = -self.size
        self.active = True
    
    def update(self, frame):
        self.y += 2
        if self.y > CFG.HEIGHT + self.size:
            self.active = False
    
    def draw(self, surface, frame):
        if not self.active:
            return
        
        bob = math.sin(frame * 0.1 + self.bob_offset) * 3
        y = self.y + bob
        
        rect = pygame.Rect(self.x - self.size//2, y - self.size//2, self.size, self.size)
        pygame.draw.rect(surface, GREEN, rect)
        pygame.draw.rect(surface, (0, 150, 0), rect, 2)
        
        pygame.draw.line(surface, (0, 150, 0), (self.x - self.size//2, y - self.size//2),
                        (self.x + self.size//2, y + self.size//2), 2)
        pygame.draw.line(surface, (0, 150, 0), (self.x - self.size//2, y + self.size//2),
                        (self.x + self.size//2, y - self.size//2), 2)
        
        text = Fonts.small.render("+5", True, WHITE)
        surface.blit(text, (self.x - text.get_width()//2, y - text.get_height()//2))


class HealthPack:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.active = False
        self.size = 15
        self.pulse = 0
    
    def reset(self, x=0):
        self.x = x
        self.y = -self.size * 2
        self.active = True
        self.pulse = 0
    
    def update(self, frame):
        self.y += 2.5
        self.pulse = frame
        if self.y > CFG.HEIGHT + self.size:
            self.active = False
    
    def draw(self, surface, frame):
        if not self.active:
            return
        
        left_center = (int(self.x - self.size // 4), int(self.y))
        right_center = (int(self.x + self.size // 4), int(self.y))
        radius = int(self.size // 4)
        
        pygame.draw.circle(surface, BLUE, left_center, radius)
        pygame.draw.circle(surface, BLUE, right_center, radius)
        
        points = [
            (self.x - self.size // 2, self.y),
            (self.x + self.size // 2, self.y),
            (self.x, self.y + self.size // 2)
        ]
        pygame.draw.polygon(surface, BLUE, [(int(p[0]), int(p[1])) for p in points])
        
        text = Fonts.small.render("+10", True, WHITE)
        surface.blit(text, (self.x - text.get_width()//2, self.y - text.get_height()//2))


class PowerUp:
    """Power-up pickups (shield, rapid fire, bomb)"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.active = False
        self.size = 25
        self.power_type = 'shield'
        self.bob_offset = random.uniform(0, 2 * math.pi)
    
    def reset(self, x=0, power_type='shield'):
        self.x = x
        self.y = -self.size
        self.active = True
        self.power_type = power_type
        self.bob_offset = random.uniform(0, 2 * math.pi)
    
    def update(self, frame):
        self.y += 1.5
        if self.y > CFG.HEIGHT + self.size:
            self.active = False
    
    def draw(self, surface, frame):
        if not self.active:
            return
        
        bob = math.sin(frame * 0.15 + self.bob_offset) * 4
        y = self.y + bob
        
        # Draw based on power type
        if self.power_type == 'shield':
            # Cyan shield icon
            pygame.draw.circle(surface, CYAN, (int(self.x), int(y)), self.size // 2)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(y)), self.size // 2, 2)
            # Shield symbol
            points = [(self.x, y - 8), (self.x - 6, y - 2), 
                     (self.x - 6, y + 4), (self.x, y + 8),
                     (self.x + 6, y + 4), (self.x + 6, y - 2)]
            pygame.draw.polygon(surface, WHITE, [(int(p[0]), int(p[1])) for p in points], 2)
        
        elif self.power_type == 'rapid_fire':
            # Orange rapid fire icon
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(y)), self.size // 2)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(y)), self.size // 2, 2)
            # Bullet symbols
            for offset in [-5, 0, 5]:
                pygame.draw.line(surface, WHITE, (int(self.x + offset), int(y + 8)),
                               (int(self.x + offset), int(y - 8)), 2)
        
        elif self.power_type == 'bomb':
            # Red bomb icon
            pygame.draw.circle(surface, RED, (int(self.x), int(y)), self.size // 2)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(y)), self.size // 2, 2)
            # Bomb symbol
            pygame.draw.circle(surface, BLACK, (int(self.x), int(y)), self.size // 4)
            pygame.draw.line(surface, ORANGE, (int(self.x), int(y - self.size // 4)),
                           (int(self.x), int(y - self.size // 2)), 3)


class FloatingText:
    def __init__(self, text, x, y, color=WHITE):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = 40
        self.max_lifetime = 40
    
    @property
    def active(self):
        return self.lifetime > 0
    
    def update(self):
        self.y -= 1.5
        self.lifetime -= 1
    
    def draw(self, surface):
        if self.lifetime <= 0:
            return
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        text_surf = Fonts.medium.render(self.text, True, self.color)
        
        alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.fill((255, 255, 255, alpha))
        text_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        surface.blit(text_surf, (self.x - text_surf.get_width()//2, int(self.y)))


# ============================================================================
# PLAYER
# ============================================================================
class Player:
    def __init__(self):
        self.width = CFG.PLAYER_WIDTH
        self.height = CFG.PLAYER_HEIGHT
        self.reset()
    
    def reset(self):
        self.x = CFG.WIDTH // 2 - self.width // 2
        self.y = CFG.HEIGHT - self.height - 10
        self.velocity = 0
        self.health = CFG.PLAYER_INITIAL_HEALTH
        self.ammo = CFG.PLAYER_INITIAL_AMMO
        self.invulnerable = 0
        self.knockback_timer = 0
        
        # Power-up states
        self.shield_timer = 0
        self.rapid_fire_timer = 0
        self.rapid_fire_cooldown = 0
    
    def update(self, keys, friction=0.98):
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
        else:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.velocity -= CFG.PLAYER_ACCELERATION
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.velocity += CFG.PLAYER_ACCELERATION
        
        self.velocity *= friction
        self.velocity = clamp(self.velocity, -CFG.PLAYER_MAX_SPEED, CFG.PLAYER_MAX_SPEED)
        self.x += self.velocity
        self.x = clamp(self.x, 0, CFG.WIDTH - self.width)
        
        if self.invulnerable > 0:
            self.invulnerable -= 1
        
        # Update power-up timers
        if self.shield_timer > 0:
            self.shield_timer -= 1
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1
        if self.rapid_fire_cooldown > 0:
            self.rapid_fire_cooldown -= 1
    
    @property
    def has_shield(self):
        return self.shield_timer > 0
    
    @property
    def has_rapid_fire(self):
        return self.rapid_fire_timer > 0
    
    @property
    def center_x(self):
        return self.x + self.width // 2
    
    @property
    def center_y(self):
        return self.y + self.height // 2
    
    def draw(self, surface, frame, particles=None):
        # Flash when invulnerable (but not with shield)
        if self.invulnerable > 0 and not self.has_shield and frame % 6 < 3:
            return
        
        x, y = int(self.x), int(self.y)
        
        # Draw shield effect
        if self.has_shield:
            shield_alpha = 100 + int(math.sin(frame * 0.2) * 50)
            shield_surf = pygame.Surface((self.width + 30, self.height + 30), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (*CYAN, shield_alpha), 
                             (self.width // 2 + 15, self.height // 2 + 15), 
                             max(self.width, self.height) // 2 + 10)
            surface.blit(shield_surf, (x - 15, y - 15))
            
            # Sparkle particles
            if particles and frame % 5 == 0:
                particles.create_shield_sparkle(
                    self.center_x, self.center_y, 
                    max(self.width, self.height) // 2 + 10
                )
        
        # Spaceship body
        ship_points = [
            (x + self.width // 2, y),
            (x, y + self.height),
            (x + self.width // 2, y + self.height - 10),
            (x + self.width, y + self.height),
        ]
        
        # Color based on power-ups
        ship_color = WHITE
        if self.has_rapid_fire:
            ship_color = ORANGE if frame % 10 < 5 else WHITE
        
        pygame.draw.polygon(surface, ship_color, ship_points)
        
        # Engine flames (animated)
        flame_offset = math.sin(frame * 0.5) * 3
        flame_size = 1.5 if self.has_rapid_fire else 1.0
        flame_points = [
            (x + self.width // 2 - int(10 * flame_size), y + self.height),
            (x + self.width // 2, y + self.height + int((10 + flame_offset) * flame_size)),
            (x + self.width // 2 + int(10 * flame_size), y + self.height),
        ]
        pygame.draw.polygon(surface, ORANGE, flame_points)
        
        inner_flame_points = [
            (x + self.width // 2 - int(5 * flame_size), y + self.height),
            (x + self.width // 2, y + self.height + int((6 + flame_offset) * flame_size)),
            (x + self.width // 2 + int(5 * flame_size), y + self.height),
        ]
        pygame.draw.polygon(surface, YELLOW, inner_flame_points)
        
        # Cockpit
        cockpit_rect = pygame.Rect(x + self.width // 4, y + 10, self.width // 2, 8)
        pygame.draw.ellipse(surface, BLUE, cockpit_rect)
    
    def apply_knockback(self, direction, force=15):
        self.velocity = force * direction
        self.knockback_timer = CFG.PLAYER_KNOCKBACK_FRAMES
        self.invulnerable = CFG.PLAYER_INVULNERABLE_FRAMES


# ============================================================================
# MAIN GAME
# ============================================================================
class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.state = "menu"  # menu, playing, paused, game_over
        
        # Screen shake
        self.shake = ScreenShake()
        
        # Spatial grid for collision detection
        self.spatial_grid = SpatialGrid(cell_size=64)
        
        # Game objects
        self.player = Player()
        self.particles = ParticleSystem()
        self.star_field = StarField()
        
        # Object pools
        self.bullet_pool = ObjectPool(Bullet, 50)
        self.asteroid_pool = ObjectPool(Asteroid, 30)
        self.mini_asteroid_pool = ObjectPool(MiniAsteroid, 20)
        self.care_package_pool = ObjectPool(CarePackage, 10)
        self.health_pack_pool = ObjectPool(HealthPack, 10)
        self.power_up_pool = ObjectPool(PowerUp, 10)
        
        self.floating_texts = []
        
        # Game state
        self.score = 0
        self.level = 1
        self.level_timer = 0
        self.frame = 0
        self.time_offset = 0
        
        # Level settings
        self.target_speed = CFG.ASTEROID_BASE_SPEED
        self.spawn_rate = CFG.ASTEROID_BASE_SPAWN_RATE
        
        # Name input
        self.player_name = ""
        self.entering_name = False
        self.name_submitted = False
        
        # Leaderboard
        self.leaderboard = []
        
        # Pause menu selection
        self.pause_selection = 0
    
    def reset_game(self):
        self.player.reset()
        self.particles.clear()
        self.bullet_pool.release_all()
        self.asteroid_pool.release_all()
        self.mini_asteroid_pool.release_all()
        self.care_package_pool.release_all()
        self.health_pack_pool.release_all()
        self.power_up_pool.release_all()
        self.floating_texts.clear()
        
        self.score = 0
        self.level = 1
        self.level_timer = time.time()
        self.frame = 0
        self.target_speed = CFG.ASTEROID_BASE_SPEED
        self.spawn_rate = CFG.ASTEROID_BASE_SPAWN_RATE
        
        self.player_name = ""
        self.entering_name = False
        self.name_submitted = False
        self.pause_selection = 0
    
    def spawn_asteroid(self):
        asteroid = self.asteroid_pool.acquire()
        if asteroid:
            x = random.randint(20, CFG.WIDTH - 20)
            
            # Choose type based on level
            type_choices = ['normal', 'normal', 'normal']
            if self.level >= 2:
                type_choices.extend(['fast', 'fast'])
            if self.level >= 3:
                type_choices.append('homing')
            if self.level >= 4:
                type_choices.append('splitting')
            
            asteroid_type = random.choice(type_choices)
            
            # Choose pattern
            if asteroid_type == 'fast':
                pattern = 'straight'
                speed = self.target_speed * 1.8
            elif asteroid_type == 'homing':
                pattern = 'homing'
                speed = self.target_speed * 0.7
            else:
                pattern = random.choices(
                    ['straight', 'zigzag', 'sine'],
                    weights=[0.6, 0.25, 0.15]
                )[0]
                speed = self.target_speed
            
            asteroid.reset(x, speed, pattern, asteroid_type)
    
    def spawn_mini_asteroids(self, x, y):
        """Spawn mini asteroids when a splitting asteroid is destroyed"""
        for i in range(3):
            mini = self.mini_asteroid_pool.acquire()
            if mini:
                angle = (i / 3) * 2 * math.pi + random.uniform(-0.3, 0.3)
                mini.reset(x, y, angle)
    
    def spawn_care_package(self):
        package = self.care_package_pool.acquire()
        if package:
            package.reset(random.randint(30, CFG.WIDTH - 30))
    
    def spawn_health_pack(self):
        pack = self.health_pack_pool.acquire()
        if pack:
            pack.reset(random.randint(30, CFG.WIDTH - 30))
    
    def spawn_power_up(self):
        power_up = self.power_up_pool.acquire()
        if power_up:
            power_type = random.choice(['shield', 'rapid_fire', 'bomb'])
            power_up.reset(random.randint(30, CFG.WIDTH - 30), power_type)
    
    def shoot(self):
        # Check rapid fire
        if self.player.has_rapid_fire:
            if self.player.rapid_fire_cooldown > 0:
                return
            self.player.rapid_fire_cooldown = CFG.RAPID_FIRE_COOLDOWN
        
        if self.player.ammo > 0:
            bullet = self.bullet_pool.acquire()
            if bullet:
                bullet.reset(self.player.center_x, self.player.y)
                self.player.ammo -= 1
    
    def trigger_bomb(self):
        """Destroy all asteroids on screen"""
        self.particles.create_bomb_wave(self.player.center_x, self.player.center_y)
        self.shake.trigger(20, 20)
        
        # Destroy all asteroids
        for asteroid in self.asteroid_pool.active[:]:
            if asteroid.active:
                self.particles.create_explosion(asteroid.x, asteroid.y, ORANGE, 15)
                self.score += asteroid.score_value // 2  # Half points for bomb kills
                asteroid.active = False
                self.asteroid_pool.release(asteroid)
        
        for mini in self.mini_asteroid_pool.active[:]:
            if mini.active:
                self.particles.create_explosion(mini.x, mini.y, ORANGE, 8)
                mini.active = False
                self.mini_asteroid_pool.release(mini)
        
        self.add_floating_text("BOMB!", CFG.WIDTH // 2, CFG.HEIGHT // 2, RED)
    
    def add_floating_text(self, text, x, y, color=WHITE):
        self.floating_texts.append(FloatingText(text, x, y, color))
    
    def check_collisions(self):
        player_cx = self.player.center_x
        player_cy = self.player.center_y
        
        # Build spatial grid
        self.spatial_grid.clear()
        for asteroid in self.asteroid_pool.active:
            if asteroid.active:
                self.spatial_grid.insert(asteroid)
        for mini in self.mini_asteroid_pool.active:
            if mini.active:
                self.spatial_grid.insert(mini)
        
        # Bullets vs asteroids
        for bullet in self.bullet_pool.active[:]:
            if not bullet.active:
                continue
            
            # Check regular asteroids
            nearby = self.spatial_grid.get_nearby(bullet.x, bullet.y)
            for asteroid in nearby:
                if not asteroid.active:
                    continue
                
                if check_circle_collision(bullet.x, bullet.y, bullet.radius,
                                         asteroid.x, asteroid.y, asteroid.radius):
                    bullet.active = False
                    asteroid.active = False
                    self.bullet_pool.release(bullet)
                    
                    # Handle splitting asteroids
                    if hasattr(asteroid, 'asteroid_type') and asteroid.asteroid_type == 'splitting':
                        self.spawn_mini_asteroids(asteroid.x, asteroid.y)
                        self.particles.create_explosion(asteroid.x, asteroid.y, (150, 100, 50), 20)
                    else:
                        self.particles.create_explosion(asteroid.x, asteroid.y, ORANGE, 25)
                    
                    self.score += asteroid.score_value
                    self.shake.trigger(5, 8)
                    
                    # Release from appropriate pool
                    if isinstance(asteroid, MiniAsteroid):
                        self.mini_asteroid_pool.release(asteroid)
                    else:
                        self.asteroid_pool.release(asteroid)
                    break
        
        # Bullets vs pickups
        for bullet in self.bullet_pool.active[:]:
            if not bullet.active:
                continue
            
            for package in self.care_package_pool.active[:]:
                if not package.active:
                    continue
                
                if abs(bullet.x - package.x) < package.size // 2 and abs(bullet.y - package.y) < package.size // 2:
                    bullet.active = False
                    package.active = False
                    self.bullet_pool.release(bullet)
                    self.care_package_pool.release(package)
                    self.particles.create_collect(package.x, package.y, GREEN)
                    self.player.ammo += CFG.CARE_PACKAGE_AMMO
                    self.add_floating_text(f"+{CFG.CARE_PACKAGE_AMMO} AMMO", package.x, package.y, GREEN)
                    break
            
            for pack in self.health_pack_pool.active[:]:
                if not pack.active:
                    continue
                
                if abs(bullet.x - pack.x) < pack.size and abs(bullet.y - pack.y) < pack.size:
                    bullet.active = False
                    pack.active = False
                    self.bullet_pool.release(bullet)
                    self.health_pack_pool.release(pack)
                    self.particles.create_collect(pack.x, pack.y, BLUE)
                    self.player.health = min(CFG.PLAYER_INITIAL_HEALTH, self.player.health + CFG.HEALTH_PACK_HEAL)
                    self.add_floating_text(f"+{CFG.HEALTH_PACK_HEAL} HP", pack.x, pack.y, BLUE)
                    break
            
            for power_up in self.power_up_pool.active[:]:
                if not power_up.active:
                    continue
                
                if abs(bullet.x - power_up.x) < power_up.size and abs(bullet.y - power_up.y) < power_up.size:
                    bullet.active = False
                    power_up.active = False
                    self.bullet_pool.release(bullet)
                    self.collect_power_up(power_up)
                    self.power_up_pool.release(power_up)
                    break
        
        # Player vs asteroids
        if self.player.invulnerable <= 0 and not self.player.has_shield:
            nearby = self.spatial_grid.get_nearby(player_cx, player_cy, radius=2)
            for asteroid in nearby:
                if not asteroid.active:
                    continue
                
                dist = distance(player_cx, player_cy, asteroid.x, asteroid.y)
                if dist < asteroid.radius + 25:
                    asteroid.active = False
                    
                    if isinstance(asteroid, MiniAsteroid):
                        self.mini_asteroid_pool.release(asteroid)
                    else:
                        self.asteroid_pool.release(asteroid)
                    
                    self.particles.create_hit(asteroid.x, asteroid.y, RED)
                    self.particles.create_explosion(asteroid.x, asteroid.y, RED, 15)
                    self.player.health -= 10
                    direction = -1 if asteroid.x > player_cx else 1
                    self.player.apply_knockback(direction)
                    self.shake.trigger(12, 15)
                    
                    if self.player.health <= 0:
                        self.state = "game_over"
                        self.entering_name = True
                    break
        
        # Player contact with pickups
        for package in self.care_package_pool.active[:]:
            if not package.active:
                continue
            
            if check_circle_rect_collision(package.x, package.y, package.size // 2,
                                          self.player.x, self.player.y, 
                                          self.player.width, self.player.height):
                package.active = False
                self.care_package_pool.release(package)
                self.particles.create_collect(package.x, package.y, GREEN)
                self.player.ammo += CFG.CARE_PACKAGE_AMMO
                self.add_floating_text(f"+{CFG.CARE_PACKAGE_AMMO} AMMO", package.x, package.y, GREEN)
        
        for pack in self.health_pack_pool.active[:]:
            if not pack.active:
                continue
            
            if check_circle_rect_collision(pack.x, pack.y, pack.size,
                                          self.player.x, self.player.y,
                                          self.player.width, self.player.height):
                pack.active = False
                self.health_pack_pool.release(pack)
                self.particles.create_collect(pack.x, pack.y, BLUE)
                self.player.health = min(CFG.PLAYER_INITIAL_HEALTH, self.player.health + CFG.HEALTH_PACK_HEAL)
                self.add_floating_text(f"+{CFG.HEALTH_PACK_HEAL} HP", pack.x, pack.y, BLUE)
        
        for power_up in self.power_up_pool.active[:]:
            if not power_up.active:
                continue
            
            if check_circle_rect_collision(power_up.x, power_up.y, power_up.size // 2,
                                          self.player.x, self.player.y,
                                          self.player.width, self.player.height):
                power_up.active = False
                self.collect_power_up(power_up)
                self.power_up_pool.release(power_up)
    
    def collect_power_up(self, power_up):
        """Handle power-up collection"""
        if power_up.power_type == 'shield':
            self.player.shield_timer = CFG.SHIELD_DURATION
            self.add_floating_text("SHIELD!", power_up.x, power_up.y, CYAN)
            self.particles.create_collect(power_up.x, power_up.y, CYAN)
        elif power_up.power_type == 'rapid_fire':
            self.player.rapid_fire_timer = CFG.RAPID_FIRE_DURATION
            self.add_floating_text("RAPID FIRE!", power_up.x, power_up.y, ORANGE)
            self.particles.create_collect(power_up.x, power_up.y, ORANGE)
        elif power_up.power_type == 'bomb':
            self.trigger_bomb()
    
    def update_playing(self):
        keys = pygame.key.get_pressed()
        
        # Update player
        friction = CFG.PLAYER_FRICTION - (self.level - 1) * 0.02
        friction = max(0.85, friction)
        self.player.update(keys, friction)
        
        # Create thrust particles
        if self.frame % 3 == 0:
            self.particles.create_thrust(
                self.player.center_x,
                self.player.y + self.player.height
            )
        
        # Rapid fire auto-shoot
        if self.player.has_rapid_fire and (keys[pygame.K_SPACE] or keys[pygame.K_UP]):
            self.shoot()
        
        # Spawn objects
        if self.frame % self.spawn_rate == 0:
            self.spawn_asteroid()
        if self.frame % CFG.CARE_PACKAGE_SPAWN_RATE == 0:
            self.spawn_care_package()
        if self.frame % CFG.HEALTH_PACK_SPAWN_RATE == 0:
            self.spawn_health_pack()
        if self.frame % 600 == 0 and self.level >= 2:  # Power-ups after level 2
            self.spawn_power_up()
        
        # Update objects
        for bullet in self.bullet_pool.active:
            bullet.update()
            if bullet.active and self.frame % 2 == 0:
                self.particles.create_bullet_trail(bullet.x, bullet.y)
        
        for asteroid in self.asteroid_pool.active:
            asteroid.update(self.frame, self.player.center_x, self.player.center_y)
        
        for mini in self.mini_asteroid_pool.active:
            mini.update(self.frame)
        
        for package in self.care_package_pool.active:
            package.update(self.frame)
        
        for pack in self.health_pack_pool.active:
            pack.update(self.frame)
        
        for power_up in self.power_up_pool.active:
            power_up.update(self.frame)
        
        # Clean up inactive objects
        for bullet in self.bullet_pool.active[:]:
            if not bullet.active:
                self.bullet_pool.release(bullet)
        
        for asteroid in self.asteroid_pool.active[:]:
            if not asteroid.active:
                self.asteroid_pool.release(asteroid)
        
        for mini in self.mini_asteroid_pool.active[:]:
            if not mini.active:
                self.mini_asteroid_pool.release(mini)
        
        for package in self.care_package_pool.active[:]:
            if not package.active:
                self.care_package_pool.release(package)
        
        for pack in self.health_pack_pool.active[:]:
            if not pack.active:
                self.health_pack_pool.release(pack)
        
        for power_up in self.power_up_pool.active[:]:
            if not power_up.active:
                self.power_up_pool.release(power_up)
        
        # Update floating texts
        for text in self.floating_texts[:]:
            text.update()
            if not text.active:
                self.floating_texts.remove(text)
        
        # Check collisions
        self.check_collisions()
        
        # Level progression
        if time.time() - self.level_timer >= CFG.LEVEL_DURATION:
            self.level += 1
            self.level_timer = time.time()
            self.target_speed = CFG.ASTEROID_BASE_SPEED * (CFG.LEVEL_SPEED_MULTIPLIER ** (self.level - 1))
            self.spawn_rate = max(CFG.ASTEROID_MIN_SPAWN_RATE, CFG.ASTEROID_BASE_SPAWN_RATE - self.level * 5)
            self.add_floating_text(f"LEVEL {self.level}!", CFG.WIDTH // 2, CFG.HEIGHT // 2, YELLOW)
            self.shake.trigger(8, 15)
    
    def draw_playing(self, surface):
        # Draw game objects
        for bullet in self.bullet_pool.active:
            bullet.draw(surface)
        
        for asteroid in self.asteroid_pool.active:
            asteroid.draw(surface)
        
        for mini in self.mini_asteroid_pool.active:
            mini.draw(surface)
        
        for package in self.care_package_pool.active:
            package.draw(surface, self.frame)
        
        for pack in self.health_pack_pool.active:
            pack.draw(surface, self.frame)
        
        for power_up in self.power_up_pool.active:
            power_up.draw(surface, self.frame)
        
        self.player.draw(surface, self.frame, self.particles)
        self.particles.draw(surface)
        
        for text in self.floating_texts:
            text.draw(surface)
        
        # HUD
        self.draw_hud(surface)
    
    def draw_hud(self, surface):
        # Score
        score_text = Fonts.medium.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_text, (10, 10))
        
        # Health bar
        health_text = Fonts.medium.render("Health:", True, WHITE)
        surface.blit(health_text, (10, 50))
        
        bar_x = 100
        bar_width = 150
        bar_height = 20
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, 52, bar_width, bar_height))
        health_width = int(bar_width * (self.player.health / CFG.PLAYER_INITIAL_HEALTH))
        health_color = GREEN if self.player.health > 50 else YELLOW if self.player.health > 25 else RED
        pygame.draw.rect(surface, health_color, (bar_x, 52, health_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, 52, bar_width, bar_height), 2)
        
        # Ammo
        ammo_color = WHITE if self.player.ammo > 5 else YELLOW if self.player.ammo > 0 else RED
        ammo_text = Fonts.medium.render(f"Ammo: {self.player.ammo}", True, ammo_color)
        surface.blit(ammo_text, (10, 90))
        
        # Level and timer
        level_text = Fonts.medium.render(f"Level: {self.level}", True, WHITE)
        surface.blit(level_text, (CFG.WIDTH - level_text.get_width() - 10, 10))
        
        time_left = max(0, CFG.LEVEL_DURATION - (time.time() - self.level_timer))
        timer_text = Fonts.medium.render(f"Next: {int(time_left)}s", True, WHITE)
        surface.blit(timer_text, (CFG.WIDTH - timer_text.get_width() - 10, 50))
        
        # Power-up indicators
        indicator_y = 130
        if self.player.has_shield:
            shield_time = self.player.shield_timer // 60
            shield_text = Fonts.small.render(f"SHIELD: {shield_time}s", True, CYAN)
            surface.blit(shield_text, (10, indicator_y))
            indicator_y += 25
        
        if self.player.has_rapid_fire:
            rapid_time = self.player.rapid_fire_timer // 60
            rapid_text = Fonts.small.render(f"RAPID FIRE: {rapid_time}s", True, ORANGE)
            surface.blit(rapid_text, (10, indicator_y))
        
        # Controls hint
        controls_text = Fonts.small.render("ESC: Pause", True, (150, 150, 150))
        surface.blit(controls_text, (CFG.WIDTH - controls_text.get_width() - 10, CFG.HEIGHT - 30))
    
    def draw_menu(self, surface):
        # Title
        title = Fonts.title.render("Adventures in Space", True, YELLOW)
        surface.blit(title, (CFG.WIDTH // 2 - title.get_width() // 2, 80))
        
        # Story
        story_lines = [
            "In the year 2157, as an elite Space Defense pilot,",
            "you patrol the dangerous Asteroid Belt.",
            "These aren't normal asteroids - they're moving with purpose,",
            "threatening Earth's outposts. Defend our territory!"
        ]
        y = 180
        for line in story_lines:
            text = Fonts.small.render(line, True, WHITE)
            surface.blit(text, (CFG.WIDTH // 2 - text.get_width() // 2, y))
            y += 30
        
        # Instructions
        instructions = [
            "← → or A D to move",
            "SPACE or ↑ to shoot",
            "",
            "Green boxes: +5 Ammo    Blue hearts: +10 Health",
            "Power-ups unlock at Level 2!"
        ]
        y = 350
        for line in instructions:
            text = Fonts.small.render(line, True, BLUE)
            surface.blit(text, (CFG.WIDTH // 2 - text.get_width() // 2, y))
            y += 28
        
        # Start button
        button_rect = pygame.Rect(CFG.WIDTH // 2 - 100, CFG.HEIGHT - 120, 200, 50)
        mouse_pos = pygame.mouse.get_pos()
        hover = button_rect.collidepoint(mouse_pos)
        
        color = (0, 150, 255) if hover else BLUE
        pygame.draw.rect(surface, color, button_rect)
        pygame.draw.rect(surface, WHITE, button_rect, 2)
        
        start_text = Fonts.medium.render("START MISSION", True, WHITE)
        surface.blit(start_text, (button_rect.centerx - start_text.get_width() // 2,
                                  button_rect.centery - start_text.get_height() // 2))
        
        return button_rect
    
    def draw_pause(self, surface):
        # Semi-transparent overlay
        overlay = pygame.Surface((CFG.WIDTH, CFG.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        title = Fonts.title.render("PAUSED", True, WHITE)
        surface.blit(title, (CFG.WIDTH // 2 - title.get_width() // 2, 150))
        
        options = ["Resume", "Restart", "Quit to Menu"]
        button_rects = []
        
        for i, option in enumerate(options):
            y = 280 + i * 70
            button_rect = pygame.Rect(CFG.WIDTH // 2 - 100, y, 200, 50)
            button_rects.append(button_rect)
            
            mouse_pos = pygame.mouse.get_pos()
            hover = button_rect.collidepoint(mouse_pos) or self.pause_selection == i
            
            color = (0, 150, 255) if hover else BLUE
            pygame.draw.rect(surface, color, button_rect)
            pygame.draw.rect(surface, WHITE, button_rect, 2)
            
            text = Fonts.medium.render(option, True, WHITE)
            surface.blit(text, (button_rect.centerx - text.get_width() // 2,
                               button_rect.centery - text.get_height() // 2))
        
        # Controls hint
        hint = Fonts.small.render("↑↓ to select, ENTER to confirm, ESC to resume", True, (150, 150, 150))
        surface.blit(hint, (CFG.WIDTH // 2 - hint.get_width() // 2, CFG.HEIGHT - 50))
        
        return button_rects
    
    def draw_game_over(self, surface):
        # Semi-transparent overlay
        overlay = pygame.Surface((CFG.WIDTH, CFG.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        title = Fonts.title.render("GAME OVER", True, RED)
        surface.blit(title, (CFG.WIDTH // 2 - title.get_width() // 2, 100))
        
        score_text = Fonts.large.render(f"Final Score: {self.score}", True, WHITE)
        surface.blit(score_text, (CFG.WIDTH // 2 - score_text.get_width() // 2, 180))
        
        level_text = Fonts.medium.render(f"Level Reached: {self.level}", True, WHITE)
        surface.blit(level_text, (CFG.WIDTH // 2 - level_text.get_width() // 2, 230))
        
        if self.entering_name:
            prompt = Fonts.medium.render("Enter your name:", True, WHITE)
            surface.blit(prompt, (CFG.WIDTH // 2 - prompt.get_width() // 2, 300))
            
            input_rect = pygame.Rect(CFG.WIDTH // 2 - 100, 340, 200, 40)
            pygame.draw.rect(surface, WHITE, input_rect, 2)
            
            name_text = Fonts.medium.render(self.player_name + "▋", True, WHITE)
            surface.blit(name_text, (input_rect.centerx - name_text.get_width() // 2,
                                    input_rect.centery - name_text.get_height() // 2))
            
            submit = Fonts.small.render("Press ENTER to submit", True, YELLOW)
            surface.blit(submit, (CFG.WIDTH // 2 - submit.get_width() // 2, 400))
        
        elif self.name_submitted:
            lb_title = Fonts.medium.render("HIGH SCORES", True, YELLOW)
            surface.blit(lb_title, (CFG.WIDTH // 2 - lb_title.get_width() // 2, 300))
            
            y = 350
            for i, entry in enumerate(self.leaderboard[:5]):
                color = GOLD if entry.get('player_name') == self.player_name and entry.get('score') == self.score else WHITE
                entry_text = Fonts.small.render(
                    f"{i+1}. {entry.get('player_name', 'Unknown')}: {entry.get('score', 0)} (Level {entry.get('level', 1)})",
                    True, color
                )
                surface.blit(entry_text, (CFG.WIDTH // 2 - entry_text.get_width() // 2, y))
                y += 30
            
            button_rect = pygame.Rect(CFG.WIDTH // 2 - 100, CFG.HEIGHT - 100, 200, 50)
            mouse_pos = pygame.mouse.get_pos()
            hover = button_rect.collidepoint(mouse_pos)
            
            color = (0, 150, 255) if hover else BLUE
            pygame.draw.rect(surface, color, button_rect)
            pygame.draw.rect(surface, WHITE, button_rect, 2)
            
            replay_text = Fonts.medium.render("PLAY AGAIN", True, WHITE)
            surface.blit(replay_text, (button_rect.centerx - replay_text.get_width() // 2,
                                       button_rect.centery - replay_text.get_height() // 2))
            
            return button_rect
        
        return None
    
    async def submit_score(self):
        """Submit score to leaderboard"""
        try:
            await save_score(self.player_name or "PLAYER", self.score, self.level)
            self.leaderboard = await get_leaderboard(5)
        except Exception as e:
            print(f"Error saving score: {e}")
            # Fallback to local leaderboard
            entry = {"player_name": self.player_name or "PLAYER", 
                     "score": self.score, "level": self.level}
            self.leaderboard.append(entry)
            self.leaderboard.sort(key=lambda x: x.get("score", 0), reverse=True)
            self.leaderboard = self.leaderboard[:5]
    
    async def run(self):
        running = True
        
        while running:
            if is_web():
                await asyncio.sleep(0)
            
            self.frame += 1
            self.time_offset = time.time()
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.state == "menu":
                        button_rect = pygame.Rect(CFG.WIDTH // 2 - 100, CFG.HEIGHT - 120, 200, 50)
                        if button_rect.collidepoint(mouse_pos):
                            self.reset_game()
                            self.state = "playing"
                    
                    elif self.state == "paused":
                        button_rects = [
                            pygame.Rect(CFG.WIDTH // 2 - 100, 280, 200, 50),
                            pygame.Rect(CFG.WIDTH // 2 - 100, 350, 200, 50),
                            pygame.Rect(CFG.WIDTH // 2 - 100, 420, 200, 50),
                        ]
                        for i, rect in enumerate(button_rects):
                            if rect.collidepoint(mouse_pos):
                                if i == 0:  # Resume
                                    self.state = "playing"
                                elif i == 1:  # Restart
                                    self.reset_game()
                                    self.state = "playing"
                                elif i == 2:  # Quit
                                    self.state = "menu"
                    
                    elif self.state == "game_over" and self.name_submitted:
                        button_rect = pygame.Rect(CFG.WIDTH // 2 - 100, CFG.HEIGHT - 100, 200, 50)
                        if button_rect.collidepoint(mouse_pos):
                            self.state = "menu"
                
                elif event.type == pygame.KEYDOWN:
                    if self.state == "playing":
                        if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                            self.shoot()
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "paused"
                            self.pause_selection = 0
                    
                    elif self.state == "paused":
                        if event.key == pygame.K_ESCAPE:
                            self.state = "playing"
                        elif event.key == pygame.K_UP:
                            self.pause_selection = (self.pause_selection - 1) % 3
                        elif event.key == pygame.K_DOWN:
                            self.pause_selection = (self.pause_selection + 1) % 3
                        elif event.key == pygame.K_RETURN:
                            if self.pause_selection == 0:  # Resume
                                self.state = "playing"
                            elif self.pause_selection == 1:  # Restart
                                self.reset_game()
                                self.state = "playing"
                            elif self.pause_selection == 2:  # Quit
                                self.state = "menu"
                    
                    elif self.state == "game_over" and self.entering_name:
                        if event.key == pygame.K_RETURN and self.player_name:
                            self.entering_name = False
                            self.name_submitted = True
                            await self.submit_score()
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif len(self.player_name) < 10 and event.unicode.isalnum():
                            self.player_name += event.unicode.upper()
                    
                    elif self.state == "menu":
                        if event.key == pygame.K_SPACE:
                            self.reset_game()
                            self.state = "playing"
            
            # Update
            self.star_field.update()
            self.particles.update()
            self.shake.update()
            
            if self.state == "playing":
                self.update_playing()
            
            # Draw
            screen.fill(BLACK)
            
            # Create shake surface
            shake_surface = pygame.Surface((CFG.WIDTH, CFG.HEIGHT))
            shake_surface.fill(BLACK)
            
            self.star_field.draw(shake_surface, self.time_offset)
            
            if self.state == "menu":
                self.draw_menu(shake_surface)
            elif self.state == "playing":
                self.draw_playing(shake_surface)
            elif self.state == "paused":
                self.draw_playing(shake_surface)
                self.draw_pause(shake_surface)
            elif self.state == "game_over":
                self.draw_playing(shake_surface)
                self.draw_game_over(shake_surface)
            
            # Apply shake offset
            screen.blit(shake_surface, (self.shake.offset_x, self.shake.offset_y))
            
            pygame.display.flip()
            self.clock.tick(CFG.FPS)
        
        pygame.quit()


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
else:
    # Web platform
    asyncio.create_task(main())
