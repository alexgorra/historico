from core.game_object import GameObject
from core.component_system import Component
from animation_system import AsepriteAnimation
import pygame
import os


class CollisionEffectRenderer(Component):
    def __init__(self, size=48):
        super().__init__()
        self.size = size
        self.animation = None
        self._load_animation()
    
    def _load_animation(self):
        try:
            assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'entities')
            json_path = os.path.join(assets_path, 'colision.json')
            png_path = os.path.join(assets_path, 'colision.png')
            
            if os.path.exists(json_path) and os.path.exists(png_path):
                self.animation = AsepriteAnimation(json_path, png_path)
                self.animation.play(loop=False)
        except Exception as e:
            print(f"Error loading collision effect: {e}")
    
    def update(self, dt):
        super().update(dt)
        
        if self.animation:
            self.animation.update(dt)
            if not self.animation.playing:
                if self.owner:
                    self.owner.active = False
    
    def render(self, surface, camera_x, camera_y):
        if not self.owner or not self.animation:
            return
        
        screen_x = int(self.owner.x - camera_x)
        screen_y = int(self.owner.y - camera_y)
        
        current_frame = self.animation.get_current_frame()
        if current_frame:
            frame_width, frame_height = self.animation.get_frame_size()
            scale_factor = self.size / max(frame_width, frame_height)
            scaled_width = int(frame_width * scale_factor)
            scaled_height = int(frame_height * scale_factor)
            
            scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
            frame_rect = scaled_frame.get_rect(center=(screen_x, screen_y))
            surface.blit(scaled_frame, frame_rect)


class CollisionEffect(GameObject):
    def __init__(self, x, y, size=48):
        super().__init__(x, y)
        self.add_tag('effect')
        renderer = CollisionEffectRenderer(size)
        self.add_component(CollisionEffectRenderer, renderer)
