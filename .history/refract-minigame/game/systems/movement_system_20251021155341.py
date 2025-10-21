"""
Movement and transform components.
"""
import math
from game_constants import WORLD_WIDTH, WORLD_HEIGHT, PLAYER_VISUAL_SIZE
from core.component_system import Component


class TransformComponent(Component):
    def __init__(self, x=0, y=0):
        super().__init__()
        self.x = x
        self.y = y
        self.last_x = x
        self.last_y = y
    
    def update(self, dt):
        super().update(dt)
        self.last_x = self.owner.x if self.owner else self.x
        self.last_y = self.owner.y if self.owner else self.y
        if self.owner:
            self.x = self.owner.x
            self.y = self.owner.y


class MovementComponent(Component):
    def __init__(self, speed=5, bounds_size=PLAYER_VISUAL_SIZE):
        super().__init__()
        self.speed = speed
        self.velocity_x = 0
        self.velocity_y = 0
        self.bounds_size = bounds_size
        self.normalize_diagonal = True
    
    def set_velocity(self, vx, vy):
        self.velocity_x = vx
        self.velocity_y = vy
    
    def update(self, dt):
        super().update(dt)
        
        if not self.owner or (self.velocity_x == 0 and self.velocity_y == 0):
            return
        
        move_x = self.velocity_x
        move_y = self.velocity_y
        
        if self.normalize_diagonal and move_x != 0 and move_y != 0:
            diagonal_factor = math.sqrt(2) / 2
            move_x *= diagonal_factor
            move_y *= diagonal_factor
        
        new_x = self.owner.x + move_x * self.speed
        new_y = self.owner.y + move_y * self.speed
        
        new_x = max(0, min(WORLD_WIDTH - self.bounds_size, new_x))
        new_y = max(0, min(WORLD_HEIGHT - self.bounds_size, new_y))
        
        self.owner.x = new_x
        self.owner.y = new_y
    
    def stop(self):
        self.velocity_x = 0
        self.velocity_y = 0
