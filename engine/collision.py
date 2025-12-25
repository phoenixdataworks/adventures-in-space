"""
Collision detection utilities with spatial partitioning for performance
"""

import math
from collections import defaultdict


def check_circle_collision(x1, y1, r1, x2, y2, r2):
    """Check if two circles collide"""
    dist_sq = (x1 - x2) ** 2 + (y1 - y2) ** 2
    return dist_sq < (r1 + r2) ** 2


def check_rect_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    """Check if two rectangles collide (AABB)"""
    return (
        x1 < x2 + w2 and
        x1 + w1 > x2 and
        y1 < y2 + h2 and
        y1 + h1 > y2
    )


def check_circle_rect_collision(cx, cy, radius, rx, ry, rw, rh):
    """Check if a circle collides with a rectangle"""
    # Find closest point on rectangle to circle center
    closest_x = max(rx, min(cx, rx + rw))
    closest_y = max(ry, min(cy, ry + rh))
    
    # Calculate distance from closest point to circle center
    dist_sq = (cx - closest_x) ** 2 + (cy - closest_y) ** 2
    
    return dist_sq < radius ** 2


def point_in_circle(px, py, cx, cy, radius):
    """Check if a point is inside a circle"""
    return (px - cx) ** 2 + (py - cy) ** 2 < radius ** 2


def point_in_rect(px, py, rx, ry, rw, rh):
    """Check if a point is inside a rectangle"""
    return rx <= px <= rx + rw and ry <= py <= ry + rh


class SpatialGrid:
    """
    Spatial partitioning grid for efficient collision detection.
    
    Usage:
        grid = SpatialGrid(cell_size=64)
        
        # Each frame:
        grid.clear()
        for entity in entities:
            grid.insert(entity)
        
        # Check collisions:
        for entity in entities:
            nearby = grid.get_nearby(entity.x, entity.y)
            for other in nearby:
                if entity != other and collides(entity, other):
                    handle_collision(entity, other)
    """
    
    def __init__(self, cell_size=64):
        self.cell_size = cell_size
        self.grid = defaultdict(list)
    
    def _get_cell(self, x, y):
        """Get cell coordinates for a position"""
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def clear(self):
        """Clear all entities from the grid"""
        self.grid.clear()
    
    def insert(self, entity):
        """
        Insert an entity into the grid.
        Entity should have x, y attributes (and optionally width, height for large entities).
        """
        x = getattr(entity, 'world_x', None) or getattr(entity, 'x', 0)
        y = getattr(entity, 'y', 0)
        width = getattr(entity, 'width', 0)
        height = getattr(entity, 'height', 0)
        
        # For large entities, insert into multiple cells
        min_cell_x = int(x // self.cell_size)
        max_cell_x = int((x + width) // self.cell_size)
        min_cell_y = int(y // self.cell_size)
        max_cell_y = int((y + height) // self.cell_size)
        
        for cx in range(min_cell_x, max_cell_x + 1):
            for cy in range(min_cell_y, max_cell_y + 1):
                self.grid[(cx, cy)].append(entity)
    
    def get_nearby(self, x, y, radius=1):
        """
        Get all entities near a position.
        
        Args:
            x, y: World position
            radius: Number of cells to check in each direction
            
        Returns:
            List of nearby entities
        """
        cx, cy = self._get_cell(x, y)
        nearby = []
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                cell_entities = self.grid.get((cx + dx, cy + dy), [])
                nearby.extend(cell_entities)
        
        return nearby
    
    def get_in_rect(self, x, y, width, height):
        """Get all entities within a rectangular area"""
        min_cx = int(x // self.cell_size)
        max_cx = int((x + width) // self.cell_size)
        min_cy = int(y // self.cell_size)
        max_cy = int((y + height) // self.cell_size)
        
        entities = []
        seen = set()
        
        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                for entity in self.grid.get((cx, cy), []):
                    entity_id = id(entity)
                    if entity_id not in seen:
                        seen.add(entity_id)
                        entities.append(entity)
        
        return entities


class CollisionResolver:
    """
    Higher-level collision management with layers and callbacks.
    
    Usage:
        resolver = CollisionResolver()
        resolver.add_layer('player')
        resolver.add_layer('enemies')
        resolver.add_layer('bullets')
        
        resolver.add_collision_rule('player', 'enemies', on_player_enemy_collision)
        resolver.add_collision_rule('bullets', 'enemies', on_bullet_enemy_collision)
        
        # Each frame:
        resolver.update(all_entities)
    """
    
    def __init__(self, cell_size=64):
        self.grid = SpatialGrid(cell_size)
        self.layers = defaultdict(list)
        self.collision_rules = []
    
    def add_layer(self, name):
        """Add a collision layer"""
        if name not in self.layers:
            self.layers[name] = []
    
    def add_entity(self, entity, layer):
        """Add an entity to a collision layer"""
        self.layers[layer].append(entity)
    
    def remove_entity(self, entity, layer):
        """Remove an entity from a collision layer"""
        if entity in self.layers[layer]:
            self.layers[layer].remove(entity)
    
    def add_collision_rule(self, layer1, layer2, callback, collision_type='circle'):
        """
        Add a collision rule between two layers.
        
        Args:
            layer1, layer2: Layer names
            callback: Function called with (entity1, entity2) when collision occurs
            collision_type: 'circle', 'rect', or 'circle_rect'
        """
        self.collision_rules.append({
            'layer1': layer1,
            'layer2': layer2,
            'callback': callback,
            'type': collision_type
        })
    
    def clear(self):
        """Clear all entities from all layers"""
        for layer in self.layers.values():
            layer.clear()
    
    def update(self):
        """Check all collision rules and trigger callbacks"""
        # Build spatial grid
        self.grid.clear()
        for layer in self.layers.values():
            for entity in layer:
                self.grid.insert(entity)
        
        # Check each collision rule
        for rule in self.collision_rules:
            layer1_entities = self.layers[rule['layer1']]
            layer2_entities = self.layers[rule['layer2']]
            
            for e1 in layer1_entities:
                x1 = getattr(e1, 'world_x', None) or getattr(e1, 'x', 0)
                y1 = getattr(e1, 'y', 0)
                
                # Get nearby entities from layer2
                nearby = self.grid.get_nearby(x1, y1)
                
                for e2 in nearby:
                    if e2 not in layer2_entities or e1 == e2:
                        continue
                    
                    # Check collision based on type
                    collision = False
                    
                    if rule['type'] == 'circle':
                        r1 = getattr(e1, 'radius', getattr(e1, 'width', 10) / 2)
                        x2 = getattr(e2, 'world_x', None) or getattr(e2, 'x', 0)
                        y2 = getattr(e2, 'y', 0)
                        r2 = getattr(e2, 'radius', getattr(e2, 'width', 10) / 2)
                        collision = check_circle_collision(x1, y1, r1, x2, y2, r2)
                    
                    elif rule['type'] == 'rect':
                        w1 = getattr(e1, 'width', 10)
                        h1 = getattr(e1, 'height', 10)
                        x2 = getattr(e2, 'world_x', None) or getattr(e2, 'x', 0)
                        y2 = getattr(e2, 'y', 0)
                        w2 = getattr(e2, 'width', 10)
                        h2 = getattr(e2, 'height', 10)
                        collision = check_rect_collision(x1, y1, w1, h1, x2, y2, w2, h2)
                    
                    if collision:
                        rule['callback'](e1, e2)

