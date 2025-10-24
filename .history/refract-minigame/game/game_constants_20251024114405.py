"""
Game constants and configuration values shared across the multiplayer game.
"""

# Display settings (viewport)
WIDTH = 800
HEIGHT = 600
FPS = 60
VSYNC = True

PLAYER_VISUAL_SIZE = 100
PLAYER_SPRITE_SIZE = 100  # Size to render the player sprite/animation on screen
PLAYER_HITBOX_WIDTH = 23
PLAYER_HITBOX_HEIGHT = 35
PLAYER_HITBOX_OFFSET_X = 39
PLAYER_HITBOX_OFFSET_Y = 30 

DRAW_HITBOXES = True
HITBOX_DEBUG_COLOR = (255, 0, 0)
HITBOX_DEBUG_WIDTH = 2

# World/Map settings
WORLD_WIDTH = 2400  # 3x screen width
WORLD_HEIGHT = 1800  # 3x screen height
BORDER_WIDTH = 100
BORDER_COLOR = (255, 255, 255)  # White borders

TILE_WIDTH = 64
TILE_HEIGHT = 48
WALL_HEIGHT = 16

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

START_X = WORLD_WIDTH // 2 - PLAYER_VISUAL_SIZE // 2
START_Y = WORLD_HEIGHT // 2 - PLAYER_VISUAL_SIZE // 2

PROJECTILE_SIZE = 20
PROJECTILE_SPEED = 8
PROJECTILE_LIFETIME = 300
PROJECTILE_COLOR = (255, 255, 0)
PROJECTILE_VISUAL_SIZE = 32

SHOOT_COOLDOWN = 0.5

# Health system settings
PLAYER_MAX_HP = 100
HEALTH_BAR_WIDTH = PLAYER_HITBOX_WIDTH
HEALTH_BAR_HEIGHT = 5
HEALTH_BAR_OFFSET_Y = -10  # Pixels above the hitbox
HEALTH_BAR_BG_COLOR = (100, 100, 100)  # Gray background
HEALTH_BAR_FILL_COLOR = (0, 255, 0)  # Green fill
HEALTH_BAR_BORDER_COLOR = (255, 255, 255)  # White border
HEALTH_BAR_BORDER_WIDTH = 1

# Damage settings
DEFAULT_PROJECTILE_DAMAGE = 25  # 1/4 of max HP (25 out of 100)

def get_world_bounds():
    return (0, 0, WORLD_WIDTH, WORLD_HEIGHT)

# Network message types
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
MSG_DAMAGE = "DAMAGE"  # Damage event with health update
MSG_RESPAWN = "RESPAWN"  # Player respawn event