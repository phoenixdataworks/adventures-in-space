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

import asyncio
import pygame
import random
import math
import time
import json
import os
import sys
import platform

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the display
WIDTH = 800
HEIGHT = 600


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
    global WIDTH, HEIGHT
    canvas = get_canvas()
    if canvas:
        try:
            WIDTH = canvas.width
            HEIGHT = canvas.height
            canvas.style.imageRendering = "pixelated"
        except Exception as e:
            print(f"Error setting canvas properties: {e}")

    return pygame.display.set_mode((WIDTH, HEIGHT))


# Initialize display
screen = init_display()
pygame.display.set_caption("Adventures in Space")

# Initialize font
try:
    font = pygame.font.Font(None, 36)
except Exception as e:
    print(f"Error loading font: {e}")
    # Fallback to default system font
    fonts = pygame.font.get_fonts()
    if fonts:
        try:
            font = pygame.font.SysFont(fonts[0], 36)
        except:
            print("Could not load any font")
            # Create a minimal font as last resort
            font = pygame.font.Font(None, 36)

# Mock leaderboard for web version
MOCK_LEADERBOARD = []


async def save_score(player_name, score, level):
    global MOCK_LEADERBOARD
    entry = {"player_name": player_name, "score": score, "level": level}
    MOCK_LEADERBOARD.append(entry)
    MOCK_LEADERBOARD.sort(key=lambda x: x["score"], reverse=True)
    MOCK_LEADERBOARD = MOCK_LEADERBOARD[:5]  # Keep top 5 scores
    return entry


async def get_leaderboard(limit=5):
    return MOCK_LEADERBOARD[:limit]


# Load sounds
def load_sound(name):
    if is_web():
        return pygame.mixer.Sound(f"assets/sounds/{name}.ogg")
    else:
        # For desktop, we can support multiple formats
        for ext in [".ogg", ".wav"]:
            path = f"assets/sounds/{name}{ext}"
            if os.path.exists(path):
                return pygame.mixer.Sound(path)
    return None


# Initialize sounds
# shoot_sound = load_sound("shoot")
# explosion_sound = load_sound("explosion")
# powerup_sound = load_sound("powerup")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
BLUE = (0, 191, 255)
YELLOW = (255, 255, 0)
DARK_RED = (139, 0, 0)  # For asteroid shading

# Game settings
player_width = 50
player_height = 50
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_velocity = 0
player_acceleration = 0.5
player_max_speed = 8
base_friction = 0.98
player_friction = base_friction
min_friction = 0.8
player_health = 100
ammo = 15

# Game state
bullets = []
targets = []
care_packages = []
health_packs = []
explosions = []
score = 0
level = 1
level_timer = time.time()
level_duration = 60
speed_increase = 1.2
target_speed = 3
target_spawn_rate = 60
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
knockback_timer = 0
floating_texts = []

# Game constants
LEADERBOARD_FILE = "leaderboard.json"
MAX_LEADERBOARD_ENTRIES = 5
MAX_NAME_LENGTH = 10
DEFAULT_NAME = "PLAYER"
PLAYER_KNOCKBACK_FORCE = 15
PLAYER_HIT_EXPLOSION_SIZE = 45
KNOCKBACK_DURATION = 10  # frames of knockback effect
HEALTH_BONUS = 10  # Changed from 15 to 10
FLOAT_SPEED = 2  # How fast the text floats up
FLOAT_DURATION = 30  # How many frames the text stays visible

# Game object sizes
BULLET_RADIUS = 5
TARGET_RADIUS = 20
CARE_PACKAGE_SIZE = 30
HEALTH_PACK_SIZE = 5

# Star settings
STAR_LAYERS = [
    {"count": 300, "size": 1},  # Tiny stars
    {"count": 150, "size": 2},  # Medium stars
    {"count": 75, "size": 3},  # Large stars
    {"count": 25, "size": 4},  # Extra bright stars
]


class Star:
    def __init__(self, size):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = size
        # Make all stars very bright
        self.color = (255, 255, 255)  # Pure white

    def draw(self, screen):
        # Draw a filled circle for better visibility
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size, 0)


# Initialize star layers
star_field = []
for layer in STAR_LAYERS:
    stars = [Star(layer["size"]) for _ in range(layer["count"])]
    star_field.append(stars)


def draw_stars():
    # Draw each star as a small filled circle
    for layer in star_field:
        for star in layer:
            pygame.draw.circle(
                screen, star.color, (int(star.x), int(star.y)), star.size, 0
            )


# Game state variables
player_name = ""
entering_name = False
name_submitted = False
game_started = False  # New variable to track if game has started

# Add button constants
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_COLOR = BLUE
BUTTON_HOVER_COLOR = (0, 150, 255)  # Lighter blue for hover

# Story and instructions
STORY_TEXT = """In the year 2157, humanity's insatiable curiosity led you to the far reaches of space. As an elite Space Defense pilot, you patrol the dangerous Asteroid Belt between Mars and Jupiter. But something's wrong - these aren't normal asteroids. They're moving with purpose, threatening Earth's outposts.

Your mission: Defend our space territory using your advanced Nerf-based weapon system. The deeper you venture into space, the faster and more unpredictable the threats become."""

INSTRUCTIONS_TEXT = """CONTROLS:
← → Arrow Keys to move
SPACE to shoot

TIPS:
- Green boxes give ammo (+5)
- Blue boxes restore health (+10)
- Watch out for red asteroids!
- Movement becomes faster and more slippery in higher levels"""


def spawn_target():
    x = random.randint(TARGET_RADIUS, WIDTH - TARGET_RADIUS)
    targets.append(
        {
            "x": x,
            "y": -TARGET_RADIUS,
            "rotation": random.uniform(0, 360),
            "spin": random.uniform(-2, 2),
        }
    )


def spawn_care_package():
    x = random.randint(CARE_PACKAGE_SIZE, WIDTH - CARE_PACKAGE_SIZE)
    care_packages.append({"x": x, "y": -CARE_PACKAGE_SIZE})


def spawn_health_pack():
    x = random.randint(HEALTH_PACK_SIZE, WIDTH - HEALTH_PACK_SIZE)
    health_packs.append({"x": x, "y": -HEALTH_PACK_SIZE})


def draw_player(x, y):
    # Draw spaceship body
    ship_points = [
        (x + player_width // 2, y),  # Nose
        (x, y + player_height),  # Bottom left
        (x + player_width // 2, y + player_height - 10),  # Bottom middle
        (x + player_width, y + player_height),  # Bottom right
    ]
    pygame.draw.polygon(screen, WHITE, ship_points)

    # Draw engine flames
    flame_points = [
        (x + player_width // 2 - 10, y + player_height),
        (x + player_width // 2, y + player_height + 10),
        (x + player_width // 2 + 10, y + player_height),
    ]
    pygame.draw.polygon(screen, ORANGE, flame_points)

    # Draw cockpit
    cockpit_rect = pygame.Rect(x + player_width // 4, y + 10, player_width // 2, 8)
    pygame.draw.ellipse(screen, BLUE, cockpit_rect)

    # Draw health indicator on the wing
    health_text = font.render(str(player_health), True, GREEN)
    text_rect = health_text.get_rect(
        center=(x + player_width // 2, y + player_height // 2)
    )
    screen.blit(health_text, text_rect)


def shoot(x, y):
    global ammo
    if ammo > 0:
        bullets.append({"x": x + player_width // 2, "y": y})
        ammo -= 1
        # if shoot_sound:
        #    shoot_sound.play()


def create_explosion(x, y, size=30):
    explosions.append({"x": x, "y": y, "frame": 0, "size": size})
    # if explosion_sound:
    #    explosion_sound.play()


def draw_name_input(screen, name):
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 40)
    pygame.draw.rect(screen, WHITE, input_box, 2)
    prompt_text = font.render("Enter your name:", True, WHITE)
    screen.blit(prompt_text, (WIDTH // 2 - 100, HEIGHT // 2 - 60))
    name_text = font.render(name + "▋", True, WHITE)
    name_rect = name_text.get_rect(center=input_box.center)
    screen.blit(name_text, name_rect)
    submit_text = font.render("Press ENTER to submit", True, YELLOW)
    screen.blit(submit_text, (WIDTH // 2 - 100, HEIGHT // 2 + 20))


def draw_button(text, x, y, mouse_pos):
    button_rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
    hover = button_rect.collidepoint(mouse_pos)
    color = (0, 150, 255) if hover else BLUE  # Lighter blue for hover
    pygame.draw.rect(screen, color, button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 2)  # White border

    button_text = font.render(text, True, WHITE)
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)
    return button_rect


def reset_game():
    global player_health, player_velocity, player_x, ammo, score, level, level_timer
    global entering_name, name_submitted, player_name, knockback_timer, player_friction
    global target_speed, target_spawn_rate

    # Reset player
    player_health = 100
    player_velocity = 0
    player_x = WIDTH // 2 - player_width // 2
    ammo = 15

    # Reset game state
    score = 0
    level = 1
    level_timer = time.time()
    player_friction = base_friction
    knockback_timer = 0
    target_speed = 3
    target_spawn_rate = 60

    # Clear lists
    bullets.clear()
    targets.clear()
    care_packages.clear()
    health_packs.clear()
    explosions.clear()
    floating_texts.clear()

    # Reset name entry
    entering_name = False
    name_submitted = False
    player_name = ""


def create_floating_text(text, x, y, color=WHITE):
    floating_texts.append({"text": text, "x": x, "y": y, "color": color, "frame": 0})


def draw_start_screen():
    screen.fill(BLACK)
    draw_stars()  # Draw stars before anything else

    # Draw title
    title_font = pygame.font.Font(None, 64)
    title_text = title_font.render("Adventures in Space", True, YELLOW)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_rect().width // 2, 50))

    # Draw story
    y_pos = 150
    wrapped_story = wrap_text(STORY_TEXT, font, WIDTH - 100)
    for line in wrapped_story:
        text_surface = font.render(line, True, WHITE)
        screen.blit(text_surface, (50, y_pos))
        y_pos += 30

    # Draw instructions
    y_pos += 30
    wrapped_instructions = wrap_text(INSTRUCTIONS_TEXT, font, WIDTH - 100)
    for line in wrapped_instructions:
        text_surface = font.render(line, True, BLUE)
        screen.blit(text_surface, (50, y_pos))
        y_pos += 30

    # Draw start button with mouse hover detection
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(
        WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT - 100, BUTTON_WIDTH, BUTTON_HEIGHT
    )
    hover = button_rect.collidepoint(mouse_pos)

    return draw_button(
        "START MISSION", WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT - 100, mouse_pos
    )


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        # Add word to test line
        test_line = current_line + [word]
        test_surface = font.render(" ".join(test_line), True, WHITE)

        # If test line is too wide, save current line and start new one
        if test_surface.get_rect().width > max_width:
            if current_line:  # Only save if there are words in current line
                lines.append(" ".join(current_line))
                current_line = [word]
            else:  # If single word is too long, force it on its own line
                lines.append(word)
                current_line = []
        else:
            current_line = test_line

    # Add the last line if there are remaining words
    if current_line:
        lines.append(" ".join(current_line))

    return lines


def draw_asteroid(screen, x, y, radius, rotation):
    # Create points for an irregular asteroid shape
    points = []
    num_points = 8
    for i in range(num_points):
        angle = math.radians(rotation + (i * 360 / num_points))
        # Vary the radius slightly for each point to make it look more like a real asteroid
        variation = random.uniform(0.8, 1.2)
        point_radius = radius * variation
        point_x = x + math.cos(angle) * point_radius
        point_y = y + math.sin(angle) * point_radius
        points.append((int(point_x), int(point_y)))

    # Draw the main asteroid body
    pygame.draw.polygon(screen, RED, points)

    # Draw some darker craters for detail
    for _ in range(3):
        crater_x = x + random.uniform(-radius / 2, radius / 2)
        crater_y = y + random.uniform(-radius / 2, radius / 2)
        crater_radius = radius / 4
        pygame.draw.circle(
            screen, DARK_RED, (int(crater_x), int(crater_y)), int(crater_radius)
        )

    # Add some highlight lines for texture
    for _ in range(2):
        start_angle = random.uniform(0, math.pi * 2)
        end_angle = start_angle + random.uniform(math.pi / 4, math.pi / 2)
        start_x = x + math.cos(start_angle) * (radius * 0.7)
        start_y = y + math.sin(start_angle) * (radius * 0.7)
        end_x = x + math.cos(end_angle) * (radius * 0.7)
        end_y = y + math.sin(end_angle) * (radius * 0.7)
        pygame.draw.line(
            screen, DARK_RED, (int(start_x), int(start_y)), (int(end_x), int(end_y)), 2
        )


def draw_crate(screen, x, y):
    # Draw main crate body
    crate_rect = pygame.Rect(
        x - CARE_PACKAGE_SIZE // 2,
        y - CARE_PACKAGE_SIZE // 2,
        CARE_PACKAGE_SIZE,
        CARE_PACKAGE_SIZE,
    )
    pygame.draw.rect(screen, GREEN, crate_rect)
    pygame.draw.rect(screen, (0, 100, 0), crate_rect, 2)  # Darker green border

    # Draw ammo symbol
    font = pygame.font.Font(None, 24)
    ammo_text = font.render("+5", True, WHITE)
    text_rect = ammo_text.get_rect(center=(x, y))
    screen.blit(ammo_text, text_rect)

    # Draw cross lines for crate texture
    pygame.draw.line(
        screen,
        (0, 100, 0),
        (x - CARE_PACKAGE_SIZE // 2, y - CARE_PACKAGE_SIZE // 2),
        (x + CARE_PACKAGE_SIZE // 2, y + CARE_PACKAGE_SIZE // 2),
        2,
    )
    pygame.draw.line(
        screen,
        (0, 100, 0),
        (x - CARE_PACKAGE_SIZE // 2, y + CARE_PACKAGE_SIZE // 2),
        (x + CARE_PACKAGE_SIZE // 2, y - CARE_PACKAGE_SIZE // 2),
        2,
    )


def draw_heart(screen, x, y):
    # Calculate heart dimensions
    size = HEALTH_PACK_SIZE * 3  # Make heart slightly larger than original health pack

    # Create the heart shape using circles and a triangle
    left_center = (x - size // 4, y)
    right_center = (x + size // 4, y)
    radius = size // 4

    # Draw the two circles for the top of the heart
    pygame.draw.circle(screen, BLUE, left_center, radius)
    pygame.draw.circle(screen, BLUE, right_center, radius)

    # Draw the triangle for the bottom of the heart
    points = [(x - size // 2, y), (x + size // 2, y), (x, y + size // 2)]
    pygame.draw.polygon(screen, BLUE, points)

    # Add a health symbol
    font = pygame.font.Font(None, 20)
    health_text = font.render("+10", True, WHITE)
    text_rect = health_text.get_rect(center=(x, y))
    screen.blit(health_text, text_rect)


async def main():
    global screen, player_health, player_velocity, player_x, ammo, score, level, level_timer
    global entering_name, name_submitted, player_name, knockback_timer, player_friction
    global target_speed, target_spawn_rate, game_started

    # Initialize game state
    reset_game()
    game_started = False  # Start with the mission brief
    running = True
    frames = 0
    game_over = False
    last_time = time.time()

    while running:
        if is_web():
            await asyncio.sleep(0)

        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if not game_started:
                    start_button = draw_start_screen()
                    if start_button.collidepoint(mouse_pos):
                        game_started = True
                elif game_over and name_submitted:
                    if replay_rect.collidepoint(event.pos):
                        reset_game()
                        game_started = False  # Go back to mission brief
                        game_over = False
            elif event.type == pygame.KEYDOWN:
                if game_over and entering_name:
                    if event.key == pygame.K_RETURN and player_name:
                        entering_name = False
                        name_submitted = True
                        await save_score(player_name, score, level)
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif len(player_name) < MAX_NAME_LENGTH and event.unicode.isalnum():
                        player_name += event.unicode.upper()
                elif event.key == pygame.K_SPACE and game_started and not game_over:
                    shoot(player_x, player_y)

        # Clear screen and draw stars
        screen.fill(BLACK)
        draw_stars()

        # Handle game states
        if not game_started:
            draw_start_screen()
        elif game_over:
            if not entering_name and not name_submitted:
                entering_name = True
                player_name = ""

            game_over_text = font.render("GAME OVER!", True, RED)
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            level_reached_text = font.render(f"Level Reached: {level}", True, WHITE)

            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 3 - 50))
            screen.blit(final_score_text, (WIDTH // 2 - 100, HEIGHT // 3))
            screen.blit(level_reached_text, (WIDTH // 2 - 100, HEIGHT // 3 + 50))

            if entering_name:
                draw_name_input(screen, player_name)
            elif name_submitted:
                leaderboard_title = font.render("HIGH SCORES", True, YELLOW)
                screen.blit(leaderboard_title, (WIDTH // 2 - 100, HEIGHT // 2 - 40))

                leaderboard = await get_leaderboard(MAX_LEADERBOARD_ENTRIES)
                for i, entry in enumerate(leaderboard):
                    score_text = font.render(
                        f"{i+1}. {entry['player_name']}: {entry['score']} (Level {entry['level']})",
                        True,
                        WHITE,
                    )
                    screen.blit(score_text, (WIDTH // 2 - 150, HEIGHT // 2 + i * 30))

                # Draw replay button
                replay_rect = draw_button(
                    "PLAY AGAIN",
                    WIDTH // 2 - BUTTON_WIDTH // 2,
                    HEIGHT - 100,
                    pygame.mouse.get_pos(),
                )
        else:
            # Game logic
            if player_health <= 0:
                game_over = True
                continue  # Skip to next frame if game is over

            if current_time - level_timer >= level_duration:
                level += 1
                level_timer = current_time
                target_speed = 3 * (speed_increase ** (level - 1))
                target_spawn_rate = max(10, 60 - (level * 5))

            # Update player movement
            if knockback_timer > 0:
                knockback_timer -= 1
                # Keep applying knockback velocity while timer is active
                player_x += player_velocity
                player_x = max(0, min(player_x, WIDTH - player_width))
            else:
                # Normal movement
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    player_velocity -= player_acceleration
                if keys[pygame.K_RIGHT]:
                    player_velocity += player_acceleration

            # Apply physics
            player_velocity *= player_friction
            player_velocity = max(
                min(player_velocity, player_max_speed), -player_max_speed
            )
            player_x += player_velocity
            player_x = max(0, min(player_x, WIDTH - player_width))

            # Spawn objects
            frames += 1
            if frames % target_spawn_rate == 0:
                spawn_target()
            if frames % 300 == 0:
                spawn_care_package()
            if frames % 240 == 0:
                spawn_health_pack()

            # Update and draw game objects
            update_game_objects()
            draw_game_objects()
            draw_hud(current_time)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def update_game_objects():
    global player_health, score, game_over

    # Update bullets
    for bullet in bullets[:]:
        bullet["y"] -= 7
        if bullet["y"] < 0:
            bullets.remove(bullet)

    # Update targets
    for target in targets[:]:
        target["y"] += target_speed
        target["rotation"] = (target["rotation"] + target["spin"]) % 360
        if target["y"] > HEIGHT:
            targets.remove(target)

    # Update care packages
    for package in care_packages[:]:
        package["y"] += 2
        if package["y"] > HEIGHT:
            care_packages.remove(package)

    # Update health packs
    for pack in health_packs[:]:
        pack["y"] += 2.5
        if pack["y"] > HEIGHT:
            health_packs.remove(pack)

    # Collision detection
    check_collisions()

    # Check for game over
    if player_health <= 0:
        game_over = True


def draw_game_objects():
    # Draw player
    draw_player(player_x, player_y)

    # Draw bullets
    for bullet in bullets:
        pygame.draw.circle(
            screen, WHITE, (int(bullet["x"]), int(bullet["y"])), BULLET_RADIUS
        )

    # Draw targets
    for target in targets:
        draw_asteroid(
            screen,
            int(target["x"]),
            int(target["y"]),
            TARGET_RADIUS,
            target["rotation"],
        )

    # Draw care packages
    for package in care_packages:
        draw_crate(screen, package["x"], package["y"])

    # Draw health packs
    for pack in health_packs:
        draw_heart(screen, pack["x"], pack["y"])

    # Draw explosions
    for explosion in explosions[:]:
        radius = (explosion["size"] * explosion["frame"]) // 20
        alpha = 255 * (1 - explosion["frame"] / 20)
        explosion_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            explosion_surface, (*YELLOW, alpha), (radius, radius), radius
        )
        screen.blit(
            explosion_surface, (explosion["x"] - radius, explosion["y"] - radius)
        )
        explosion["frame"] += 1
        if explosion["frame"] >= 20:
            explosions.remove(explosion)

    # Draw floating texts
    for text in floating_texts[:]:
        text_surface = font.render(text["text"], True, text["color"])
        text_rect = text_surface.get_rect(
            center=(text["x"], text["y"] - text["frame"] * FLOAT_SPEED)
        )
        screen.blit(text_surface, text_rect)
        text["frame"] += 1
        if text["frame"] >= FLOAT_DURATION:
            floating_texts.remove(text)


def draw_hud(current_time):
    # Draw HUD elements
    score_text = font.render(f"Score: {score}", True, WHITE)
    health_text = font.render(f"Health: {player_health}", True, WHITE)
    ammo_text = font.render(f"Ammo: {ammo}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    time_left = level_duration - (current_time - level_timer)
    timer_text = font.render(f"Next Level: {int(time_left)}s", True, WHITE)

    # Left-aligned HUD elements
    screen.blit(score_text, (10, 10))  # Moved back to original position
    screen.blit(health_text, (10, 50))
    screen.blit(ammo_text, (10, 90))

    # Right-aligned HUD elements
    level_x = WIDTH - level_text.get_width() - 10
    timer_x = WIDTH - timer_text.get_width() - 10
    screen.blit(level_text, (level_x, 10))
    screen.blit(timer_text, (timer_x, 50))


def check_collisions():
    global player_health, ammo, score, game_over, player_velocity, knockback_timer

    player_center_x = player_x + player_width // 2
    player_center_y = player_y + player_height // 2

    # Bullet collisions with targets, ammo crates, and health packs
    for bullet in bullets[:]:
        # Check bullet collision with targets
        for target in targets[:]:
            distance = math.sqrt(
                (bullet["x"] - target["x"]) ** 2 + (bullet["y"] - target["y"]) ** 2
            )
            if distance < TARGET_RADIUS + BULLET_RADIUS:
                if bullet in bullets:
                    bullets.remove(bullet)
                if target in targets:
                    targets.remove(target)
                    create_explosion(target["x"], target["y"])
                    score += 10
                    break

        # Check bullet collision with care packages
        for package in care_packages[:]:
            if (
                abs(bullet["x"] - package["x"]) < CARE_PACKAGE_SIZE // 2
                and abs(bullet["y"] - package["y"]) < CARE_PACKAGE_SIZE // 2
            ):
                if bullet in bullets:
                    bullets.remove(bullet)
                if package in care_packages:
                    care_packages.remove(package)
                    create_explosion(package["x"], package["y"])
                    ammo += 5
                    create_floating_text("+5", package["x"], package["y"], GREEN)
                    break

        # Check bullet collision with health packs
        for pack in health_packs[:]:
            if (
                abs(bullet["x"] - pack["x"]) < HEALTH_PACK_SIZE * 2
                and abs(bullet["y"] - pack["y"]) < HEALTH_PACK_SIZE * 2
            ):
                if bullet in bullets:
                    bullets.remove(bullet)
                if pack in health_packs:
                    health_packs.remove(pack)
                    create_explosion(pack["x"], pack["y"])
                    player_health = min(100, player_health + HEALTH_BONUS)
                    create_floating_text("+10", pack["x"], pack["y"], BLUE)
                    break

    # Player collisions with targets
    for target in targets[:]:
        distance = math.sqrt(
            (player_center_x - target["x"]) ** 2 + (player_center_y - target["y"]) ** 2
        )
        if distance < 45:
            # Apply damage and check for game over
            player_health = max(0, player_health - 10)  # Prevent negative health
            if player_health <= 0:
                game_over = True
                return  # Exit immediately if game is over

            # Calculate knockback direction and apply force
            impact_direction = -1 if target["x"] > player_center_x else 1
            player_velocity = PLAYER_KNOCKBACK_FORCE * impact_direction
            knockback_timer = KNOCKBACK_DURATION
            targets.remove(target)
            create_explosion(target["x"], target["y"], PLAYER_HIT_EXPLOSION_SIZE)

    # Collision with care packages (only if not shot)
    for package in care_packages[:]:
        if (
            player_x < package["x"] + 30
            and player_x + player_width > package["x"] - 30
            and player_y < package["y"] + 30
            and player_y + player_height > package["y"] - 30
        ):
            ammo += 5
            create_floating_text("+5", package["x"], package["y"], GREEN)
            care_packages.remove(package)
            # if powerup_sound:
            #   powerup_sound.play()

    # Collision with health packs (only if not shot)
    for pack in health_packs[:]:
        if (
            player_x < pack["x"] + HEALTH_PACK_SIZE
            and player_x + player_width > pack["x"] - HEALTH_PACK_SIZE
            and player_y < pack["y"] + HEALTH_PACK_SIZE
            and player_y + player_height > pack["y"] - HEALTH_PACK_SIZE
        ):
            player_health = min(100, player_health + HEALTH_BONUS)
            create_floating_text("+10", pack["x"], pack["y"], BLUE)
            health_packs.remove(pack)
            # if powerup_sound:
            #    powerup_sound.play()


# Entry point
if __name__ == "__main__":
    asyncio.run(main())
else:
    # Web platform
    asyncio.create_task(main())
