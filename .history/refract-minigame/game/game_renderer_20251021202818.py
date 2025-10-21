"""
Game renderer module for handling all drawing and display logic.
"""

import pygame
from game_constants import *
from map_system import MapRenderer


class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.status_font = pygame.font.Font(None, 36)
        
        self.camera_x = 0
        self.camera_y = 0
        
        self.target_camera_x = 0
        self.target_camera_y = 0
        
        self.map_renderer = MapRenderer()
    
    def update_camera(self, player_x, player_y):
        """Update camera to follow player with smooth scrolling."""
        # Calculate target camera position (center player on screen)
        self.target_camera_x = player_x - WIDTH // 2 + PLAYER_VISUAL_SIZE // 2
        self.target_camera_y = player_y - HEIGHT // 2 + PLAYER_VISUAL_SIZE // 2
        
        # Clamp camera to world bounds
        self.target_camera_x = max(0, min(self.target_camera_x, WORLD_WIDTH - WIDTH))
        self.target_camera_y = max(0, min(self.target_camera_y, WORLD_HEIGHT - HEIGHT))
        
        # Smooth camera movement
        self.camera_x += (self.target_camera_x - self.camera_x) * CAMERA_SMOOTHING
        self.camera_y += (self.target_camera_y - self.camera_y) * CAMERA_SMOOTHING
    
    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates."""
        return (world_x - self.camera_x, world_y - self.camera_y)
    
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates."""
        return (screen_x + self.camera_x, screen_y + self.camera_y)
    
    def _draw_world_borders(self):
        """Draw world map (floor and walls)."""
        self.map_renderer.render(self.screen, self.camera_x, self.camera_y)
    
    def _draw_connection_status(self, connected, player_count):
        """Draw connection status and player count."""
        status_text = f"Connected: {connected} | Players: {player_count}"
        status_surface = self.status_font.render(status_text, True, WHITE)
        self.screen.blit(status_surface, (10, 10))
    
    def draw_disconnect_screen(self):
        """Draw a screen when disconnected."""
        self.screen.fill(BLACK)
        
        # Draw disconnected message
        disconnect_text = self.status_font.render("Disconnected from server", True, WHITE)
        text_rect = disconnect_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(disconnect_text, text_rect)
        
        # Draw instructions
        instruction_text = self.font.render("Press ESC to quit", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        self.screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
