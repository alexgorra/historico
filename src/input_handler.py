"""
Input handler module for processing player input and movement.
"""

import pygame
import math
from game_constants import *


class InputHandler:
    def __init__(self):
        self.keys_pressed = set()
        self.last_shot_time = 0
        self.shot_cooldown = 15  # frames between shots (4 shots per second at 60 FPS)
        
    def handle_input(self, current_x, current_y, other_players):
        """
        Handle keyboard input and return new position.
        Returns (new_x, new_y, moved) where moved indicates if position changed.
        """
        keys = pygame.key.get_pressed()
        
        new_x, new_y = current_x, current_y
        
        # Handle movement keys
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y += PLAYER_SPEED
        
        # Keep player within bounds
        new_x = max(0, min(WIDTH - PLAYER_SIZE, new_x))
        new_y = max(0, min(HEIGHT - PLAYER_SIZE, new_y))
        
        # Check collision with other players
        if self._check_collision(new_x, new_y, other_players):
            # If collision detected, don't move
            return current_x, current_y, False
        
        # Check if position changed
        moved = (new_x != current_x or new_y != current_y)
        
        return new_x, new_y, moved
    
    def _check_collision(self, x, y, other_players):
        """
        Check if the player would collide with any other player at position (x, y).
        Returns True if collision detected.
        """
        from game_constants import PLAYER_WIDTH, PLAYER_HEIGHT
        # Create rectangle for current player
        player_rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)

        # Check collision with all other players
        for pid, player_data in other_players.items():
            other_rect = pygame.Rect(player_data['x'], player_data['y'], PLAYER_WIDTH, PLAYER_HEIGHT)
            if player_rect.colliderect(other_rect):
                return True
        
        return False
    
    def check_quit_input(self, event):
        """Check if user wants to quit the game."""
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True
        return False
    
    def get_pressed_keys(self):
        """Get currently pressed keys."""
        return pygame.key.get_pressed()
    
    def check_shooting(self, player_x, player_y, current_frame):
        """
        Check for mouse clicks and return shooting information.
        Returns (should_shoot, target_x, target_y, direction_x, direction_y)
        """
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Check if enough time has passed since last shot
        if current_frame - self.last_shot_time < self.shot_cooldown:
            return False, 0, 0, 0, 0
        
        if mouse_buttons[0]:  # Left mouse button
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Calculate player center
            player_center_x = player_x + PLAYER_SIZE // 2
            player_center_y = player_y + PLAYER_SIZE // 2
            
            # Calculate direction from player to mouse
            dx = mouse_x - player_center_x
            dy = mouse_y - player_center_y
            
            # Normalize direction
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                direction_x = dx / distance
                direction_y = dy / distance
                
                self.last_shot_time = current_frame
                return True, mouse_x, mouse_y, direction_x, direction_y
        
        return False, 0, 0, 0, 0
    
    def is_movement_key_pressed(self):
        """Check if any movement key is currently pressed."""
        keys = pygame.key.get_pressed()
        movement_keys = [
            pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
            pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s
        ]
        return any(keys[key] for key in movement_keys)