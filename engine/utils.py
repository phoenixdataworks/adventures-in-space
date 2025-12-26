"""
Common utility functions for game development.
"""

import math


def clamp(value, min_val, max_val):
    """Clamp a value between min and max"""
    return max(min_val, min(max_val, value))


def lerp(start, end, t):
    """Linear interpolation between start and end"""
    return start + (end - start) * t


def inverse_lerp(start, end, value):
    """Get the interpolation factor for a value between start and end"""
    if end == start:
        return 0
    return (value - start) / (end - start)


def remap(value, in_min, in_max, out_min, out_max):
    """Remap a value from one range to another"""
    t = inverse_lerp(in_min, in_max, value)
    return lerp(out_min, out_max, t)


def distance(x1, y1, x2, y2):
    """Calculate distance between two points"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distance_squared(x1, y1, x2, y2):
    """Calculate squared distance (faster, avoids sqrt)"""
    return (x2 - x1) ** 2 + (y2 - y1) ** 2


def angle_between(x1, y1, x2, y2):
    """Calculate angle from point 1 to point 2 in radians"""
    return math.atan2(y2 - y1, x2 - x1)


def angle_between_degrees(x1, y1, x2, y2):
    """Calculate angle from point 1 to point 2 in degrees"""
    return math.degrees(angle_between(x1, y1, x2, y2))


def normalize_angle(angle):
    """Normalize angle to be between -pi and pi"""
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle


def normalize_angle_degrees(angle):
    """Normalize angle to be between 0 and 360"""
    return angle % 360


def move_towards(current, target, max_delta):
    """Move current towards target by at most max_delta"""
    diff = target - current
    if abs(diff) <= max_delta:
        return target
    return current + math.copysign(max_delta, diff)


def move_towards_angle(current, target, max_delta):
    """Move current angle towards target angle by at most max_delta"""
    diff = normalize_angle(target - current)
    if abs(diff) <= max_delta:
        return target
    return current + math.copysign(max_delta, diff)


def smooth_damp(current, target, current_velocity, smooth_time, max_speed=float('inf'), dt=1/60):
    """
    Gradually changes a value towards a target (Unity-style SmoothDamp).
    
    Returns:
        (new_value, new_velocity) tuple
    """
    smooth_time = max(0.0001, smooth_time)
    omega = 2 / smooth_time
    
    x = omega * dt
    exp = 1 / (1 + x + 0.48 * x * x + 0.235 * x * x * x)
    
    change = current - target
    original_to = target
    
    max_change = max_speed * smooth_time
    change = clamp(change, -max_change, max_change)
    target = current - change
    
    temp = (current_velocity + omega * change) * dt
    new_velocity = (current_velocity - omega * temp) * exp
    output = target + (change + temp) * exp
    
    if (original_to - current > 0) == (output > original_to):
        output = original_to
        new_velocity = (output - original_to) / dt
    
    return output, new_velocity


def point_in_polygon(px, py, polygon):
    """
    Check if a point is inside a polygon using ray casting.
    
    Args:
        px, py: Point coordinates
        polygon: List of (x, y) tuples forming the polygon
        
    Returns:
        True if point is inside polygon
    """
    n = len(polygon)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        
        j = i
    
    return inside


def rotate_point(px, py, cx, cy, angle):
    """
    Rotate a point around a center point.
    
    Args:
        px, py: Point to rotate
        cx, cy: Center of rotation
        angle: Rotation angle in radians
        
    Returns:
        (new_x, new_y) tuple
    """
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Translate point to origin
    px -= cx
    py -= cy
    
    # Rotate
    new_x = px * cos_a - py * sin_a
    new_y = px * sin_a + py * cos_a
    
    # Translate back
    return new_x + cx, new_y + cy


def ease_in_quad(t):
    """Quadratic ease in"""
    return t * t


def ease_out_quad(t):
    """Quadratic ease out"""
    return 1 - (1 - t) * (1 - t)


def ease_in_out_quad(t):
    """Quadratic ease in-out"""
    if t < 0.5:
        return 2 * t * t
    return 1 - pow(-2 * t + 2, 2) / 2


def ease_out_elastic(t):
    """Elastic ease out (bouncy)"""
    c4 = (2 * math.pi) / 3
    
    if t == 0:
        return 0
    if t == 1:
        return 1
    
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def ease_out_bounce(t):
    """Bounce ease out"""
    n1 = 7.5625
    d1 = 2.75
    
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


class Timer:
    """
    Simple timer utility.
    
    Usage:
        timer = Timer(60)  # 60 frames / 1 second at 60fps
        
        # Each frame:
        timer.update()
        if timer.finished:
            do_something()
            timer.reset()
    """
    
    def __init__(self, duration, auto_reset=False):
        self.duration = duration
        self.current = 0
        self.auto_reset = auto_reset
        self.finished = False
        self.on_finish = None  # Callback
    
    def update(self, dt=1):
        if self.finished and not self.auto_reset:
            return
        
        self.current += dt
        
        if self.current >= self.duration:
            self.finished = True
            if self.on_finish:
                self.on_finish()
            if self.auto_reset:
                self.current = 0
                self.finished = False
    
    def reset(self, new_duration=None):
        if new_duration is not None:
            self.duration = new_duration
        self.current = 0
        self.finished = False
    
    @property
    def progress(self):
        """Get progress from 0 to 1"""
        return min(1, self.current / self.duration) if self.duration > 0 else 1
    
    @property
    def remaining(self):
        """Get remaining time"""
        return max(0, self.duration - self.current)


class Cooldown:
    """
    Cooldown timer for abilities, attacks, etc.
    
    Usage:
        shoot_cooldown = Cooldown(30)  # 30 frame cooldown
        
        if shoot_cooldown.ready:
            shoot()
            shoot_cooldown.trigger()
        
        # Each frame:
        shoot_cooldown.update()
    """
    
    def __init__(self, duration):
        self.duration = duration
        self.current = 0
    
    def trigger(self):
        """Start the cooldown"""
        self.current = self.duration
    
    def update(self, dt=1):
        """Update the cooldown"""
        if self.current > 0:
            self.current -= dt
    
    @property
    def ready(self):
        """Check if cooldown is ready"""
        return self.current <= 0
    
    @property
    def progress(self):
        """Get progress from 0 (just triggered) to 1 (ready)"""
        return 1 - (self.current / self.duration) if self.duration > 0 else 1
    
    def reset(self):
        """Reset cooldown to ready state"""
        self.current = 0


