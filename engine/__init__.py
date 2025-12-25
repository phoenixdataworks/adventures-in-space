"""
Shared Game Engine for Arcade Games
Provides common utilities for camera, collision, state management, particles, and more.
"""

from .camera import Camera, ScreenShake
from .collision import SpatialGrid, check_circle_collision, check_rect_collision, check_circle_rect_collision
from .state_machine import GameState, StateMachine
from .particles import Particle, ParticleEmitter, ParticleSystem
from .object_pool import ObjectPool
from .fonts import Fonts
from .utils import clamp, lerp, angle_between, distance, normalize_angle
from .leaderboard import Leaderboard, get_leaderboard, add_score, get_top_scores, is_high_score

__all__ = [
    # Camera
    'Camera', 'ScreenShake',
    # Collision
    'SpatialGrid', 'check_circle_collision', 'check_rect_collision', 'check_circle_rect_collision',
    # State Machine
    'GameState', 'StateMachine',
    # Particles
    'Particle', 'ParticleEmitter', 'ParticleSystem',
    # Object Pool
    'ObjectPool',
    # Fonts
    'Fonts',
    # Utils
    'clamp', 'lerp', 'angle_between', 'distance', 'normalize_angle',
    # Leaderboard
    'Leaderboard', 'get_leaderboard', 'add_score', 'get_top_scores', 'is_high_score',
]

