"""
Game renderer module for handling all drawing and display logic.
"""

import pygame
from game_constants import *


class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.status_font = pygame.font.Font(None, 36)
        
    def draw_frame(self, player_x, player_y, player_color, player_id, other_players, connected, projectiles=None):
        """Draw a complete game frame."""
        self.screen.fill(BLACK)
        
        # Draw other players
        self._draw_other_players(other_players)
        
        # Draw current player
        self._draw_current_player(player_x, player_y, player_color)
        
        # Draw projectiles
        if projectiles:
            self._draw_projectiles(projectiles)
        
        # Draw UI elements
        self._draw_connection_status(connected, len(other_players) + 1)
        
        pygame.display.flip()
    
    def _draw_other_players(self, other_players):
        """Draw all other players on the screen."""
        for pid, player_data in other_players.items():
            color = COLORS.get(player_data['color'], WHITE)
            pygame.draw.rect(self.screen, color, 
                           (player_data['x'], player_data['y'], PLAYER_SIZE, PLAYER_SIZE))
            
            # Draw player ID above square
            text = self.font.render(pid, True, WHITE)
            self.screen.blit(text, (player_data['x'], player_data['y'] - 20))
    
    def _draw_current_player(self, player_x, player_y, player_color):
        """Draw the current player on the screen."""
        if player_color:
            color = COLORS.get(player_color, WHITE)
            pygame.draw.rect(self.screen, color, 
                           (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))
            
            # Draw "YOU" above current player
            text = self.font.render("YOU", True, WHITE)
            self.screen.blit(text, (player_x, player_y - 20))
    
    def _draw_projectiles(self, projectiles):
        """Draw all projectiles on the screen."""
        for projectile in projectiles.values():
            pygame.draw.circle(self.screen, PROJECTILE_COLOR, 
                             (int(projectile.x), int(projectile.y)), 
                             PROJECTILE_SIZE // 2)
    
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
    
    def draw_connecting_screen(self):
        """Draw a screen while connecting to server."""
        self.screen.fill(BLACK)
        
        # Draw connecting message
        connecting_text = self.status_font.render("Connecting to server...", True, WHITE)
        text_rect = connecting_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(connecting_text, text_rect)
        
        pygame.display.flip()