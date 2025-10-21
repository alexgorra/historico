"""
Refactored game client using component-based architecture.
"""
import pygame
from game_constants import *
from network_client import NetworkClient
from game_renderer import GameRenderer
from animation_system import AnimationManager
from core.game_state import GameState
from entities.player import Player
from entities.projectile import Projectile
from systems.input_system import InputComponent
from systems.movement_system import MovementComponent
from systems.render_system import AnimationComponent
from systems.collision_system import CollisionComponent

pygame.init()


class RefactoredGameClient:
    """Game client using component-based architecture."""
    
    def __init__(self):
        """Initialize the game client."""
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Multiplayer Squares Game - Refactored")
        self.clock = pygame.time.Clock()
        
        # Initialize core systems
        self.game_state = GameState()
        self.animation_manager = AnimationManager()
        self.network_client = NetworkClient()
        self.renderer = GameRenderer(self.screen)
        
        # Game state
        self.frame_count = 0
        self.running = True
        
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
    
    def _on_welcome(self, player_id, x, y, color):
        """Handle welcome message from server."""
        print(f"Welcome! You are {player_id} at ({x}, {y}) with color {color}")
        
        # Create local player object
        local_player = Player(
            player_id=player_id,
            x=x,
            y=y,
            color=color,
            animation_manager=self.animation_manager,
            is_local=True
        )
        
        # Add to game state
        self.game_state.add_object(local_player)
        self.game_state.player_id = player_id
        self.game_state.player_object = local_player
        self.game_state.connected = True
        
        print(f"Created local player object with {len(local_player.components)} components")
    
    def _on_player_update(self, other_players):
        """Handle player updates from server."""
        # Update existing player positions or create new players
        for player_id, player_data in other_players.items():
            if player_id in self.game_state.other_players:
                player_obj = self.game_state.other_players[player_id]
                player_obj.set_position(player_data['x'], player_data['y'])
            else:
                # Create new player that we didn't know about
                remote_player = Player(
                    player_id=player_id,
                    x=player_data['x'],
                    y=player_data['y'],
                    color=player_data['color'],
                    animation_manager=self.animation_manager,
                    is_local=False
                )
                self.game_state.add_object(remote_player)
                self.game_state.other_players[player_id] = remote_player
    
    def _on_new_player(self, player_id, x, y, color):
        """Handle new player joining."""
        print(f"New player joined: {player_id}")
        
        # Create remote player object
        remote_player = Player(
            player_id=player_id,
            x=x,
            y=y,
            color=color,
            animation_manager=self.animation_manager,
            is_local=False
        )
        
        # Add to game state
        self.game_state.add_object(remote_player)
        self.game_state.other_players[player_id] = remote_player
        
        print(f"Created remote player object for {player_id}")
    
    def _on_player_left(self, player_id):
        """Handle player leaving."""
        print(f"Player left: {player_id}")
        
        if player_id in self.game_state.other_players:
            player_obj = self.game_state.other_players[player_id]
            self.game_state.remove_object(player_obj)
            del self.game_state.other_players[player_id]
        
        # Clean up animations
        self.animation_manager.remove_player(player_id)
    
    def _on_disconnect(self):
        """Handle disconnection from server."""
        print("Disconnected from server!")
        self.game_state.connected = False
    
    def _on_projectile_update(self, projectile_data):
        """Handle projectile update from server."""
        projectile_id = projectile_data['id']
        
        if projectile_id in self.game_state.projectiles:
            # Update existing projectile
            proj_obj = self.game_state.projectiles[projectile_id]
            proj_obj.x = projectile_data['x']
            proj_obj.y = projectile_data['y']
        else:
            # Create new projectile
            projectile = Projectile(
                projectile_id=projectile_id,
                x=projectile_data['x'],
                y=projectile_data['y'],
                direction_x=projectile_data['direction_x'],
                direction_y=projectile_data['direction_y'],
                owner_id=projectile_data['owner_id']
            )
            
            self.game_state.add_object(projectile)
            self.game_state.projectiles[projectile_id] = projectile
    
    def _on_projectile_remove(self, projectile_id):
        """Handle projectile removal."""
        if projectile_id in self.game_state.projectiles:
            proj_obj = self.game_state.projectiles[projectile_id]
            self.game_state.remove_object(proj_obj)
            del self.game_state.projectiles[projectile_id]
    
    def connect_to_server(self):
        """Connect to the game server."""
        return self.network_client.connect()
    
    def handle_input(self):
        """Handle player input."""
        if not self.game_state.player_object:
            return
        
        player = self.game_state.player_object
        input_comp = player.get_component(InputComponent)
        if not input_comp:
            return
        
        should_shoot, target_x, target_y, direction_x, direction_y = input_comp.check_shooting(self.renderer)
        
        if should_shoot:
            center_x, center_y = player.get_center()
            self.network_client.send_shoot(center_x, center_y, direction_x, direction_y)
    
    def send_position_update(self):
        """Send position update if player moved."""
        if not self.game_state.player_object:
            return
        
        player = self.game_state.player_object
        movement = player.get_component(MovementComponent)
        
        if movement and (movement.velocity_x != 0 or movement.velocity_y != 0):
            # Round coordinates to avoid float parsing issues on server
            self.network_client.send_move(
                int(round(player.x)),
                int(round(player.y))
            )
    
    def check_collisions(self):
        """Check for collisions between projectiles and players."""
        hits_to_process = []
        
        # Get all projectiles and players
        projectiles = list(self.game_state.projectiles.values())
        players = [self.game_state.player_object] + list(self.game_state.other_players.values())
        players = [p for p in players if p and p.active]
        
        for proj in projectiles:
            if not proj.active:
                continue
            
            proj_collision = proj.get_component(CollisionComponent)
            if not proj_collision:
                continue
            
            # Check collision with players
            for player in players:
                if not player.active:
                    continue
                
                # Don't collide with owner
                if proj.owner_id == player.player_id:
                    continue
                
                player_collision = player.get_component(CollisionComponent)
                if not player_collision:
                    continue
                
                if proj_collision.check_collision(player):
                    hits_to_process.append((player.player_id, proj.owner_id, proj.projectile_id))
        
        # Process hits
        for victim_id, shooter_id, projectile_id in hits_to_process:
            self.network_client.send_hit(victim_id, shooter_id, projectile_id)
            
            # Remove projectile locally
            if projectile_id in self.game_state.projectiles:
                proj_obj = self.game_state.projectiles[projectile_id]
                self.game_state.remove_object(proj_obj)
                del self.game_state.projectiles[projectile_id]
    
    def _resolve_player_collisions(self):
        """Resolve player-vs-player collisions."""
        local_player = self.game_state.player_object
        local_col = local_player.get_component(CollisionComponent)
        if not local_col:
            return
        
        lp_rect = local_col.get_rect()
        for other in self.game_state.other_players.values():
            if not other or not other.active:
                continue
            
            other_col = other.get_component(CollisionComponent)
            if not other_col:
                continue
            
            other_rect = other_col.get_rect()
            if lp_rect.colliderect(other_rect):
                overlap = lp_rect.clip(other_rect)
                if overlap.width < overlap.height:
                    offset = overlap.width if lp_rect.centerx < other_rect.centerx else -overlap.width
                    local_player.x -= offset
                else:
                    offset = overlap.height if lp_rect.centery < other_rect.centery else -overlap.height
                    local_player.y -= offset
    
    def update(self, dt):
        """Update game state."""
        self.game_state.update(dt)
        
        if self.game_state.player_object:
            anim_comp = self.game_state.player_object.get_component(AnimationComponent)
            if anim_comp and anim_comp.is_local_player:
                keys = pygame.key.get_pressed()
                anim_comp.update_from_keys(dt, keys)
            
            self._resolve_player_collisions()
    
    def render(self):
        """Render the game."""
        if not self.game_state.connected:
            self.renderer.draw_disconnect_screen()
            return
        
        self.screen.fill(BLACK)
        
        camera_x = camera_y = 0
        if self.game_state.player_object:
            self.renderer.update_camera(
                self.game_state.player_object.x,
                self.game_state.player_object.y
            )
            camera_x = self.renderer.camera_x
            camera_y = self.renderer.camera_y
        
        self.renderer._draw_world_borders()
        
        from entities.projectile import ProjectileRendererComponent
        for obj in self.game_state.game_objects:
            if not obj.active:
                continue
            
            anim_comp = obj.get_component(AnimationComponent)
            if anim_comp:
                anim_comp.render(self.screen, camera_x, camera_y)
                continue
            
            proj_renderer = obj.get_component(ProjectileRendererComponent)
            if proj_renderer:
                proj_renderer.render(self.screen, camera_x, camera_y)
        
        if DRAW_HITBOXES:
            for obj in self.game_state.game_objects:
                if obj.active:
                    collision_comp = obj.get_component(CollisionComponent)
                    if collision_comp:
                        collision_comp.debug_render(self.screen, camera_x, camera_y)
        
        player_count = len(self.game_state.get_objects_with_tag('player'))
        self.renderer._draw_connection_status(self.network_client.connected, player_count)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        if not self.connect_to_server():
            return
        
        self.running = True
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            if self.game_state.connected:
                # Calculate delta time
                dt = self.clock.get_time()
                
                # Handle input
                self.handle_input()
                
                # Update game state
                self.update(dt)
                
                # Send position update
                self.send_position_update()
                
                # Check collisions
                self.check_collisions()
                
                # Render
                self.render()
            else:
                self.renderer.draw_disconnect_screen()
                pygame.display.flip()
            
            # Maintain frame rate
            self.frame_count += 1
            self.clock.tick(FPS)
        
        # Cleanup
        self.network_client.disconnect()
        pygame.quit()


if __name__ == "__main__":
    client = RefactoredGameClient()
    client.run()
