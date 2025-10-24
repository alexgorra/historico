"""
Projectile entity class.
"""
from game_constants import PROJECTILE_SPEED, PROJECTILE_SIZE, PROJECTILE_LIFETIME, get_world_bounds
from core.game_object import GameObject
from core.component_system import Component
from systems.collision_system import CollisionComponent


class ProjectileMovementComponent(Component):
    """Special movement component for projectiles."""
    
    def __init__(self, direction_x, direction_y, speed=PROJECTILE_SPEED):
        """
        Initialize projectile movement.
        
        Args:
            direction_x: Normalized X direction
            direction_y: Normalized Y direction
            speed: Speed in pixels per frame
        """
        super().__init__()
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.speed = speed
        self.lifetime_frames = 0
        self.max_lifetime = PROJECTILE_LIFETIME
    
    def update(self, dt):
        """Update projectile position and check boundaries."""
        super().update(dt)
        
        if not self.owner:
            return
        
        # Update position
        self.owner.x += self.direction_x * self.speed
        self.owner.y += self.direction_y * self.speed
        
        # Check world bounds
        min_x, min_y, max_x, max_y = get_world_bounds()
        if (self.owner.x < min_x or self.owner.x > max_x or 
            self.owner.y < min_y or self.owner.y > max_y):
            self.owner.active = False
        
        # Check lifetime
        self.lifetime_frames += 1
        if self.lifetime_frames > self.max_lifetime:
            self.owner.active = False


class ProjectileRendererComponent(Component):
    """Renders projectiles with animation."""
    
    def __init__(self, direction_x=1, direction_y=0, size=PROJECTILE_SIZE):
        """
        Initialize projectile renderer.
        
        Args:
            direction_x: X direction for rotation
            direction_y: Y direction for rotation
            size: Size of the projectile
        """
        super().__init__()
        self.size = size
        self.direction_x = direction_x
        self.direction_y = direction_y
        from game_constants import PROJECTILE_COLOR, PROJECTILE_VISUAL_SIZE
        self.color = PROJECTILE_COLOR
        self.visual_size = PROJECTILE_VISUAL_SIZE
        self.projectile_animation = None
        
        # Load projectile animation
        self._load_projectile_animation()
    
    def _load_projectile_animation(self):
        """Load the projectile animation from assets."""
        try:
            import os
            from animation_system import AsepriteAnimation
            
            assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets')
            proj_json = os.path.join(assets_path, 'f1_projectile.json')
            proj_png = os.path.join(assets_path, 'f1_projectile.png')
            
            self.projectile_animation = AsepriteAnimation(proj_json, proj_png)
            self.projectile_animation.play(loop=True)
            print("Projectile animation loaded successfully")
        except Exception as e:
            print(f"Error loading projectile animation: {e}")
    
    def update(self, dt):
        """Update projectile animation."""
        super().update(dt)
        
        if self.projectile_animation:
            self.projectile_animation.update(dt)
    
    def render(self, surface, camera_x, camera_y):
        """
        Render the projectile.
        
        Args:
            surface: Pygame surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        if not self.owner:
            return
        
        import pygame
        
        # Calculate screen position (projectile position is center)
        screen_x = int(self.owner.x - camera_x)
        screen_y = int(self.owner.y - camera_y)
        
        # Try to render with animation
        if self.projectile_animation:
            current_frame = self.projectile_animation.get_current_frame()
            if current_frame:
                # Get frame size
                frame_width, frame_height = self.projectile_animation.get_frame_size()
                
                # Scale to projectile visual size
                scale_factor = self.visual_size / max(frame_width, frame_height)
                scaled_width = int(frame_width * scale_factor)
                scaled_height = int(frame_height * scale_factor)
                
                # Scale the frame
                scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
                
                # Calculate rotation angle (sprite default is facing right)
                import math
                angle = math.degrees(math.atan2(-self.direction_y, self.direction_x))
                
                # Rotate the frame
                rotated_frame = pygame.transform.rotate(scaled_frame, angle)
                
                # Center the rotated sprite on the projectile position
                rotated_rect = rotated_frame.get_rect(center=(screen_x, screen_y))
                
                # Render the sprite
                surface.blit(rotated_frame, rotated_rect)
                return
        
        # Fallback: Draw projectile as a circle with proper radius
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
        renderer = ProjectileRendererComponent()
        self.add_component(ProjectileRendererComponent, renderer)
