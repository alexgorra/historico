"""
Input handling component.
"""
import pygame
from game_constants import SHOOT_COOLDOWN
from core.component_system import Component
from systems.movement_system import MovementComponent


class InputComponent(Component):
    """Component for handling player input."""
    
    def __init__(self):
        super().__init__()
        self.last_shot_time = 0.0
        self.shot_cooldown = SHOOT_COOLDOWN
        self.time_elapsed = 0.0
    
    def update(self, dt):
        """Process input and update movement."""
        super().update(dt)
        
        if not self.owner:
            return
        
        # Update time tracking (dt is in milliseconds)
        self.time_elapsed += dt / 1000.0
        
        # Get movement component
        movement = self.owner.get_component(MovementComponent)
        if not movement:
            return
        
        # Handle keyboard input
        keys = pygame.key.get_pressed()
        
        move_x = 0
        move_y = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += 1
        
        # Set velocity on movement component
        movement.set_velocity(move_x, move_y)
    
    def check_shooting(self, renderer=None):
        """
        Check for shooting input.
        
        Args:
            renderer: Renderer for coordinate conversion
            
        Returns:
            Tuple of (should_shoot, target_x, target_y, direction_x, direction_y)
        """
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Check cooldown (time-based)
        if self.time_elapsed - self.last_shot_time < self.shot_cooldown:
            return False, 0, 0, 0, 0
        
        if mouse_buttons[0]:  # Left click
            mouse_screen_x, mouse_screen_y = pygame.mouse.get_pos()
            
            # Convert to world coordinates if renderer available
            if renderer:
                mouse_x, mouse_y = renderer.screen_to_world(mouse_screen_x, mouse_screen_y)
            else:
                mouse_x, mouse_y = mouse_screen_x, mouse_screen_y
            
            # Calculate direction from player to mouse
            from game_constants import PLAYER_VISUAL_SIZE
            import math
            
            player_center_x = self.owner.x + PLAYER_VISUAL_SIZE // 2
            player_center_y = self.owner.y + PLAYER_VISUAL_SIZE // 2
            
            dx = mouse_x - player_center_x
            dy = mouse_y - player_center_y
            
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                direction_x = dx / distance
                direction_y = dy / distance
                
                self.last_shot_time = self.time_elapsed
                return True, mouse_x, mouse_y, direction_x, direction_y
        
        return False, 0, 0, 0, 0
    
    def is_movement_key_pressed(self):
        """Check if any movement key is pressed."""
        keys = pygame.key.get_pressed()
        return any(keys[k] for k in [
            pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
            pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s
        ])
