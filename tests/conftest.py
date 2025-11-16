"""
Pytest configuration and fixtures for game testing.
Provides mocking utilities for Pygame to enable headless testing.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, Mock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(autouse=True, scope="session")
def mock_pygame():
    """
    Auto-use fixture that mocks Pygame to prevent display initialization.
    This allows tests to run headlessly without requiring a display.
    Scope is 'session' so the mock persists across all tests.
    """
    # Create mock pygame module
    mock_pg = MagicMock()
    
    # Mock pygame.init() to do nothing
    mock_pg.init = MagicMock()
    
    # KeyArray class for simulating pygame key state
    class KeyArray:
        def __init__(self):
            self._keys = {}
        
        def __getitem__(self, key):
            return self._keys.get(key, False)
        
        def __setitem__(self, key, value):
            self._keys[key] = value
            
        def set_keys(self, key_dict):
            """Helper to set multiple keys at once. Accepts a dictionary."""
            self._keys = key_dict
    
    # Create a single KeyArray instance that persists for the test
    # but can be configured by tests
    key_array_instance = KeyArray()
    mock_pg.key.get_pressed = MagicMock(return_value=key_array_instance)
    # Store the instance on the mock so tests can access it
    mock_pg._key_array = key_array_instance
    
    # Mock key constants
    mock_pg.K_LEFT = 276
    mock_pg.K_RIGHT = 275
    mock_pg.K_UP = 273
    mock_pg.K_DOWN = 274
    mock_pg.K_a = 97
    mock_pg.K_d = 100
    mock_pg.K_w = 119
    mock_pg.K_s = 115
    mock_pg.K_ESCAPE = 27
    mock_pg.QUIT = 12
    mock_pg.KEYDOWN = 2
    
    # Mock mouse functions
    mock_pg.mouse.get_pressed = MagicMock(return_value=(False, False, False))
    mock_pg.mouse.get_pos = MagicMock(return_value=(0, 0))
    
    # Mock Rect class for collision detection
    class MockRect:
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.left = x
            self.right = x + width
            self.top = y
            self.bottom = y + height
        
        def colliderect(self, other):
            """Check collision with another rect using AABB."""
            return (self.left < other.right and self.right > other.left and
                    self.top < other.bottom and self.bottom > other.top)
    
    mock_pg.Rect = MockRect
    
    # Mock display functions
    mock_pg.display.set_mode = MagicMock(return_value=MagicMock())
    mock_pg.display.set_caption = MagicMock()
    mock_pg.display.flip = MagicMock()
    
    # Mock clock
    mock_pg.time.Clock = MagicMock(return_value=MagicMock())
    
    # Mock event
    mock_pg.event.get = MagicMock(return_value=[])
    
    # Replace pygame in sys.modules before any imports
    sys.modules['pygame'] = mock_pg
    
    yield mock_pg
    
    # Don't cleanup - keep mock in sys.modules to prevent module import issues


@pytest.fixture
def input_handler(mock_pygame):
    """Fixture that provides an InputHandler instance with mocked Pygame."""
    # Reset key state before each test
    mock_pygame._key_array.set_keys({})
    from input_handler import InputHandler
    return InputHandler()


@pytest.fixture
def sample_player_position():
    """Fixture providing a sample player position in the middle of the screen."""
    return {'x': 400, 'y': 300}


@pytest.fixture
def sample_other_players():
    """Fixture providing sample other player data for collision testing."""
    return {
        'player2': {'x': 100, 'y': 100, 'color': (0, 0, 255)},
        'player3': {'x': 600, 'y': 400, 'color': (0, 255, 0)}
    }


@pytest.fixture
def key_array(mock_pygame):
    """Fixture that provides a KeyArray for setting key states in tests."""
    class KeyArray:
        def __init__(self):
            self._keys = {}
        
        def __getitem__(self, key):
            return self._keys.get(key, False)
        
        def __setitem__(self, key, value):
            self._keys[key] = value
            
        def set_keys(self, **kwargs):
            """Helper to set multiple keys at once"""
            self._keys.update(kwargs)
    
    return KeyArray()
