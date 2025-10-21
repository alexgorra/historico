"""
Rendering and animation components.
"""
import pygame
from game_constants import PLAYER_VISUAL_SIZE, PLAYER_SPRITE_SIZE, COLORS
from core.component_system import Component


class RendererComponent(Component):
    """Component for rendering game objects."""
    
    def __init__(self, color=None, size=PLAYER_VISUAL_SIZE):
        super().__init__()
        
        if isinstance(color, str) and color in COLORS:
            self.color = COLORS[color]
        elif isinstance(color, tuple):
            self.color = color
        else:
            self.color = (255, 255, 255)
        
        self.size = size
        self.visible = True
    
    def render(self, surface, camera_x, camera_y):
        if not self.visible or not self.owner:
            return
        
        screen_x = int(self.owner.x - camera_x)
        screen_y = int(self.owner.y - camera_y)
        
        pygame.draw.rect(surface, self.color, 
                        (screen_x, screen_y, self.size, self.size))


class AnimationComponent(Component):
    """Component for animated sprites using the animation system."""
    
    def __init__(self, player_id, animation_manager):
        super().__init__()
        self.player_id = player_id
        self.animation_manager = animation_manager
        self.animator = animation_manager.get_or_create_animator(player_id)
        self.is_local_player = False
    
    def update(self, dt):
        super().update(dt)
        
        if not self.owner or self.is_local_player:
            return
        
        self.animation_manager.update_remote_player(
            self.player_id,
            dt,
            self.owner.x,
            self.owner.y
        )
    
    def update_from_keys(self, dt, keys_pressed):
        if self.animation_manager:
            self.animation_manager.update_local_player(
                self.player_id,
                dt,
                keys_pressed
            )
    
    def render(self, surface, camera_x, camera_y):
        if not self.owner or not self.animator:
            return
        
        current_frame = self.animator.get_current_frame()
        if not current_frame:
            return
        
        screen_x = int(self.owner.x - camera_x)
        screen_y = int(self.owner.y - camera_y)
        
        # Scale the sprite to PLAYER_SPRITE_SIZE
        frame_width, frame_height = current_frame.get_size()
        scale_factor = PLAYER_SPRITE_SIZE / max(frame_width, frame_height)
        scaled_width = int(frame_width * scale_factor)
        scaled_height = int(frame_height * scale_factor)
        
        scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
        surface.blit(scaled_frame, (screen_x, screen_y))
