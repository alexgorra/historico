import pygame
from game_constants import *
from network_client import NetworkClient
from game_renderer import GameRenderer
from input_handler import InputHandler
from projectile_system import ProjectileManager, Projectile

# Initialize Pygame
pygame.init()

class GameClient:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Multiplayer Squares Game")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.network_client = NetworkClient()
        self.renderer = GameRenderer(self.screen)
        self.input_handler = InputHandler()
        self.projectile_manager = ProjectileManager()
        
        # Game state
        self.frame_count = 0
        
        # Set up network callbacks
        self.network_client.set_callbacks(
            on_welcome=self._on_welcome,
            on_player_update=self._on_player_update,
            on_new_player=self._on_new_player,
            on_player_left=self._on_player_left,
            on_disconnect=self._on_disconnect,
            on_projectile_update=self._on_projectile_update,
            on_projectile_remove=self._on_projectile_remove
        )
        
        # Game state
        self.running = True
        
    def _on_welcome(self, player_id, x, y, color):
        """Callback for when we receive welcome message from server."""
        print(f"Welcome callback: {player_id} at ({x}, {y}) with color {color}")
        
    def _on_player_update(self, other_players):
        """Callback for when player data is updated."""
        pass  # No specific action needed, data is already updated in network_client
        
    def _on_new_player(self, player_id, x, y, color):
        """Callback for when a new player joins."""
        print(f"New player joined: {player_id}")
        
    def _on_player_left(self, player_id):
        """Callback for when a player leaves."""
        print(f"Player left: {player_id}")
        
    def _on_disconnect(self):
        """Callback for when disconnected from server."""
        print("Disconnected from server!")
        
    def _on_projectile_update(self, projectile_data):
        """Callback for when a projectile is created or updated."""
        # Create or update projectile in our local manager
        projectile = self.projectile_manager.projectiles.get(projectile_data['id'])
        if not projectile:
            # Create new projectile
            projectile = Projectile(
                projectile_data['id'],
                projectile_data['x'],
                projectile_data['y'],
                projectile_data['direction_x'],
                projectile_data['direction_y'],
                projectile_data['owner_id']
            )
            self.projectile_manager.projectiles[projectile_data['id']] = projectile
        else:
            # Update existing projectile
            projectile.x = projectile_data['x']
            projectile.y = projectile_data['y']
    
    def _on_projectile_remove(self, projectile_id):
        """Callback for when a projectile should be removed."""
        self.projectile_manager.remove_projectile(projectile_id)
        
    def connect_to_server(self):
        """Connect to the game server."""
        return self.network_client.connect()
    
    def handle_input(self):
        """Handle player input and send movement updates."""
        # Handle movement WITH COLLISION DETECTION
        new_x, new_y, moved = self.input_handler.handle_input(
            self.network_client.player_x, 
            self.network_client.player_y,
            self.network_client.other_players  # Pass other players for collision check
        )
        
        # Send update if position changed
        if moved:
            self.network_client.player_x = new_x
            self.network_client.player_y = new_y
            self.network_client.send_move(new_x, new_y)
        
        # Handle shooting
        should_shoot, target_x, target_y, direction_x, direction_y = self.input_handler.check_shooting(
            self.network_client.player_x, 
            self.network_client.player_y,
            self.frame_count
        )
        
        if should_shoot:
            # Calculate projectile starting position (center of player)
            start_x = self.network_client.player_x + PLAYER_SIZE // 2
            start_y = self.network_client.player_y + PLAYER_SIZE // 2
            
            # Send shoot command to server
            self.network_client.send_shoot(start_x, start_y, direction_x, direction_y)
    
    def draw(self):
        """Draw the game screen."""
        self.renderer.draw_frame(
            self.network_client.player_x,
            self.network_client.player_y,
            self.network_client.player_color,
            self.network_client.player_id,
            self.network_client.other_players,
            self.network_client.connected,
            self.projectile_manager.get_all_projectiles()
        )
    
    def run(self):
        """Main game loop."""
        if not self.connect_to_server():
            return
        
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if self.input_handler.check_quit_input(event):
                    self.running = False
            
            # Only handle input and draw if connected
            if self.network_client.connected:
                self.handle_input()
                self.draw()
            else:
                self.renderer.draw_disconnect_screen()
            
            # Update frame counter
            self.frame_count += 1
            self.clock.tick(FPS)
        
        # Cleanup
        self.network_client.disconnect()
        pygame.quit()

if __name__ == "__main__":
    client = GameClient()
    client.run()