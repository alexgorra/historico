"""
Game constants and configuration values shared across the multiplayer game.
"""

# Display settings (viewport)
WIDTH = 800
HEIGHT = 600
FPS = 60

PLAYER_VISUAL_SIZE = 100
PLAYER_HITBOX_WIDTH = 70
PLAYER_HITBOX_HEIGHT = 85
PLAYER_HITBOX_OFFSET_X = 15
PLAYER_HITBOX_OFFSET_Y = 10

# Debug settings
DRAW_HITBOXES = False  # Set to True to draw hitbox outlines for all entities
HITBOX_DEBUG_COLOR = (255, 0, 0)  # Red outline for hitboxes
HITBOX_DEBUG_WIDTH = 2  # Thickness of hitbox outline

# World/Map settings
WORLD_WIDTH = 2400  # 3x screen width
WORLD_HEIGHT = 1800  # 3x screen height
BORDER_WIDTH = 100
BORDER_COLOR = (255, 255, 255)  # White borders

# Camera settings
CAMERA_DEAD_ZONE = 50  # Pixels from center before camera starts moving
CAMERA_SMOOTHING = 0.15  # Lower = more delay/smoothness (0.1-0.3)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = {
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),
    'yellow': (255, 255, 0),
    'purple': (128, 0, 128),
    'orange': (255, 165, 0)
}

# Network settings
DEFAULT_SERVER_HOST = 'localhost'
DEFAULT_SERVER_PORT = 5555

# Game settings
PLAYER_SPEED = 5

# Starting position (center of world)
START_X = WORLD_WIDTH // 2 - PLAYER_SIZE // 2
START_Y = WORLD_HEIGHT // 2 - PLAYER_SIZE // 2

# Projectile settings
PROJECTILE_SIZE = 5
PROJECTILE_SPEED = 8
PROJECTILE_LIFETIME = 600  # frames (10 seconds at 60 FPS) - backup if doesn't hit border
PROJECTILE_COLOR = (255, 255, 0)  # Yellow
PROJECTILE_VISUAL_SIZE = 32  # Size for projectile animation rendering

# Shooting settings
SHOOT_COOLDOWN = 0.5  # Seconds between shots (0.5s = 30 frames at 60 FPS)

# Helper function to get current world bounds
def get_world_bounds():
    """Returns current world boundaries (min_x, min_y, max_x, max_y)"""
    return (0, 0, WORLD_WIDTH, WORLD_HEIGHT)

# Hitbox settings
HITBOX_ENABLED = True  # Always show hitboxes
HITBOX_COLOR = (255, 0, 0)  # Red
HITBOX_ALPHA = 0  # COMPLETELY TRANSPARENT
HITBOX_SIZE = PLAYER_SIZE  # Same size as player

# Protocol messages
MSG_WELCOME = "WELCOME"
MSG_PLAYERS = "PLAYERS"
MSG_UPDATE = "UPDATE"
MSG_NEW_PLAYER = "NEW_PLAYER"
MSG_PLAYER_LEFT = "PLAYER_LEFT"
MSG_MOVE = "MOVE"
MSG_DISCONNECT = "DISCONNECT"
MSG_SHOOT = "SHOOT"
MSG_PROJECTILE_UPDATE = "PROJECTILE_UPDATE"
MSG_PROJECTILE_REMOVE = "PROJECTILE_REMOVE"
MSG_HIT = "HIT"

# Helper functions for world bounds
def get_world_bounds():
    """
    Get the current world boundaries.
    Returns a tuple of (min_x, min_y, max_x, max_y).
    This allows world bounds to be changed dynamically if needed.
    """
    return (0, 0, WORLD_WIDTH, WORLD_HEIGHT)

def is_within_world_bounds(x, y):
    """
    Check if a point is within the world boundaries.
    
    Args:
        x: X coordinate
        y: Y coordinate
    
    Returns:
        True if the point is within world bounds, False otherwise
    """
    min_x, min_y, max_x, max_y = get_world_bounds()
    return min_x <= x <= max_x and min_y <= y <= max_y