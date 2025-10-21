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
        
        self._load_projectile_animation()
    
    def _load_projectile_animation(self):
        try:
            from animation_system import AsepriteAnimation
            
            assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets')
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
        
        import pygame
        import math
        
        screen_x = int(self.owner.x - camera_x)
        screen_y = int(self.owner.y - camera_y)
        
        if self.projectile_animation:
            current_frame = self.projectile_animation.get_current_frame()
            if current_frame:
                frame_width, frame_height = self.projectile_animation.get_frame_size()
                
                scale_factor = self.visual_size / max(frame_width, frame_height)
                scaled_width = int(frame_width * scale_factor)
                scaled_height = int(frame_height * scale_factor)
                
                scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
                
                angle = math.degrees(math.atan2(-self.direction_y, self.direction_x))
                rotated_frame = pygame.transform.rotate(scaled_frame, angle)
                rotated_rect = rotated_frame.get_rect(center=(screen_x, screen_y))
                
                surface.blit(rotated_frame, rotated_rect)
                return
        
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), self.size // 2)


class Projectile(GameObject):
    """Projectile entity."""
    
    def __init__(self, projectile_id, x, y, direction_x, direction_y, owner_id):
        """
        Initialize a projectile.
        
        Args:
            projectile_id: Unique projectile identifier
            x: Initial X position (center)
            y: Initial Y position (center)
            direction_x: Normalized X direction
            direction_y: Normalized Y direction
            owner_id: ID of the player who shot this projectile
        """
        super().__init__(x, y)
        
        self.projectile_id = projectile_id
        self.owner_id = owner_id
        
        # Add projectile tag
        self.add_tag('projectile')
        
        # Add movement component
        movement = ProjectileMovementComponent(direction_x, direction_y)
        self.add_component(ProjectileMovementComponent, movement)
        
        # Add collision component
        # Projectile is rendered as a circle with radius PROJECTILE_SIZE//2 centered at (x,y)
        # Use an AABB that matches the circle's bounding box
        collision = CollisionComponent(
            width=PROJECTILE_SIZE,
            height=PROJECTILE_SIZE,
            offset_x=-(PROJECTILE_SIZE // 2),
            offset_y=-(PROJECTILE_SIZE // 2),
        )
        collision.add_collision_tag('player')
        self.add_component(CollisionComponent, collision)
        
        # Add renderer component
        renderer = ProjectileRendererComponent(direction_x, direction_y)
        self.add_component(ProjectileRendererComponent, renderer)
