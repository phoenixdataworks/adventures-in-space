"""
Camera system with smooth following, screen shake, and bounds
"""

import math
import random


class ScreenShake:
    """Handles screen shake effects"""
    
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.offset_x = 0
        self.offset_y = 0
        self.decay = 0.9
    
    def trigger(self, intensity=10, duration=10):
        """Start a screen shake effect"""
        self.intensity = intensity
        self.duration = duration
    
    def update(self):
        """Update shake and return offset"""
        if self.duration > 0:
            self.offset_x = random.uniform(-self.intensity, self.intensity)
            self.offset_y = random.uniform(-self.intensity, self.intensity)
            self.intensity *= self.decay
            self.duration -= 1
        else:
            self.offset_x = 0
            self.offset_y = 0
        
        return (self.offset_x, self.offset_y)
    
    @property
    def is_shaking(self):
        return self.duration > 0


class Camera:
    """
    Flexible camera system with smooth following and bounds.
    
    Usage:
        camera = Camera(screen_width, screen_height)
        camera.follow(player, lerp=0.1)  # Smooth follow
        camera.update()
        
        # When drawing:
        screen_pos = camera.apply(entity)
        screen.blit(sprite, screen_pos)
    """
    
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Bounds (None = no bounds)
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None
        
        # Following settings
        self.follow_target = None
        self.follow_lerp = 0.1
        self.follow_offset_x = 0
        self.follow_offset_y = 0
        self.dead_zone_x = 0  # No camera movement within this range
        self.dead_zone_y = 0
        
        # Screen shake
        self.shake = ScreenShake()
        
        # Zoom (1.0 = normal)
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_lerp = 0.1
    
    def set_bounds(self, min_x=None, max_x=None, min_y=None, max_y=None):
        """Set world bounds for the camera"""
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
    
    def follow(self, target, lerp=0.1, offset_x=0, offset_y=0, dead_zone=(0, 0)):
        """
        Set camera to follow a target entity.
        
        Args:
            target: Entity with x, y or world_x, world_y attributes
            lerp: Smoothing factor (0 = no movement, 1 = instant snap)
            offset_x, offset_y: Offset from target center
            dead_zone: (x, y) tuple - no movement within this zone
        """
        self.follow_target = target
        self.follow_lerp = lerp
        self.follow_offset_x = offset_x
        self.follow_offset_y = offset_y
        self.dead_zone_x, self.dead_zone_y = dead_zone
    
    def center_on(self, x, y, instant=False):
        """Center camera on a point"""
        self.target_x = x - self.screen_width // 2
        self.target_y = y - self.screen_height // 2
        
        if instant:
            self.x = self.target_x
            self.y = self.target_y
    
    def update(self, dt=1.0):
        """Update camera position"""
        # Follow target if set
        if self.follow_target:
            # Get target position (support both x/y and world_x/world_y)
            target_x = getattr(self.follow_target, 'world_x', None) or getattr(self.follow_target, 'x', 0)
            target_y = getattr(self.follow_target, 'y', 0)
            
            # Calculate desired camera position (center target on screen)
            desired_x = target_x - self.screen_width // 2 + self.follow_offset_x
            desired_y = target_y - self.screen_height // 2 + self.follow_offset_y
            
            # Apply dead zone
            if abs(desired_x - self.x) > self.dead_zone_x:
                self.target_x = desired_x
            if abs(desired_y - self.y) > self.dead_zone_y:
                self.target_y = desired_y
        
        # Smooth interpolation
        self.x += (self.target_x - self.x) * self.follow_lerp * dt
        self.y += (self.target_y - self.y) * self.follow_lerp * dt
        
        # Apply bounds
        if self.min_x is not None:
            self.x = max(self.min_x, self.x)
        if self.max_x is not None:
            self.x = min(self.max_x - self.screen_width, self.x)
        if self.min_y is not None:
            self.y = max(self.min_y, self.y)
        if self.max_y is not None:
            self.y = min(self.max_y - self.screen_height, self.y)
        
        # Update zoom
        self.zoom += (self.target_zoom - self.zoom) * self.zoom_lerp * dt
        
        # Update screen shake
        self.shake.update()
    
    def apply(self, entity):
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            entity: Object with x, y or world_x attributes
            
        Returns:
            (screen_x, screen_y) tuple
        """
        # Get entity position
        world_x = getattr(entity, 'world_x', None) or getattr(entity, 'x', 0)
        world_y = getattr(entity, 'y', 0)
        
        # Apply camera offset and zoom
        screen_x = (world_x - self.x) * self.zoom + self.shake.offset_x
        screen_y = (world_y - self.y) * self.zoom + self.shake.offset_y
        
        return (int(screen_x), int(screen_y))
    
    def apply_point(self, x, y):
        """Convert a world point to screen coordinates"""
        screen_x = (x - self.x) * self.zoom + self.shake.offset_x
        screen_y = (y - self.y) * self.zoom + self.shake.offset_y
        return (int(screen_x), int(screen_y))
    
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_x - self.shake.offset_x) / self.zoom + self.x
        world_y = (screen_y - self.shake.offset_y) / self.zoom + self.y
        return (world_x, world_y)
    
    def is_visible(self, entity, margin=50):
        """Check if an entity is visible on screen"""
        screen_x, screen_y = self.apply(entity)
        width = getattr(entity, 'width', 0)
        height = getattr(entity, 'height', 0)
        
        return (
            screen_x + width + margin > 0 and
            screen_x - margin < self.screen_width and
            screen_y + height + margin > 0 and
            screen_y - margin < self.screen_height
        )
    
    def trigger_shake(self, intensity=10, duration=10):
        """Trigger a screen shake effect"""
        self.shake.trigger(intensity, duration)
    
    def set_zoom(self, zoom, instant=False):
        """Set camera zoom level"""
        self.target_zoom = zoom
        if instant:
            self.zoom = zoom

