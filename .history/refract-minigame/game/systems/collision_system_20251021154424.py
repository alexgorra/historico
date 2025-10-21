"""
Collision detection component.
"""
import pygame
from game_constants import PLAYER_SIZE, PROJECTILE_SIZE
from core.component_system import Component


class CollisionComponent(Component):
    """Component for collision detection."""
    
    def __init__(self, width=PLAYER_SIZE, height=PLAYER_SIZE):
        """
        Initialize collision component.
        
        Args:
            width: Collision box width
            height: Collision box height
        """
        super().__init__()
        self.width = width
        self.height = height
        self.collision_tags = set()  # Tags of objects this can collide with
    
    def get_rect(self):
        """Get the collision rectangle."""
        if not self.owner:
            return None
        return pygame.Rect(self.owner.x, self.owner.y, self.width, self.height)
    
    def check_collision(self, other):
        """
        Check collision with another object.
        
        Args:
            other: Another GameObject with CollisionComponent
            
        Returns:
            True if collision detected
        """
        if not self.owner or not other:
            return False
        
        other_collision = other.get_component(CollisionComponent)
        if not other_collision:
            return False
        
        my_rect = self.get_rect()
        other_rect = other_collision.get_rect()
        
        if not my_rect or not other_rect:
            return False
        
        return my_rect.colliderect(other_rect)
    
    def add_collision_tag(self, tag):
        """Add a tag for collision filtering."""
        self.collision_tags.add(tag)
    
    def can_collide_with(self, other):
        """Check if this object can collide with another based on tags."""
        if not other:
            return False
        
        # If no collision tags set, collide with everything
        if not self.collision_tags:
            return True
        
        # Check if other has any matching tags
        return any(other.has_tag(tag) for tag in self.collision_tags)
