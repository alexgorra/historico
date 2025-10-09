"""
Game constants and configuration values shared across the multiplayer game.
"""

# Display settings
WIDTH = 800
HEIGHT = 600
PLAYER_SIZE = 50
PLAYER_HEIGHT = 50
PLAYER_WIDTH = 50
FPS = 60

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

# Projectile settings
PROJECTILE_SIZE = 5
PROJECTILE_SPEED = 8
PROJECTILE_LIFETIME = 120  # frames (2 seconds at 60 FPS)
PROJECTILE_COLOR = (255, 255, 0)  # Yellow

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