"""
Player entity class.
"""
from game_constants import (
    PLAYER_SPEED, 
    PLAYER_VISUAL_SIZE,
    PLAYER_HITBOX_WIDTH,
    PLAYER_HITBOX_HEIGHT,
    PLAYER_HITBOX_OFFSET_X,
    PLAYER_HITBOX_OFFSET_Y
)
from core.game_object import GameObject
from systems.movement_system import MovementComponent, TransformComponent
from systems.input_system import InputComponent
from systems.collision_system import CollisionComponent
from systems.render_system import AnimationComponent


class Player(GameObject):
    """Player entity with all necessary components."""
    
    def __init__(self, player_id, x, y, color, animation_manager=None, is_local=False):
        super().__init__(x, y)
        
        self.player_id = player_id
        self.is_local = is_local
        self.color = color
        
        self.add_tag('player')
        
        self.add_component(TransformComponent, TransformComponent(x, y))
        self.add_component(MovementComponent, MovementComponent(speed=PLAYER_SPEED))
        
        collision = CollisionComponent(
            width=PLAYER_HITBOX_WIDTH,
            height=PLAYER_HITBOX_HEIGHT,
            offset_x=PLAYER_HITBOX_OFFSET_X,
            offset_y=PLAYER_HITBOX_OFFSET_Y
        )
        collision.add_collision_tag('player')
        collision.add_collision_tag('projectile')
        self.add_component(CollisionComponent, collision)
        
        if animation_manager:
            anim = AnimationComponent(player_id, animation_manager)
            anim.is_local_player = is_local
            self.add_component(AnimationComponent, anim)
        
        if is_local:
            self.add_component(InputComponent, InputComponent())
    
    def set_position(self, x, y):
        """Set player position (for network updates)."""
        self.x = x
        self.y = y
    
    def get_center(self):
        """Get the center position of the player (based on visual size)."""
        return (self.x + PLAYER_VISUAL_SIZE // 2, self.y + PLAYER_VISUAL_SIZE // 2)
