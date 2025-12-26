"""
Particle system for visual effects (explosions, trails, sparks, etc.)
"""

import pygame
import random
import math


class Particle:
    """
    Individual particle with position, velocity, lifetime, and visual properties.
    """
    
    def __init__(self, x, y, vx=0, vy=0, lifetime=60, color=(255, 255, 255), 
                 size=5, gravity=0, fade=True, shrink=True):
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
        self.friction = 0.99
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
    
    def update(self):
        if not self.active:
            return
        
        # Apply physics
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= self.friction
        self.vy *= self.friction
        self.rotation += self.rotation_speed
        
        # Update lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
            return
        
        # Calculate progress (0 = just spawned, 1 = about to die)
        progress = 1 - (self.lifetime / self.max_lifetime)
        
        # Shrink over time
        if self.shrink:
            self.size = self.initial_size * (1 - progress)
    
    def get_alpha(self):
        """Get current alpha based on lifetime"""
        if not self.fade:
            return 255
        progress = 1 - (self.lifetime / self.max_lifetime)
        return int(255 * (1 - progress))
    
    def draw(self, surface, camera=None):
        if not self.active or self.size < 1:
            return
        
        # Get screen position
        if camera:
            draw_x, draw_y = camera.apply_point(self.x, self.y)
        else:
            draw_x, draw_y = int(self.x), int(self.y)
        
        alpha = self.get_alpha()
        
        # Draw with alpha
        if alpha < 255:
            # Create a surface for alpha blending
            size = max(1, int(self.size * 2))
            particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            color_with_alpha = (*self.color[:3], alpha)
            pygame.draw.circle(particle_surface, color_with_alpha, 
                             (size // 2, size // 2), max(1, int(self.size)))
            surface.blit(particle_surface, (draw_x - size // 2, draw_y - size // 2))
        else:
            pygame.draw.circle(surface, self.color, (draw_x, draw_y), max(1, int(self.size)))
    
    def reset(self, x, y, vx, vy, lifetime, color, size):
        """Reset particle for object pooling"""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
        self.initial_size = size
        self.active = True


class ParticleEmitter:
    """
    Spawns particles with configurable properties.
    """
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.particles = []
        self.active = True
        
        # Emission properties
        self.emit_rate = 5  # Particles per frame
        self.emit_timer = 0
        self.continuous = False
        
        # Particle properties (ranges)
        self.lifetime_range = (30, 60)
        self.speed_range = (2, 5)
        self.angle_range = (0, 360)  # Degrees
        self.size_range = (3, 6)
        self.colors = [(255, 200, 50), (255, 100, 50), (255, 50, 50)]
        self.gravity = 0.1
        self.fade = True
        self.shrink = True
    
    def set_position(self, x, y):
        self.x = x
        self.y = y
    
    def emit(self, count=None):
        """Emit particles"""
        count = count or self.emit_rate
        
        for _ in range(count):
            # Random properties within ranges
            angle = math.radians(random.uniform(*self.angle_range))
            speed = random.uniform(*self.speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            lifetime = random.randint(*self.lifetime_range)
            size = random.uniform(*self.size_range)
            color = random.choice(self.colors)
            
            particle = Particle(
                self.x, self.y, vx, vy, lifetime, color, size,
                self.gravity, self.fade, self.shrink
            )
            self.particles.append(particle)
    
    def burst(self, count=20, speed_multiplier=1.0):
        """Emit a burst of particles in all directions"""
        old_angle_range = self.angle_range
        old_speed_range = self.speed_range
        
        self.angle_range = (0, 360)
        self.speed_range = (self.speed_range[0] * speed_multiplier, 
                           self.speed_range[1] * speed_multiplier)
        
        self.emit(count)
        
        self.angle_range = old_angle_range
        self.speed_range = old_speed_range
    
    def update(self):
        # Continuous emission
        if self.continuous and self.active:
            self.emit_timer += 1
            if self.emit_timer >= 60 / self.emit_rate:
                self.emit(1)
                self.emit_timer = 0
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.active:
                self.particles.remove(particle)
    
    def draw(self, surface, camera=None):
        for particle in self.particles:
            particle.draw(surface, camera)
    
    def clear(self):
        self.particles.clear()
    
    @property
    def particle_count(self):
        return len(self.particles)


class ParticleSystem:
    """
    Manages multiple particle emitters with presets for common effects.
    """
    
    def __init__(self):
        self.emitters = []
    
    def create_explosion(self, x, y, color=(255, 200, 50), count=30, size=8, speed=6):
        """Create an explosion effect"""
        emitter = ParticleEmitter(x, y)
        emitter.colors = [
            color,
            (min(255, color[0] + 50), max(0, color[1] - 50), max(0, color[2] - 50)),
            (max(0, color[0] - 100), max(0, color[1] - 100), max(0, color[2] - 100))
        ]
        emitter.size_range = (size * 0.5, size)
        emitter.speed_range = (speed * 0.5, speed)
        emitter.lifetime_range = (20, 40)
        emitter.gravity = 0.05
        emitter.burst(count)
        self.emitters.append(emitter)
        return emitter
    
    def create_trail(self, x, y, color=(100, 150, 255), size=4):
        """Create a continuous trail emitter"""
        emitter = ParticleEmitter(x, y)
        emitter.colors = [color]
        emitter.size_range = (size * 0.5, size)
        emitter.speed_range = (0.5, 1.5)
        emitter.lifetime_range = (15, 25)
        emitter.emit_rate = 10
        emitter.continuous = True
        emitter.gravity = 0
        self.emitters.append(emitter)
        return emitter
    
    def create_sparks(self, x, y, direction=None, color=(255, 255, 100)):
        """Create spark particles"""
        emitter = ParticleEmitter(x, y)
        emitter.colors = [color, (255, 200, 50)]
        emitter.size_range = (2, 4)
        emitter.speed_range = (3, 8)
        
        if direction is not None:
            # Spread around a direction
            emitter.angle_range = (direction - 30, direction + 30)
        else:
            emitter.angle_range = (0, 360)
        
        emitter.lifetime_range = (10, 25)
        emitter.gravity = 0.2
        emitter.burst(15)
        self.emitters.append(emitter)
        return emitter
    
    def create_smoke(self, x, y, count=10):
        """Create smoke particles"""
        emitter = ParticleEmitter(x, y)
        emitter.colors = [(100, 100, 100), (80, 80, 80), (60, 60, 60)]
        emitter.size_range = (8, 15)
        emitter.speed_range = (0.5, 2)
        emitter.angle_range = (250, 290)  # Upward
        emitter.lifetime_range = (40, 80)
        emitter.gravity = -0.03  # Rise up
        emitter.emit(count)
        self.emitters.append(emitter)
        return emitter
    
    def create_collect(self, x, y, color=(255, 255, 100)):
        """Create collect/pickup effect"""
        emitter = ParticleEmitter(x, y)
        emitter.colors = [color, (255, 255, 255)]
        emitter.size_range = (3, 6)
        emitter.speed_range = (2, 5)
        emitter.angle_range = (0, 360)
        emitter.lifetime_range = (20, 35)
        emitter.gravity = -0.05  # Float up slightly
        emitter.burst(12)
        self.emitters.append(emitter)
        return emitter
    
    def create_damage(self, x, y, color=(255, 50, 50)):
        """Create damage/hit effect"""
        emitter = ParticleEmitter(x, y)
        emitter.colors = [color, (255, 100, 100), (200, 50, 50)]
        emitter.size_range = (4, 8)
        emitter.speed_range = (4, 8)
        emitter.lifetime_range = (15, 30)
        emitter.gravity = 0.1
        emitter.burst(20)
        self.emitters.append(emitter)
        return emitter
    
    def update(self):
        """Update all emitters and remove inactive ones"""
        for emitter in self.emitters[:]:
            emitter.update()
            # Remove one-shot emitters that are done
            if not emitter.continuous and emitter.particle_count == 0:
                self.emitters.remove(emitter)
    
    def draw(self, surface, camera=None):
        """Draw all particles"""
        for emitter in self.emitters:
            emitter.draw(surface, camera)
    
    def clear(self):
        """Clear all emitters and particles"""
        for emitter in self.emitters:
            emitter.clear()
        self.emitters.clear()
    
    @property
    def total_particles(self):
        return sum(e.particle_count for e in self.emitters)


