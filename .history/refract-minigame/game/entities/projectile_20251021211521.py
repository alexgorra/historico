"""
Projectile entity class.
"""
from game_constants import PROJECTILE_SPEED, PROJECTILE_SIZE, PROJECTILE_LIFETIME, get_world_bounds
from core.game_object import GameObject
from core.component_system import Component
from systems.collision_system import CollisionComponent
import pygame
import math
import os


class ProjectileMovementComponent(Component):
    def __init__(self, direction_x, direction_y, speed=PROJECTILE_SPEED, lifetime=PROJECTILE_LIFETIME):
        super().__init__()
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.speed = speed
        self.lifetime_frames = 0
        self.max_lifetime = lifetime
    
    def update(self, dt):
        super().update(dt)
        
        if not self.owner:
            return
        
        self.owner.x += self.direction_x * self.speed
        self.owner.y += self.direction_y * self.speed
        
        min_x, min_y, max_x, max_y = get_world_bounds()
        if (self.owner.x < min_x or self.owner.x > max_x or 
            self.owner.y < min_y or self.owner.y > max_y):
            self.owner.active = False
        
        self.lifetime_frames += 1
        if self.lifetime_frames > self.max_lifetime:
            self.owner.active = False


class ProjectileRendererComponent(Component):
    def __init__(self, direction_x=1, direction_y=0, size=PROJECTILE_SIZE, animation_name='f1_projectile'):
        super().__init__()
        self.size = size
        self.direction_x = direction_x
        self.direction_y = direction_y
        from game_constants import PROJECTILE_COLOR, PROJECTILE_VISUAL_SIZE
        self.color = PROJECTILE_COLOR
        self.visual_size = PROJECTILE_VISUAL_SIZE
        self.animation_name = animation_name
        self.projectile_animation = None
        self.cached_rotated_frame = None
        self.last_angle = None
        self.last_frame = None
        self.trail_positions = []
        self.max_trail_length = 5
        
        self._load_projectile_animation()
    
    def _load_projectile_animation(self):
        try:
            from animation_system import AsepriteAnimation
            
            assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'entities')
            proj_json = os.path.join(assets_path, f'{self.animation_name}.json')
            proj_png = os.path.join(assets_path, f'{self.animation_name}.png')
            
            if os.path.exists(proj_json) and os.path.exists(proj_png):
                self.projectile_animation = AsepriteAnimation(proj_json, proj_png)
                self.projectile_animation.play(loop=True)
        except Exception as e:
            print(f"Error loading projectile animation: {e}")
    
    def update(self, dt):
        super().update(dt)
        
        if self.projectile_animation:
            self.projectile_animation.update(dt)
    
    
    def render(self, surface, camera_x, camera_y):
        if not self.owner:
            return
        
        screen_x = int(self.owner.x - camera_x)
        screen_y = int(self.owner.y - camera_y)
        
        if self.projectile_animation:
            current_frame = self.projectile_animation.get_current_frame()
            if current_frame:
                angle = math.degrees(math.atan2(-self.direction_y, self.direction_x))
                
                if (self.cached_rotated_frame is None or 
                    self.last_angle != angle or 
                    self.last_frame != self.projectile_animation.current_frame):
                    
                    frame_width, frame_height = self.projectile_animation.get_frame_size()
                    
                    scale_factor = self.visual_size / max(frame_width, frame_height)
                    scaled_width = int(frame_width * scale_factor)
                    scaled_height = int(frame_height * scale_factor)
                    
                    scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
                    self.cached_rotated_frame = pygame.transform.rotate(scaled_frame, angle)
                    self.last_angle = angle
                    self.last_frame = self.projectile_animation.current_frame
                
                rotated_rect = self.cached_rotated_frame.get_rect(center=(screen_x, screen_y))
                surface.blit(self.cached_rotated_frame, rotated_rect)
                return
        
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), self.size // 2)


class Projectile(GameObject):
    def __init__(self, projectile_id, x, y, direction_x, direction_y, owner_id, 
                 speed=PROJECTILE_SPEED, size=PROJECTILE_SIZE, animation_name='f1_projectile'):
        super().__init__(x, y)
        
        self.projectile_id = projectile_id
        self.owner_id = owner_id
        
        self.add_tag('projectile')
        
        movement = ProjectileMovementComponent(direction_x, direction_y, speed)
        self.add_component(ProjectileMovementComponent, movement)
        
        collision = CollisionComponent(
            width=size,
            height=size,
            offset_x=-(size // 2),
            offset_y=-(size // 2),
        )
        collision.add_collision_tag('player')
        self.add_component(CollisionComponent, collision)
        
        renderer = ProjectileRendererComponent(direction_x, direction_y, size, animation_name)
        self.add_component(ProjectileRendererComponent, renderer)
