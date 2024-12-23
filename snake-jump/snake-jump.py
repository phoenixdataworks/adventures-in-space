import pygame
import random
import math
from collections import deque

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Jump")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 191, 255)
COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (255, 165, 0),
]

# Player settings
SNAKE_SIZE = 20
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 5
player_angle = 0
player_segments = deque([(player_x, player_y)])
player_length = 10
player_color = random.choice(COLORS)
jumping = False
jump_height = 0
max_jump_height = 30
jump_speed = 2


# AI Snake settings
class AISnake:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = 3
        self.length = 10
        self.segments = deque([(self.x, self.y)])
        self.color = random.choice(COLORS)
        self.change_direction_timer = 0
        self.direction_change_interval = random.randint(30, 120)

    def move(self):
        # Randomly change direction occasionally
        self.change_direction_timer += 1
        if self.change_direction_timer >= self.direction_change_interval:
            self.angle += random.uniform(-0.5, 0.5)
            self.change_direction_timer = 0
            self.direction_change_interval = random.randint(30, 120)

        # Move snake
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Wrap around screen
        self.x = self.x % WIDTH
        self.y = self.y % HEIGHT

        # Update segments
        self.segments.appendleft((self.x, self.y))
        while len(self.segments) > self.length:
            self.segments.pop()


# Game settings
ai_snakes = [AISnake() for _ in range(5)]
score = 0
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


def draw_snake(segments, color, is_player=False, jump_height=0):
    for i, (x, y) in enumerate(segments):
        # For the player snake when jumping, adjust Y position based on jump height
        draw_y = y - jump_height if is_player else y
        # Make segments get progressively smaller
        size = SNAKE_SIZE - (i * 0.5)
        if size < 5:  # Minimum size for visibility
            size = 5
        pygame.draw.circle(screen, color, (int(x), int(draw_y)), int(size))


def check_collision(x1, y1, x2, y2, min_distance):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) < min_distance


running = True
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not jumping:
                jumping = True

    if not game_over:
        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_angle -= 0.1
        if keys[pygame.K_RIGHT]:
            player_angle += 0.1

    # Draw player snake
    draw_snake(player_segments, player_color, True, jump_height)

    # Draw HUD
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    if game_over:
        game_over_text = font.render("GAME OVER!", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
