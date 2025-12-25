"""
Snake Jump - A snake game where you can jump over other snakes!
PYGBAG_REQUIRE=pygame,asyncio,platform,json,math,random,time,os
"""

import pygame
import random
import math
import asyncio
from collections import deque

# Initialize Pygame
pygame.init()

# Set up the display (viewport size - what we see)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Jump")

# World size (larger play area)
WORLD_WIDTH = 2400
WORLD_HEIGHT = 1800

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 191, 255)
YELLOW = (255, 255, 0)
COLORS = [
    (255, 100, 100),  # Light red
    (100, 255, 100),  # Light green
    (100, 100, 255),  # Light blue
    (255, 255, 100),  # Yellow
    (255, 100, 255),  # Magenta
    (100, 255, 255),  # Cyan
    (255, 180, 100),  # Orange
]

# Game constants
SNAKE_SIZE = 12
PLAYER_SPEED = 2.5
AI_SPEED_BASE = 1.5
TURN_SPEED = 0.08
MAX_JUMP_HEIGHT = 60
JUMP_SPEED = 5
FOOD_SIZE = 8
FOOD_SPAWN_RATE = 120
MAX_FOOD = 20
GROWTH_PER_FOOD = 3
GROWTH_PER_KILL = 8
WALL_MARGIN = 10

# Game states
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.shake_intensity = 0
        self.shake_duration = 0
    
    def update(self, target_x, target_y):
        # Smooth follow
        self.target_x = target_x - SCREEN_WIDTH // 2
        self.target_y = target_y - SCREEN_HEIGHT // 2
        
        # Clamp to world bounds
        self.target_x = max(0, min(self.target_x, WORLD_WIDTH - SCREEN_WIDTH))
        self.target_y = max(0, min(self.target_y, WORLD_HEIGHT - SCREEN_HEIGHT))
        
        # Smooth interpolation
        self.x += (self.target_x - self.x) * 0.1
        self.y += (self.target_y - self.y) * 0.1
        
        # Screen shake
        if self.shake_duration > 0:
            self.shake_duration -= 1
    
    def shake(self, intensity=10, duration=10):
        self.shake_intensity = intensity
        self.shake_duration = duration
    
    def get_offset(self):
        shake_x = 0
        shake_y = 0
        if self.shake_duration > 0:
            shake_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            shake_y = random.uniform(-self.shake_intensity, self.shake_intensity)
        return (int(self.x + shake_x), int(self.y + shake_y))
    
    def world_to_screen(self, x, y):
        offset = self.get_offset()
        return (int(x - offset[0]), int(y - offset[1]))


class Particle:
    def __init__(self, x, y, color, velocity=None, lifetime=30, size=4):
        self.x = x
        self.y = y
        self.color = color
        self.vx = velocity[0] if velocity else random.uniform(-3, 3)
        self.vy = velocity[1] if velocity else random.uniform(-3, 3)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, surface, camera):
        alpha = self.lifetime / self.max_lifetime
        size = int(self.size * alpha)
        if size > 0:
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
            if -10 < screen_x < SCREEN_WIDTH + 10 and -10 < screen_y < SCREEN_HEIGHT + 10:
                pygame.draw.circle(surface, self.color, (screen_x, screen_y), size)


class FloatingText:
    def __init__(self, x, y, text, color=YELLOW, size=36):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, size)
        self.lifetime = 60
        self.max_lifetime = 60
    
    def update(self):
        self.y -= 1  # Float upward
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, surface, camera):
        alpha = self.lifetime / self.max_lifetime
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        if -100 < screen_x < SCREEN_WIDTH + 100 and -50 < screen_y < SCREEN_HEIGHT + 50:
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(int(255 * alpha))
            rect = text_surface.get_rect(center=(screen_x, screen_y))
            surface.blit(text_surface, rect)


class BackgroundStar:
    def __init__(self):
        self.x = random.randint(0, WORLD_WIDTH)
        self.y = random.randint(0, WORLD_HEIGHT)
        self.size = random.uniform(1, 3)
        self.brightness = random.randint(40, 100)
        self.twinkle_speed = random.uniform(0.02, 0.08)
        self.twinkle_phase = random.uniform(0, math.pi * 2)
    
    def update(self):
        self.twinkle_phase += self.twinkle_speed
    
    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        if -5 < screen_x < SCREEN_WIDTH + 5 and -5 < screen_y < SCREEN_HEIGHT + 5:
            twinkle = 0.5 + 0.5 * math.sin(self.twinkle_phase)
            brightness = int(self.brightness * twinkle)
            color = (brightness, brightness, brightness + 20)
            pygame.draw.circle(surface, color, (screen_x, screen_y), int(self.size))


class Food:
    def __init__(self):
        self.x = random.randint(FOOD_SIZE + WALL_MARGIN, WORLD_WIDTH - FOOD_SIZE - WALL_MARGIN)
        self.y = random.randint(FOOD_SIZE + WALL_MARGIN, WORLD_HEIGHT - FOOD_SIZE - WALL_MARGIN)
        self.pulse = random.uniform(0, math.pi * 2)
        self.color = YELLOW
    
    def update(self):
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
    
    def draw(self, surface, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        if -20 < screen_x < SCREEN_WIDTH + 20 and -20 < screen_y < SCREEN_HEIGHT + 20:
            size = FOOD_SIZE + math.sin(self.pulse) * 2
            pygame.draw.circle(surface, self.color, (screen_x, screen_y), int(size))
            pygame.draw.circle(surface, WHITE, (screen_x, screen_y), int(size * 0.5))


class Snake:
    def __init__(self, x, y, color, is_player=False, ai_speed=AI_SPEED_BASE):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = PLAYER_SPEED if is_player else ai_speed
        self.length = 15
        self.segments = deque()
        for i in range(self.length):
            seg_x = x - math.cos(self.angle) * i * 3
            seg_y = y - math.sin(self.angle) * i * 3
            self.segments.append((seg_x, seg_y))
        self.color = color
        self.is_player = is_player
        
        # Jump mechanics
        self.jumping = False
        self.jump_height = 0
        self.jump_velocity = 0
        
        # AI behavior
        self.change_direction_timer = 0
        self.direction_change_interval = random.randint(60, 180)
        self.target_angle = self.angle
        self.ai_mode = "wander"  # wander, hunt, flee
        self.ai_target = None
    
    def update_ai(self, player, all_snakes):
        """Smart AI behavior"""
        dist_to_player = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        
        # Determine AI mode based on situation
        if self.length > player.length + 5:
            # We're bigger - hunt the player
            self.ai_mode = "hunt"
            self.ai_target = player
        elif player.length > self.length + 10:
            # Player is much bigger - flee
            self.ai_mode = "flee"
            self.ai_target = player
        elif dist_to_player < 150:
            # Close to player - react based on who's chasing whom
            angle_to_player = math.atan2(player.y - self.y, player.x - self.x)
            player_facing_us = abs(self.normalize_angle(player.angle - angle_to_player)) > math.pi / 2
            
            if player_facing_us:
                self.ai_mode = "flee"
            else:
                self.ai_mode = "hunt"
            self.ai_target = player
        else:
            self.ai_mode = "wander"
            self.ai_target = None
    
    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
    
    def move(self, turn_direction=0, player=None, all_snakes=None):
        if self.is_player:
            self.angle += turn_direction * TURN_SPEED
        else:
            # Update AI behavior
            if player and all_snakes:
                self.update_ai(player, all_snakes)
            
            if self.ai_mode == "hunt" and self.ai_target:
                # Turn towards target
                target_angle = math.atan2(self.ai_target.y - self.y, self.ai_target.x - self.x)
                angle_diff = self.normalize_angle(target_angle - self.angle)
                self.angle += angle_diff * 0.08
            elif self.ai_mode == "flee" and self.ai_target:
                # Turn away from target
                away_angle = math.atan2(self.y - self.ai_target.y, self.x - self.ai_target.x)
                angle_diff = self.normalize_angle(away_angle - self.angle)
                self.angle += angle_diff * 0.06
            else:
                # Wander randomly
                self.change_direction_timer += 1
                if self.change_direction_timer >= self.direction_change_interval:
                    self.target_angle = self.angle + random.uniform(-1.5, 1.5)
                    self.change_direction_timer = 0
                    self.direction_change_interval = random.randint(60, 180)
                
                angle_diff = self.normalize_angle(self.target_angle - self.angle)
                self.angle += angle_diff * 0.05
        
        # Move forward
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # Wall handling
        if self.is_player:
            pass  # Handled in Game.update
        else:
            # AI: bounce off walls
            if self.x < WALL_MARGIN:
                self.x = WALL_MARGIN
                self.angle = math.pi - self.angle
                self.target_angle = self.angle
            elif self.x > WORLD_WIDTH - WALL_MARGIN:
                self.x = WORLD_WIDTH - WALL_MARGIN
                self.angle = math.pi - self.angle
                self.target_angle = self.angle
            if self.y < WALL_MARGIN:
                self.y = WALL_MARGIN
                self.angle = -self.angle
                self.target_angle = self.angle
            elif self.y > WORLD_HEIGHT - WALL_MARGIN:
                self.y = WORLD_HEIGHT - WALL_MARGIN
                self.angle = -self.angle
                self.target_angle = self.angle
        
        self.segments.appendleft((self.x, self.y))
        while len(self.segments) > self.length:
            self.segments.pop()
    
    def check_wall_collision(self):
        return (self.x < WALL_MARGIN or self.x > WORLD_WIDTH - WALL_MARGIN or
                self.y < WALL_MARGIN or self.y > WORLD_HEIGHT - WALL_MARGIN)
    
    def update_jump(self):
        if self.jumping:
            self.jump_height += self.jump_velocity
            self.jump_velocity -= 0.5
            
            if self.jump_height <= 0:
                self.jump_height = 0
                self.jumping = False
                self.jump_velocity = 0
    
    def start_jump(self):
        if not self.jumping:
            self.jumping = True
            self.jump_velocity = JUMP_SPEED
    
    def grow(self, amount=GROWTH_PER_FOOD):
        self.length += amount
    
    def check_collision_with(self, other_snake, collision_distance=SNAKE_SIZE * 1.5):
        head_x, head_y = self.x, self.y
        head_z = self.jump_height
        other_z = 0
        
        for i, (seg_x, seg_y) in enumerate(list(other_snake.segments)[1:]):
            dist_2d = math.sqrt((head_x - seg_x) ** 2 + (head_y - seg_y) ** 2)
            dist_z = abs(head_z - other_z)
            dist_3d = math.sqrt(dist_2d ** 2 + dist_z ** 2)
            
            if dist_3d < collision_distance:
                return True
        return False
    
    def check_self_collision(self, collision_distance=SNAKE_SIZE):
        segments_list = list(self.segments)
        num_segments = len(segments_list)
        if num_segments < 10:
            return False
        
        head_x, head_y = self.x, self.y
        head_z = self.jump_height
        
        for i, (seg_x, seg_y) in enumerate(segments_list[10:], start=10):
            if self.jump_height > 0:
                progress = i / max(1, num_segments - 1)
                seg_z = self.jump_height * (1 - progress * 0.7)
            else:
                seg_z = 0
            
            dist_2d = math.sqrt((head_x - seg_x) ** 2 + (head_y - seg_y) ** 2)
            dist_z = abs(head_z - seg_z)
            dist_3d = math.sqrt(dist_2d ** 2 + dist_z ** 2)
            
            if dist_3d < collision_distance:
                return True
        return False
    
    def check_head_hits_tail(self, other_snake, collision_distance=SNAKE_SIZE * 1.5):
        head_x, head_y = self.x, self.y
        head_z = self.jump_height
        
        segments_list = list(other_snake.segments)
        num_segments = len(segments_list)
        if num_segments < 5:
            return False
        
        for i, (seg_x, seg_y) in enumerate(segments_list[3:], start=3):
            if other_snake.is_player and other_snake.jump_height > 0:
                progress = i / max(1, num_segments - 1)
                seg_z = other_snake.jump_height * (1 - progress * 0.7)
            else:
                seg_z = 0
            
            dist_2d = math.sqrt((head_x - seg_x) ** 2 + (head_y - seg_y) ** 2)
            dist_z = abs(head_z - seg_z)
            dist_3d = math.sqrt(dist_2d ** 2 + dist_z ** 2)
            
            if dist_3d < collision_distance:
                return True
        return False
    
    def draw(self, surface, camera):
        segments_list = list(self.segments)
        num_segments = len(segments_list)
        
        # Draw shadow first (when jumping)
        if self.is_player and self.jump_height > 0:
            shadow_offset = self.jump_height * 0.5
            shadow_alpha = min(180, int(80 + 100 * (self.jump_height / MAX_JUMP_HEIGHT)))
            
            for i, (sx, sy) in enumerate(segments_list):
                progress = i / max(1, num_segments - 1)
                seg_size = SNAKE_SIZE * (1 - progress * 0.6)
                seg_size = max(4, seg_size)
                segment_jump = self.jump_height * (1 - progress * 0.7)
                
                screen_x, screen_y = camera.world_to_screen(sx + shadow_offset * 0.3, sy + segment_jump * 0.8)
                if -20 < screen_x < SCREEN_WIDTH + 20 and -20 < screen_y < SCREEN_HEIGHT + 20:
                    shadow_w = int(seg_size * 2)
                    shadow_h = int(seg_size * 0.8)
                    shadow_surface = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
                    pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), (0, 0, shadow_w, shadow_h))
                    surface.blit(shadow_surface, (screen_x - shadow_w // 2, screen_y - shadow_h // 2))
        
        # Draw snake body
        for i, (x, y) in enumerate(segments_list):
            progress = i / max(1, num_segments - 1)
            size = SNAKE_SIZE * (1 - progress * 0.6)
            size = max(4, size)
            
            if self.is_player and self.jumping:
                segment_jump = self.jump_height * (1 - progress * 0.7)
                draw_y = y - segment_jump
            else:
                draw_y = y
            
            r = int(self.color[0] * (1 - progress * 0.5))
            g = int(self.color[1] * (1 - progress * 0.5))
            b = int(self.color[2] * (1 - progress * 0.5))
            segment_color = (r, g, b)
            
            screen_x, screen_y = camera.world_to_screen(x, draw_y)
            if -20 < screen_x < SCREEN_WIDTH + 20 and -20 < screen_y < SCREEN_HEIGHT + 20:
                if self.is_player:
                    pygame.draw.circle(surface, WHITE, (screen_x, screen_y), int(size + 2))
                pygame.draw.circle(surface, segment_color, (screen_x, screen_y), int(size))
        
        # Draw eyes
        head_x, head_y = segments_list[0]
        if self.is_player and self.jumping:
            head_y -= self.jump_height
        
        screen_hx, screen_hy = camera.world_to_screen(head_x, head_y)
        if -20 < screen_hx < SCREEN_WIDTH + 20 and -20 < screen_hy < SCREEN_HEIGHT + 20:
            eye_offset = SNAKE_SIZE * 0.4
            eye_angle_offset = 0.5
            
            eye1_x = screen_hx + math.cos(self.angle - eye_angle_offset) * eye_offset
            eye1_y = screen_hy + math.sin(self.angle - eye_angle_offset) * eye_offset
            eye2_x = screen_hx + math.cos(self.angle + eye_angle_offset) * eye_offset
            eye2_y = screen_hy + math.sin(self.angle + eye_angle_offset) * eye_offset
            
            pygame.draw.circle(surface, WHITE, (int(eye1_x), int(eye1_y)), 4)
            pygame.draw.circle(surface, WHITE, (int(eye2_x), int(eye2_y)), 4)
            pygame.draw.circle(surface, BLACK, (int(eye1_x), int(eye1_y)), 2)
            pygame.draw.circle(surface, BLACK, (int(eye2_x), int(eye2_y)), 2)


class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.state = MENU
        self.high_score = 0
        self.camera = Camera()
        self.reset_game()
    
    def reset_game(self):
        # Score and stats (initialize first, needed by spawn_ai_snakes)
        self.score = 0
        self.jumps_used = 0
        self.kills = 0
        self.combo = 0
        self.combo_timer = 0
        self.difficulty = 1.0
        
        # Create player at center of world
        self.player = Snake(WORLD_WIDTH // 2, WORLD_HEIGHT // 2, (0, 255, 128), is_player=True)
        
        # Create AI snakes
        self.ai_snakes = []
        self.spawn_ai_snakes(8)
        
        # Food
        self.foods = [Food() for _ in range(15)]
        self.food_timer = 0
        
        # Background stars
        self.stars = [BackgroundStar() for _ in range(200)]
        
        # Effects
        self.particles = []
        self.floating_texts = []
    
    def spawn_ai_snakes(self, count):
        for _ in range(count):
            x = random.randint(100, WORLD_WIDTH - 100)
            y = random.randint(100, WORLD_HEIGHT - 100)
            while math.sqrt((x - self.player.x) ** 2 + (y - self.player.y) ** 2) < 200:
                x = random.randint(100, WORLD_WIDTH - 100)
                y = random.randint(100, WORLD_HEIGHT - 100)
            color = random.choice(COLORS)
            # Faster AI based on difficulty
            ai_speed = AI_SPEED_BASE + (self.difficulty - 1) * 0.3
            snake = Snake(x, y, color, is_player=False, ai_speed=ai_speed)
            # Longer snakes at higher difficulty
            snake.length = 15 + int((self.difficulty - 1) * 5)
            self.ai_snakes.append(snake)
    
    def spawn_death_particles(self, x, y, color, count=20):
        for _ in range(count):
            vx = random.uniform(-5, 5)
            vy = random.uniform(-5, 5)
            self.particles.append(Particle(x, y, color, velocity=(vx, vy), lifetime=40, size=6))
    
    def add_floating_text(self, x, y, text, color=YELLOW):
        self.floating_texts.append(FloatingText(x, y, text, color))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == MENU:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.state = PLAYING
                        self.reset_game()
                
                elif self.state == PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.player.start_jump()
                        self.jumps_used += 1
                
                elif self.state == GAME_OVER:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.state = MENU
        
        return True
    
    def update(self):
        if self.state != PLAYING:
            return
        
        # Handle player input
        keys = pygame.key.get_pressed()
        turn = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            turn = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            turn = 1
        
        # Update player
        self.player.move(turn)
        self.player.update_jump()
        
        # Update camera
        self.camera.update(self.player.x, self.player.y)
        
        # Check wall collision
        if self.player.check_wall_collision():
            self.spawn_death_particles(self.player.x, self.player.y, self.player.color, 30)
            self.camera.shake(15, 20)
            self.game_over()
            return
        
        # Update AI snakes
        for snake in self.ai_snakes:
            snake.move(player=self.player, all_snakes=self.ai_snakes)
        
        # Update food
        for food in self.foods:
            food.update()
        
        # Update background
        for star in self.stars:
            star.update()
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Update floating texts
        self.floating_texts = [t for t in self.floating_texts if t.update()]
        
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0
        
        # Spawn new food
        self.food_timer += 1
        if self.food_timer >= FOOD_SPAWN_RATE and len(self.foods) < MAX_FOOD:
            self.foods.append(Food())
            self.food_timer = 0
        
        # Check food collection
        for food in self.foods[:]:
            dist = math.sqrt((self.player.x - food.x) ** 2 + (self.player.y - food.y) ** 2)
            if dist < SNAKE_SIZE + FOOD_SIZE:
                self.foods.remove(food)
                self.player.grow()
                self.score += 10
                self.add_floating_text(food.x, food.y, "+10", (100, 255, 100))
        
        # Check if AI snakes hit player's tail
        snakes_to_remove = []
        for snake in self.ai_snakes:
            if snake.check_head_hits_tail(self.player):
                snakes_to_remove.append(snake)
                self.player.grow(GROWTH_PER_KILL)
                self.kills += 1
                
                # Combo system
                self.combo += 1
                self.combo_timer = 120  # 2 seconds to maintain combo
                
                multiplier = min(self.combo, 5)
                points = 50 * multiplier
                self.score += points
                
                # Effects
                self.spawn_death_particles(snake.x, snake.y, snake.color, 25)
                self.camera.shake(8, 12)
                
                if multiplier > 1:
                    self.add_floating_text(snake.x, snake.y, f"+{points} x{multiplier}!", (255, 200, 50))
                else:
                    self.add_floating_text(snake.x, snake.y, f"+{points} KILL!", (255, 100, 100))
        
        for snake in snakes_to_remove:
            self.ai_snakes.remove(snake)
        
        # Update difficulty based on score
        self.difficulty = 1.0 + (self.score / 500) * 0.5
        self.difficulty = min(self.difficulty, 3.0)
        
        # Spawn new AI snakes
        target_snakes = 5 + int(self.difficulty * 2)
        while len(self.ai_snakes) < target_snakes:
            self.spawn_ai_snakes(1)
        
        # Check collisions with AI snakes
        for snake in self.ai_snakes:
            if self.player.check_collision_with(snake):
                self.spawn_death_particles(self.player.x, self.player.y, self.player.color, 30)
                self.camera.shake(15, 20)
                self.game_over()
                return
        
        # Check self-collision
        if self.player.check_self_collision():
            self.spawn_death_particles(self.player.x, self.player.y, self.player.color, 30)
            self.camera.shake(15, 20)
            self.game_over()
            return
    
    def game_over(self):
        self.state = GAME_OVER
        if self.score > self.high_score:
            self.high_score = self.score
    
    def draw(self):
        # Clear screen
        screen.fill((15, 18, 25))
        
        if self.state == MENU:
            self.draw_menu()
        elif self.state == PLAYING:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game()
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_menu(self):
        # Draw some stars in background
        for i in range(50):
            x = (i * 37) % SCREEN_WIDTH
            y = (i * 53) % SCREEN_HEIGHT
            brightness = 40 + (i % 60)
            pygame.draw.circle(screen, (brightness, brightness, brightness + 10), (x, y), 1 + i % 2)
        
        # Title
        title = self.font_large.render("SNAKE JUMP", True, (100, 200, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_small.render("Eat food, kill enemies, avoid walls!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50))
        screen.blit(subtitle, subtitle_rect)
        
        # Instructions
        instructions = [
            "← → or A/D to turn",
            "SPACE to jump over snakes",
            "Let enemies hit YOUR tail to kill them!",
            "Build combos for bonus points!",
            "",
            "Press SPACE to start!"
        ]
        for i, text in enumerate(instructions):
            inst = self.font_small.render(text, True, (150, 150, 150))
            inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30 + i * 32))
            screen.blit(inst, inst_rect)
        
        if self.high_score > 0:
            hs = self.font_small.render(f"High Score: {self.high_score}", True, YELLOW)
            hs_rect = hs.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            screen.blit(hs, hs_rect)
    
    def draw_game(self):
        # Draw background stars
        for star in self.stars:
            star.draw(screen, self.camera)
        
        # Draw grid for movement reference
        grid_color = (25, 30, 40)
        offset = self.camera.get_offset()
        for x in range(0, WORLD_WIDTH, 80):
            screen_x = x - offset[0]
            if -1 < screen_x < SCREEN_WIDTH + 1:
                pygame.draw.line(screen, grid_color, (screen_x, 0), (screen_x, SCREEN_HEIGHT))
        for y in range(0, WORLD_HEIGHT, 80):
            screen_y = y - offset[1]
            if -1 < screen_y < SCREEN_HEIGHT + 1:
                pygame.draw.line(screen, grid_color, (0, screen_y), (SCREEN_WIDTH, screen_y))
        
        # Draw world border walls
        wall_color = (255, 80, 80)
        wall_thickness = 6
        # Only draw walls that are visible
        left = -offset[0]
        top = -offset[1]
        right = WORLD_WIDTH - offset[0]
        bottom = WORLD_HEIGHT - offset[1]
        
        if left > -wall_thickness and left < SCREEN_WIDTH:
            pygame.draw.rect(screen, wall_color, (left, max(0, top), wall_thickness, min(SCREEN_HEIGHT, bottom - top)))
        if right > 0 and right < SCREEN_WIDTH + wall_thickness:
            pygame.draw.rect(screen, wall_color, (right - wall_thickness, max(0, top), wall_thickness, min(SCREEN_HEIGHT, bottom - top)))
        if top > -wall_thickness and top < SCREEN_HEIGHT:
            pygame.draw.rect(screen, wall_color, (max(0, left), top, min(SCREEN_WIDTH, right - left), wall_thickness))
        if bottom > 0 and bottom < SCREEN_HEIGHT + wall_thickness:
            pygame.draw.rect(screen, wall_color, (max(0, left), bottom - wall_thickness, min(SCREEN_WIDTH, right - left), wall_thickness))
        
        # Draw food
        for food in self.foods:
            food.draw(screen, self.camera)
        
        # Draw particles (behind snakes)
        for particle in self.particles:
            particle.draw(screen, self.camera)
        
        # Draw AI snakes
        for snake in self.ai_snakes:
            snake.draw(screen, self.camera)
        
        # Draw player
        self.player.draw(screen, self.camera)
        
        # Draw floating texts
        for text in self.floating_texts:
            text.draw(screen, self.camera)
        
        # Draw HUD
        score_text = self.font_small.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        length_text = self.font_small.render(f"Length: {self.player.length}", True, WHITE)
        screen.blit(length_text, (10, 45))
        
        kills_text = self.font_small.render(f"Kills: {self.kills}", True, (255, 100, 100))
        screen.blit(kills_text, (10, 80))
        
        # Combo display
        if self.combo > 1:
            combo_text = self.font_medium.render(f"COMBO x{self.combo}!", True, (255, 200, 50))
            combo_rect = combo_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
            screen.blit(combo_text, combo_rect)
        
        # Jump indicator
        if not self.player.jumping:
            jump_text = self.font_small.render("SPACE to Jump", True, (100, 255, 100))
        else:
            jump_text = self.font_small.render("JUMPING!", True, YELLOW)
        screen.blit(jump_text, (SCREEN_WIDTH - 180, 10))
        
        # Minimap
        self.draw_minimap()
    
    def draw_minimap(self):
        # Minimap in corner
        map_w, map_h = 120, 90
        map_x, map_y = SCREEN_WIDTH - map_w - 10, SCREEN_HEIGHT - map_h - 10
        
        # Background
        pygame.draw.rect(screen, (20, 25, 35), (map_x, map_y, map_w, map_h))
        pygame.draw.rect(screen, (60, 70, 80), (map_x, map_y, map_w, map_h), 1)
        
        # Scale factors
        scale_x = map_w / WORLD_WIDTH
        scale_y = map_h / WORLD_HEIGHT
        
        # Draw AI snakes as dots
        for snake in self.ai_snakes:
            mx = map_x + int(snake.x * scale_x)
            my = map_y + int(snake.y * scale_y)
            pygame.draw.circle(screen, snake.color, (mx, my), 2)
        
        # Draw player
        px = map_x + int(self.player.x * scale_x)
        py = map_y + int(self.player.y * scale_y)
        pygame.draw.circle(screen, (0, 255, 128), (px, py), 3)
        pygame.draw.circle(screen, WHITE, (px, py), 3, 1)
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        go_text = self.font_large.render("GAME OVER", True, RED)
        go_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(go_text, go_rect)
        
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(score_text, score_rect)
        
        stats = self.font_small.render(f"Length: {self.player.length}  |  Kills: {self.kills}  |  Jumps: {self.jumps_used}", True, (150, 150, 150))
        stats_rect = stats.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(stats, stats_rect)
        
        if self.score >= self.high_score and self.score > 0:
            hs_text = self.font_medium.render("NEW HIGH SCORE!", True, YELLOW)
            hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            screen.blit(hs_text, hs_rect)
        
        restart = self.font_small.render("Press SPACE to continue", True, WHITE)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        screen.blit(restart, restart_rect)
    
    async def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            await asyncio.sleep(0)
        
        pygame.quit()


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
else:
    asyncio.create_task(main())
