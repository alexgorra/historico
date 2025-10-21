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
        super().update(dt)
        
        if not self.owner:
            return
        
        self.time_elapsed += dt / 1000.0
        
        movement = self.owner.get_component(MovementComponent)
        if not movement:
            return
        
        keys = pygame.key.get_pressed()
        
        move_x = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        move_y = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        
        movement.set_velocity(move_x, move_y)
    
    def check_shooting(self, renderer=None):
        if self.time_elapsed - self.last_shot_time < self.shot_cooldown:
            return False, 0, 0, 0, 0
        
        mouse_buttons = pygame.mouse.get_pressed()
        
        if mouse_buttons[0]:
            import math
            from game_constants import PLAYER_VISUAL_SIZE
            
            mouse_screen_x, mouse_screen_y = pygame.mouse.get_pos()
            
            if renderer:
                mouse_x, mouse_y = renderer.screen_to_world(mouse_screen_x, mouse_screen_y)
            else:
                mouse_x, mouse_y = mouse_screen_x, mouse_screen_y
            
            player_center_x = self.owner.x + PLAYER_VISUAL_SIZE // 2
            player_center_y = self.owner.y + PLAYER_VISUAL_SIZE // 2
            
            dx = mouse_x - player_center_x
            dy = mouse_y - player_center_y
            
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                self.last_shot_time = self.time_elapsed
                return True, mouse_x, mouse_y, dx / distance, dy / distance
        
        return False, 0, 0, 0, 0
    
    def is_movement_key_pressed(self):
        """Check if any movement key is pressed."""
        keys = pygame.key.get_pressed()
        return any(keys[k] for k in [
            pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
            pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s
        ])
