"""
Rendering and animation components.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pygame
from game_constants import PLAYER_SIZE, COLORS
from game.core.component_system import Component


class RendererComponent(Component):
    """Component for rendering game objects."""
    
    def __init__(self, color=None, size=PLAYER_SIZE):
        """
        Initialize renderer component.
        
        Args:
            color: Color tuple (r, g, b) or color name string
            size: Size of the rendered object
        """
        super().__init__()
        
        if isinstance(color, str) and color in COLORS:
            self.color = COLORS[color]
        elif isinstance(color, tuple):
            self.color = color
        else:
            self.color = (255, 255, 255)  # White default
        
        self.size = size
        self.visible = True
    
    def render(self, surface, camera_x, camera_y):
        """
        Render the object to the surface.
        
        Args:
            surface: Pygame surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        if not self.visible or not self.owner:
            return
        
        # Calculate screen position
        screen_x = self.owner.x - camera_x
        screen_y = self.owner.y - camera_y
        
        # Draw simple colored square
        pygame.draw.rect(surface, self.color, 
                        (screen_x, screen_y, self.size, self.size))


class AnimationComponent(Component):
    """Component for animated sprites using the animation system."""
    
    def __init__(self, player_id, animation_manager):
        """
        Initialize animation component.
        
        Args:
            player_id: Unique player ID
            animation_manager: AnimationManager instance
        """
        super().__init__()
        self.player_id = player_id
        self.animation_manager = animation_manager
        self.animator = animation_manager.get_or_create_animator(player_id)
        self.is_local_player = False
        self.last_x = 0
        self.last_y = 0
    
    def update(self, dt):
        """Update animation based on movement."""
        super().update(dt)
        
        if not self.owner:
            return
        
        # If local player, animations are updated via input system
        # If remote player, update based on position changes
        if not self.is_local_player:
            self.animation_manager.update_remote_player(
                self.player_id,
                dt,
                self.owner.x,
                self.owner.y
            )
    
    def update_from_keys(self, dt, keys_pressed):
        """
        Update animation from keyboard input (for local player).
        
        Args:
            dt: Delta time in milliseconds
            keys_pressed: Pygame keys state
        """
        if self.animation_manager:
            self.animation_manager.update_local_player(
                self.player_id,
                dt,
                keys_pressed
            )
    
    def render(self, surface, camera_x, camera_y):
        """
        Render the animated sprite.
        
        Args:
            surface: Pygame surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        if not self.owner or not self.animator:
            return
        
        # Get current frame
        current_frame = self.animator.get_current_frame()
        if not current_frame:
            return
        
        # Calculate screen position
        screen_x = self.owner.x - camera_x
        screen_y = self.owner.y - camera_y
        
        # Apply horizontal flip if needed
        if self.animator.should_flip():
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        # Render the sprite
        surface.blit(current_frame, (screen_x, screen_y))
