"""
Collision detection component.
"""
import pygame
from game_constants import PLAYER_SIZE, PROJECTILE_SIZE
from core.component_system import Component


class CollisionComponent(Component):
    """Component for collision detection."""
    
    def __init__(self, width=PLAYER_SIZE, height=PLAYER_SIZE, offset_x=0, offset_y=0):
        super().__init__()
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.collision_tags = set()
    
    def get_rect(self):
        """Get the collision rectangle."""
        if not self.owner:
            return None
        return pygame.Rect(self.owner.x + self.offset_x, self.owner.y + self.offset_y, self.width, self.height)
    
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
        
        if not self.collision_tags:
            return True
        
        return any(other.has_tag(tag) for tag in self.collision_tags)
    
    def debug_render(self, surface, camera_x, camera_y):
        """Render debug hitbox."""
        if not self.owner:
            return
        
        from game_constants import HITBOX_DEBUG_COLOR, HITBOX_DEBUG_WIDTH
        rect = self.get_rect()
        if rect:
            debug_rect = pygame.Rect(
                rect.x - camera_x,
                rect.y - camera_y,
                rect.width,
                rect.height
            )
            pygame.draw.rect(surface, HITBOX_DEBUG_COLOR, debug_rect, HITBOX_DEBUG_WIDTH)
