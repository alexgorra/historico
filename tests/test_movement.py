"""
Unit tests for player movement mechanics.
Tests keyboard input, boundary enforcement, and collision detection.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestBasicMovement:
    """Test basic player movement with arrow keys and WASD."""
    
    def test_move_right_with_arrow_key(self, input_handler, mock_pygame):
        """Test that pressing RIGHT arrow moves player right by PLAYER_SPEED."""
        from game_constants import PLAYER_SPEED
        
        # Set up key press using the mock's key array
        mock_pygame._key_array.set_keys({
            mock_pygame.K_RIGHT: True,
            mock_pygame.K_LEFT: False,
            mock_pygame.K_UP: False,
            mock_pygame.K_DOWN: False,
            mock_pygame.K_a: False,
            mock_pygame.K_d: False,
            mock_pygame.K_w: False,
            mock_pygame.K_s: False
        })
        
        # Initial position
        current_x, current_y = 400, 300
        other_players = {}
        
        # Handle input
        new_x, new_y, moved = input_handler.handle_input(current_x, current_y, other_players)
        
        # Assertions
        assert new_x == current_x + PLAYER_SPEED, f"Expected x to increase by {PLAYER_SPEED}"
        assert new_y == current_y, "Y position should not change"
        assert moved is True, "Movement flag should be True"
    
    def test_move_left_with_wasd(self, input_handler, mock_pygame):
        """Test that pressing 'A' key moves player left by PLAYER_SPEED."""
        from game_constants import PLAYER_SPEED
        
        # Set up key press
        mock_pygame._key_array.set_keys({
            mock_pygame.K_RIGHT: False,
            mock_pygame.K_LEFT: False,
            mock_pygame.K_UP: False,
            mock_pygame.K_DOWN: False,
            mock_pygame.K_a: True,
            mock_pygame.K_d: False,
            mock_pygame.K_w: False,
            mock_pygame.K_s: False
        })
        
        # Initial position
        current_x, current_y = 400, 300
        other_players = {}
        
        # Handle input
        new_x, new_y, moved = input_handler.handle_input(current_x, current_y, other_players)
        
        # Assertions
        assert new_x == current_x - PLAYER_SPEED, f"Expected x to decrease by {PLAYER_SPEED}"
        assert new_y == current_y, "Y position should not change"
        assert moved is True, "Movement flag should be True"
    
    def test_move_up_and_right_diagonal(self, input_handler, mock_pygame):
        """Test diagonal movement by pressing UP and RIGHT simultaneously."""
        from game_constants import PLAYER_SPEED
        
        # Set up key press for diagonal movement
        mock_pygame._key_array.set_keys({
            mock_pygame.K_RIGHT: True,
            mock_pygame.K_LEFT: False,
            mock_pygame.K_UP: True,
            mock_pygame.K_DOWN: False,
            mock_pygame.K_a: False,
            mock_pygame.K_d: False,
            mock_pygame.K_w: False,
            mock_pygame.K_s: False
        })
        
        # Initial position
        current_x, current_y = 400, 300
        other_players = {}
        
        # Handle input
        new_x, new_y, moved = input_handler.handle_input(current_x, current_y, other_players)
        
        # Assertions
        assert new_x == current_x + PLAYER_SPEED, f"Expected x to increase by {PLAYER_SPEED}"
        assert new_y == current_y - PLAYER_SPEED, f"Expected y to decrease by {PLAYER_SPEED}"
        assert moved is True, "Movement flag should be True"
    
    def test_no_movement_when_no_keys_pressed(self, input_handler, mock_pygame):
        """Test that player doesn't move when no keys are pressed."""
        # Set up no key press
        mock_pygame._key_array.set_keys({
            mock_pygame.K_RIGHT: False,
            mock_pygame.K_LEFT: False,
            mock_pygame.K_UP: False,
            mock_pygame.K_DOWN: False,
            mock_pygame.K_a: False,
            mock_pygame.K_d: False,
            mock_pygame.K_w: False,
            mock_pygame.K_s: False
        })
        
        # Initial position
        current_x, current_y = 400, 300
        other_players = {}
        
        # Handle input
        new_x, new_y, moved = input_handler.handle_input(current_x, current_y, other_players)
        
        # Assertions
        assert new_x == current_x, "X position should not change"
        assert new_y == current_y, "Y position should not change"
        assert moved is False, "Movement flag should be False"


class TestBoundaryEnforcement:
    """Test that players cannot move beyond screen boundaries."""
    
    def test_cannot_move_past_left_boundary(self, input_handler, mock_pygame):
        """Test that player stops at x=0 when trying to move left."""
        # Set up left key press
        mock_pygame._key_array.set_keys({
            mock_pygame.K_RIGHT: False,
            mock_pygame.K_LEFT: True,
            mock_pygame.K_UP: False,
            mock_pygame.K_DOWN: False,
            mock_pygame.K_a: False,
            mock_pygame.K_d: False,
            mock_pygame.K_w: False,
            mock_pygame.K_s: False
        })
        
        # Position at left edge
        current_x, current_y = 0, 300
        other_players = {}
        
        # Handle input
        new_x, new_y, moved = input_handler.handle_input(current_x, current_y, other_players)
        
        # Assertions
        assert new_x == 0, "Player should not move past left boundary (x=0)"
        assert new_y == current_y, "Y position should not change"
        assert moved is False, "Movement flag should be False when at boundary"
    
    def test_cannot_move_past_right_boundary(self, input_handler, mock_pygame):
        """Test that player stops at right edge when trying to move right."""
        from game_constants import WIDTH, PLAYER_SIZE
        
        # Set up right key press
        mock_pygame._key_array.set_keys({
            mock_pygame.K_RIGHT: True,
            mock_pygame.K_LEFT: False,
            mock_pygame.K_UP: False,
            mock_pygame.K_DOWN: False,
            mock_pygame.K_a: False,
            mock_pygame.K_d: False,
            mock_pygame.K_w: False,
            mock_pygame.K_s: False
        })
        
        # Position at right edge
        current_x = WIDTH - PLAYER_SIZE
        current_y = 300
        other_players = {}
        
        # Handle input
        new_x, new_y, moved = input_handler.handle_input(current_x, current_y, other_players)
        
        # Assertions
        assert new_x == WIDTH - PLAYER_SIZE, f"Player should not move past right boundary (x={WIDTH - PLAYER_SIZE})"
        assert new_y == current_y, "Y position should not change"
        assert moved is False, "Movement flag should be False when at boundary"
    
    def test_cannot_move_past_top_boundary(self, input_handler, mock_pygame):
        """Test that player stops at y=0 when trying to move up."""
        # Set up up key press
        mock_pygame._key_array.set_keys({
            mock_pygame.K_RIGHT: False,
            mock_pygame.K_LEFT: False,
            mock_pygame.K_UP: False,
            mock_pygame.K_DOWN: False,
            mock_pygame.K_a: False,
            mock_pygame.K_d: False,
            mock_pygame.K_w: True,
            mock_pygame.K_s: False
        })
        
        # Position at top edge
        current_x, current_y = 400, 0
        other_players = {}
        
        # Handle input
        new_x, new_y, moved = input_handler.handle_input(current_x, current_y, other_players)
        
        # Assertions
        assert new_x == current_x, "X position should not change"
        assert new_y == 0, "Player should not move past top boundary (y=0)"
        assert moved is False, "Movement flag should be False when at boundary"
    
    def test_cannot_move_past_bottom_boundary(self, input_handler, mock_pygame):
        """Test that player stops at bottom edge when trying to move down."""
        from game_constants import HEIGHT, PLAYER_SIZE
        
        # Set up down key press
        mock_pygame._key_array.set_keys({
            mock_pygame.K_RIGHT: False,
            mock_pygame.K_LEFT: False,
            mock_pygame.K_UP: False,
            mock_pygame.K_DOWN: False,
            mock_pygame.K_a: False,
            mock_pygame.K_d: False,
            mock_pygame.K_w: False,
            mock_pygame.K_s: True
        })
        
        # Position at bottom edge
        current_x = 400
        current_y = HEIGHT - PLAYER_SIZE
        other_players = {}
        
        # Handle input
        new_x, new_y, moved = input_handler.handle_input(current_x, current_y, other_players)
        
        # Assertions
        assert new_x == current_x, "X position should not change"
        assert new_y == HEIGHT - PLAYER_SIZE, f"Player should not move past bottom boundary (y={HEIGHT - PLAYER_SIZE})"
        assert moved is False, "Movement flag should be False when at boundary"


class TestCollisionDetection:
    """Test collision detection with other players."""
    
    def test_collision_blocks_movement_into_other_player(self, input_handler, mock_pygame):
        """Test that player cannot move into another player's space."""
        from game_constants import PLAYER_SIZE, PLAYER_SPEED
        
        # Set up right key press
        mock_pygame._key_array.set_keys({
            mock_pygame.K_RIGHT: True,
            mock_pygame.K_LEFT: False,
            mock_pygame.K_UP: False,
            mock_pygame.K_DOWN: False,
            mock_pygame.K_a: False,
            mock_pygame.K_d: False,
            mock_pygame.K_w: False,
            mock_pygame.K_s: False
        })
        
        # Current player position
        current_x, current_y = 100, 100
        
        # Other player directly to the right, close enough to collide
        other_players = {
            'player2': {
                'x': current_x + PLAYER_SIZE,  # Adjacent
                'y': current_y,
                'color': (0, 0, 255)
            }
        }
        
        # Handle input - should NOT move due to collision
        new_x, new_y, moved = input_handler.handle_input(current_x, current_y, other_players)
        
        # Assertions
        assert new_x == current_x, "Player should not move into other player (collision detected)"
        assert new_y == current_y, "Y position should not change"
        assert moved is False, "Movement flag should be False when collision blocks movement"
    
    def test_no_collision_when_players_far_apart(self, input_handler, mock_pygame):
        """Test that movement works normally when other players are far away."""
        from game_constants import PLAYER_SPEED
        
        # Set up down key press
        mock_pygame._key_array.set_keys({
            mock_pygame.K_RIGHT: False,
            mock_pygame.K_LEFT: False,
            mock_pygame.K_UP: False,
            mock_pygame.K_DOWN: True,
            mock_pygame.K_a: False,
            mock_pygame.K_d: False,
            mock_pygame.K_w: False,
            mock_pygame.K_s: False
        })
        
        # Current player position
        current_x, current_y = 100, 100
        
        # Other player far away
        other_players = {
            'player2': {
                'x': 500,
                'y': 400,
                'color': (0, 0, 255)
            }
        }
        
        # Handle input - should move normally
        new_x, new_y, moved = input_handler.handle_input(current_x, current_y, other_players)
        
        # Assertions
        assert new_x == current_x, "X position should not change"
        assert new_y == current_y + PLAYER_SPEED, f"Y position should increase by {PLAYER_SPEED}"
        assert moved is True, "Movement flag should be True when no collision"
    
    def test_collision_with_overlapping_player(self, input_handler, mock_pygame):
        """Test collision detection with partially overlapping players."""
        from game_constants import PLAYER_SIZE
        
        # Set up up key press
        mock_pygame._key_array.set_keys({
            mock_pygame.K_RIGHT: False,
            mock_pygame.K_LEFT: False,
            mock_pygame.K_UP: True,
            mock_pygame.K_DOWN: False,
            mock_pygame.K_a: False,
            mock_pygame.K_d: False,
            mock_pygame.K_w: False,
            mock_pygame.K_s: False
        })
        
        # Current player position
        current_x, current_y = 100, 100
        
        # Other player partially overlapping above
        other_players = {
            'player2': {
                'x': current_x + 10,  # Slightly offset horizontally
                'y': current_y - PLAYER_SIZE + 10,  # Overlapping vertically
                'color': (0, 255, 0)
            }
        }
        
        # Handle input - should NOT move due to collision
        new_x, new_y, moved = input_handler.handle_input(current_x, current_y, other_players)
        
        # Assertions
        assert new_x == current_x, "X position should not change"
        assert new_y == current_y, "Player should not move into overlapping player"
        assert moved is False, "Movement flag should be False when collision detected"
