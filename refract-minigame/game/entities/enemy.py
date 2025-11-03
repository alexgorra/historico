"""
Enemy entity class.
"""
from game_constants import (
    ENEMY_SPEED,
    ENEMY_MAX_HP,
    ENEMY_DAMAGE,
    ENEMY_DAMAGE_RANGE,
    ENEMY_STOP_DISTANCE,
    PLAYER_HITBOX_WIDTH,
    PLAYER_HITBOX_HEIGHT,
    PLAYER_HITBOX_OFFSET_X,
    PLAYER_HITBOX_OFFSET_Y,
    PLAYER_VISUAL_SIZE,
    ENEMY_DAMAGE_COOLDOWN
)
from core.game_object import GameObject
from systems.movement_system import TransformComponent
from systems.collision_system import CollisionComponent
from systems.health_system import HealthComponent
from systems.render_system import AnimationComponent
import math


class EnemyAIComponent:
    """AI component for enemy behavior."""
    
    def __init__(self, target_player):
        self.target_player = target_player
        self.last_damage_time = 0
    
    def update(self, owner, dt, other_enemies, map_renderer):
        """Update AI behavior - move towards target with collision avoidance."""
        if not self.target_player or not self.target_player.active:
            return
        
        # Calculate direction to target
        dx = self.target_player.x - owner.x
        dy = self.target_player.y - owner.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Stop before overlapping with player
        if distance > ENEMY_STOP_DISTANCE:
            # Normalize and move towards target
            move_x = (dx / distance) * ENEMY_SPEED
            move_y = (dy / distance) * ENEMY_SPEED
            
            # Store old position
            old_x, old_y = owner.x, owner.y
            
            # Try to move
            owner.x += move_x
            owner.y += move_y
            
            # Check collision with walls if map_renderer is available
            if map_renderer:
                owner_collision = owner.get_component(CollisionComponent)
                if owner_collision:
                    owner_rect = owner_collision.get_rect()
                    if owner_rect and map_renderer.check_wall_collision(owner_rect):
                        # Revert movement
                        owner.x, owner.y = old_x, old_y
                        return
            
            # Check collision with target player to prevent pushing
            owner_collision = owner.get_component(CollisionComponent)
            if owner_collision and self.target_player:
                player_collision = self.target_player.get_component(CollisionComponent)
                if player_collision and owner_collision.check_collision(self.target_player):
                    # Revert movement - we're close enough to attack
                    owner.x, owner.y = old_x, old_y
                    return
            
            # Check collision with other enemies
            if owner_collision and other_enemies:
                for other_enemy in other_enemies:
                    if other_enemy is owner or not other_enemy.active:
                        continue
                    
                    other_collision = other_enemy.get_component(CollisionComponent)
                    if other_collision and owner_collision.check_collision(other_enemy):
                        # Revert movement
                        owner.x, owner.y = old_x, old_y
                        return
    
    def check_damage_player(self, owner, current_time):
        """Check if enemy should damage the target player."""
        if not self.target_player or not self.target_player.active:
            return None
        
        # Check cooldown
        if current_time - self.last_damage_time < ENEMY_DAMAGE_COOLDOWN:
            return None
        
        # Calculate distance to target
        dx = self.target_player.x - owner.x
        dy = self.target_player.y - owner.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if within damage range
        if distance <= ENEMY_DAMAGE_RANGE:
            self.last_damage_time = current_time
            return self.target_player
        
        return None


class Enemy(GameObject):
    """Enemy entity with AI and health."""
    
    def __init__(self, enemy_id, x, y, target_player, animation_manager=None):
        super().__init__(x, y)
        
        self.enemy_id = enemy_id
        self.add_tag('enemy')
        
        # Interpolation for smooth network movement
        self.target_x = x
        self.target_y = y
        self.interpolation_speed = 0.2  # Smooth interpolation
        self.network_controlled = False  # Flag to disable AI when server-controlled
        
        # Add components
        self.add_component(TransformComponent, TransformComponent(x, y))
        
        collision = CollisionComponent(
            width=PLAYER_HITBOX_WIDTH,
            height=PLAYER_HITBOX_HEIGHT,
            offset_x=PLAYER_HITBOX_OFFSET_X,
            offset_y=PLAYER_HITBOX_OFFSET_Y
        )
        collision.add_collision_tag('projectile')
        self.add_component(CollisionComponent, collision)
        
        health = HealthComponent(max_hp=ENEMY_MAX_HP)
        self.add_component(HealthComponent, health)
        
        # AI component (not a Component subclass, just a helper)
        self.ai = EnemyAIComponent(target_player)
        
        # Animation
        if animation_manager:
            from systems.render_system import EnemyAnimationComponent
            anim = EnemyAnimationComponent(enemy_id, animation_manager)
            self.add_component(AnimationComponent, anim)
    
    def set_network_position(self, x, y):
        """Set target position from network update."""
        self.target_x = x
        self.target_y = y
        self.network_controlled = True  # Mark as server-controlled
    
    def update(self, dt, other_enemies=None, map_renderer=None):
        """Update enemy state."""
        super().update(dt)
        
        # If network-controlled, only do interpolation and animation
        if self.network_controlled:
            # Interpolate towards target position for smooth movement
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            
            # Move towards target
            self.x += dx * self.interpolation_speed
            self.y += dy * self.interpolation_speed
            
            # Update animation based on movement towards target
            anim_comp = self.get_component(AnimationComponent)
            if anim_comp and hasattr(anim_comp, 'update_from_position'):
                anim_comp.update_from_position(dt, self.target_x, self.target_y)
        else:
            # Local AI control (server-side only)
            if self.ai:
                if other_enemies is None:
                    other_enemies = []
                self.ai.update(self, dt, other_enemies, map_renderer)
                
                # Update animation based on actual movement
                anim_comp = self.get_component(AnimationComponent)
                if anim_comp and hasattr(anim_comp, 'update_from_position'):
                    anim_comp.update_from_position(dt, self.x, self.y)
