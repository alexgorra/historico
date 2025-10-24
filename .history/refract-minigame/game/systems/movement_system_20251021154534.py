"""
Movement and transform components.
"""
import math
from game_constants import WORLD_WIDTH, WORLD_HEIGHT, PLAYER_VISUAL_SIZE
from core.component_system import Component


class TransformComponent(Component):
    """Component for position and transform data."""
    
    def __init__(self, x=0, y=0):
        """
        Initialize transform component.
        
        Args:
            x: Initial X position
            y: Initial Y position
        """
        super().__init__()
        self.x = x
        self.y = y
        self.last_x = x
        self.last_y = y
    
    def update(self, dt):
        """Update transform (store last position for interpolation)."""
        super().update(dt)
        self.last_x = self.owner.x if self.owner else self.x
        self.last_y = self.owner.y if self.owner else self.y
        if self.owner:
            self.x = self.owner.x
            self.y = self.owner.y


class MovementComponent(Component):
    """Component for movement logic."""
    
    def __init__(self, speed=5):
        """
        Initialize movement component.
        
        Args:
            speed: Movement speed in pixels per frame
        """
        super().__init__()
        self.speed = speed
        self.velocity_x = 0
        self.velocity_y = 0
        self.normalize_diagonal = True
    
    def set_velocity(self, vx, vy):
        """
        Set movement velocity.
        
        Args:
            vx: Velocity in X direction (-1, 0, 1)
            vy: Velocity in Y direction (-1, 0, 1)
        """
        self.velocity_x = vx
        self.velocity_y = vy
    
    def update(self, dt):
        """Update position based on velocity."""
        super().update(dt)
        
        if not self.owner:
            return
        
        # Apply diagonal normalization if needed
        move_x = self.velocity_x
        move_y = self.velocity_y
        
        if self.normalize_diagonal and move_x != 0 and move_y != 0:
            # Normalize diagonal movement to prevent faster speed
            diagonal_factor = math.sqrt(2) / 2
            move_x *= diagonal_factor
            move_y *= diagonal_factor
        
        # Calculate new position
        new_x = self.owner.x + move_x * self.speed
        new_y = self.owner.y + move_y * self.speed
        
        # Clamp to world bounds
        new_x = max(0, min(WORLD_WIDTH - PLAYER_SIZE, new_x))
        new_y = max(0, min(WORLD_HEIGHT - PLAYER_SIZE, new_y))
        
        # Update owner position
        self.owner.x = new_x
        self.owner.y = new_y
    
    def stop(self):
        """Stop all movement."""
        self.velocity_x = 0
        self.velocity_y = 0
