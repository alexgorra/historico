"""
Health system component for managing entity health and damage.
"""
import pygame
from game_constants import (
    PLAYER_MAX_HP,
    HEALTH_BAR_WIDTH,
    HEALTH_BAR_HEIGHT,
    HEALTH_BAR_OFFSET_Y,
    HEALTH_BAR_BG_COLOR,
    HEALTH_BAR_FILL_COLOR,
    HEALTH_BAR_BORDER_COLOR,
    HEALTH_BAR_BORDER_WIDTH,
    PLAYER_HITBOX_OFFSET_X,
    PLAYER_HITBOX_OFFSET_Y
)
from core.component_system import Component


class HealthComponent(Component):
    """Component for managing entity health."""
    
    def __init__(self, max_hp=PLAYER_MAX_HP):
        """
        Initialize health component.
        
        Args:
            max_hp: Maximum health points
        """
        super().__init__()
        self.max_hp = max_hp
        self.current_hp = max_hp
    
    def take_damage(self, damage):
        """
        Apply damage to this entity.
        
        Args:
            damage: Amount of damage to take
            
        Returns:
            True if entity is still alive, False if dead
        """
        self.current_hp = max(0, self.current_hp - damage)
        return self.current_hp > 0
    
    def heal(self, amount):
        """
        Heal this entity.
        
        Args:
            amount: Amount of health to restore
        """
        self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    def is_alive(self):
        """Check if entity is alive."""
        return self.current_hp > 0
    
    def get_health_percentage(self):
        """Get health as a percentage (0.0 to 1.0)."""
        return self.current_hp / self.max_hp if self.max_hp > 0 else 0
    
    def render_health_bar(self, surface, camera_x, camera_y):
        """
        Render health bar above the entity's hitbox.
        
        Args:
            surface: Pygame surface to draw on
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        if not self.owner:
            return
        
        # Calculate health bar position (above the hitbox)
        bar_x = int(self.owner.x + PLAYER_HITBOX_OFFSET_X - camera_x)
        bar_y = int(self.owner.y + PLAYER_HITBOX_OFFSET_Y + HEALTH_BAR_OFFSET_Y - camera_y)
        
        # Draw background (gray)
        bg_rect = pygame.Rect(bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        pygame.draw.rect(surface, HEALTH_BAR_BG_COLOR, bg_rect)
        
        # Draw health fill (green, scaled by current health percentage)
        health_percentage = self.get_health_percentage()
        fill_width = int(HEALTH_BAR_WIDTH * health_percentage)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, HEALTH_BAR_HEIGHT)
            pygame.draw.rect(surface, HEALTH_BAR_FILL_COLOR, fill_rect)
        
        # Draw border (white)
        pygame.draw.rect(surface, HEALTH_BAR_BORDER_COLOR, bg_rect, HEALTH_BAR_BORDER_WIDTH)
