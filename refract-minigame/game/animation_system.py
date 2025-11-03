"""
Animation system for handling Aseprite sprite sheet animations.
"""

import pygame
import json
import os
from game_constants import *


class AsepriteAnimation:
    def __init__(self, json_path, image_path):
        """Initialize the Aseprite animation from JSON and image files."""
        self.frames = []
        self.current_frame = 0
        self.frame_timer = 0
        self.playing = False
        self.loop = True
        
        # Load animation data
        self._load_animation(json_path, image_path)
    
    def _load_animation(self, json_path, image_path):
        """Load animation data from Aseprite JSON and sprite sheet."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            sprite_sheet = pygame.image.load(image_path)
            try:
                sprite_sheet = sprite_sheet.convert_alpha()
            except pygame.error:
                pass
            
            for frame_data in data['frames']:
                frame_info = frame_data['frame']
                duration = frame_data['duration']
                
                frame_surface = pygame.Surface((frame_info['w'], frame_info['h']), pygame.SRCALPHA)
                frame_surface.blit(sprite_sheet, (0, 0), 
                                 (frame_info['x'], frame_info['y'], 
                                  frame_info['w'], frame_info['h']))
                try:
                    frame_surface = frame_surface.convert_alpha()
                except pygame.error:
                    pass
                
                self.frames.append({
                    'surface': frame_surface,
                    'duration': duration,
                    'width': frame_info['w'],
                    'height': frame_info['h']
                })
            
        except Exception as e:
            print(f"Error loading animation: {e}")
            fallback_surface = pygame.Surface((PLAYER_VISUAL_SIZE, PLAYER_VISUAL_SIZE), pygame.SRCALPHA)
            fallback_surface.fill((255, 0, 255))
            self.frames = [{
                'surface': fallback_surface,
                'duration': 150,
                'width': PLAYER_VISUAL_SIZE,
                'height': PLAYER_VISUAL_SIZE
            }]
    
    def play(self, loop=True):
        """Start playing the animation."""
        self.playing = True
        self.loop = loop
    
    def stop(self):
        """Stop the animation."""
        self.playing = False
    
    def reset(self):
        """Reset animation to first frame."""
        self.current_frame = 0
        self.frame_timer = 0
    
    def update(self, dt_ms):
        """Update animation frame based on delta time in milliseconds."""
        if not self.playing or len(self.frames) == 0:
            return
        
        # Convert frame time to milliseconds (60 FPS = ~16.67ms per frame)
        self.frame_timer += dt_ms
        
        current_frame_data = self.frames[self.current_frame]
        
        # Check if it's time to advance to next frame
        if self.frame_timer >= current_frame_data['duration']:
            self.frame_timer = 0
            self.current_frame += 1
            
            # Handle looping
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.playing = False
    
    def get_current_frame(self):
        """Get the current frame surface."""
        if len(self.frames) == 0:
            return None
        return self.frames[self.current_frame]['surface']
    
    def get_frame_size(self):
        """Get the size of the current frame."""
        if len(self.frames) == 0:
            return (PLAYER_VISUAL_SIZE, PLAYER_VISUAL_SIZE)
        current_frame_data = self.frames[self.current_frame]
        return (current_frame_data['width'], current_frame_data['height'])


class PlayerAnimator:
    """Manages animations for a single player."""
    
    def __init__(self, player_id, assets_path):
        self.player_id = player_id
        self.assets_path = os.path.join(assets_path, 'main_c')  # Updated to use main_c folder
        self.animations = {}
        self.current_animation = 'idle'
        self.current_direction = 'f'
        self.flip_sprite = False
        self.last_pos_x = 0
        self.last_pos_y = 0
        
        # Track movement for better animation detection
        self.position_history = []  # Track last few positions
        self.idle_frames = 0  # Count frames without movement
        
        self._load_animations()
    
    def _load_animations(self):
        """Load all animations for the player."""
        idle_anim = self._load_animation('f_idle')
        if idle_anim:
            self.animations['idle'] = idle_anim
            idle_anim.play(loop=True)
        
        for direction in ['f', 'b', 'l', 'r']:
            walk_anim = self._load_animation(f'{direction}_walk')
            if walk_anim:
                self.animations[f'walk_{direction}'] = walk_anim
    
    def _load_animation(self, name):
        """Load a single animation."""
        try:
            json_path = os.path.join(self.assets_path, f'{name}.json')
            png_path = os.path.join(self.assets_path, f'{name}.png')
            
            if os.path.exists(json_path) and os.path.exists(png_path):
                return AsepriteAnimation(json_path, png_path)
        except Exception as e:
            print(f"Error loading {name}: {e}")
        return None
    
    def update(self, dt, keys_pressed=None, pos_x=None, pos_y=None):
        """Update animator state."""
        if keys_pressed is not None:
            self._update_from_keys(dt, keys_pressed)
        elif pos_x is not None and pos_y is not None:
            self._update_from_position(dt, pos_x, pos_y)
        
        current_anim = self.animations.get(self.current_animation)
        if current_anim:
            current_anim.update(dt)
    
    def _update_from_keys(self, dt, keys):
        """Update based on keyboard input."""
        moving = False
        new_direction = self.current_direction
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            moving = True
            new_direction = 'l'
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            moving = True
            new_direction = 'r'
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            moving = True
            new_direction = 'b'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            moving = True
            new_direction = 'f'
        
        self._set_animation('walk' if moving else 'idle', new_direction)
    
    def _update_from_position(self, dt, pos_x, pos_y):
        """Update based on position changes with better movement detection."""
        # Ensure positions are numeric (defensive programming)
        try:
            pos_x = float(pos_x)
            pos_y = float(pos_y)
        except (TypeError, ValueError):
            return  # Invalid position data, skip update
        
        dx = pos_x - self.last_pos_x
        dy = pos_y - self.last_pos_y
        
        # Calculate total movement
        movement_distance = (dx * dx + dy * dy) ** 0.5
        
        # Update position history (keep last 5 positions)
        self.position_history.append((pos_x, pos_y))
        if len(self.position_history) > 5:
            self.position_history.pop(0)
        
        # Calculate average movement over recent frames for smoother detection
        avg_movement = 0
        if len(self.position_history) >= 2:
            for i in range(1, len(self.position_history)):
                prev = self.position_history[i-1]
                curr = self.position_history[i]
                dx_hist = curr[0] - prev[0]
                dy_hist = curr[1] - prev[1]
                avg_movement += (dx_hist * dx_hist + dy_hist * dy_hist) ** 0.5
            avg_movement /= (len(self.position_history) - 1)
        
        self.last_pos_x = pos_x
        self.last_pos_y = pos_y
        
        # Use higher threshold and average movement to reduce jitter
        # Movement threshold increased from 0.1 to 2.0 pixels
        if avg_movement < 2.0 and movement_distance < 2.0:
            self.idle_frames += 1
            # Only switch to idle after several frames of no movement (hysteresis)
            if self.idle_frames > 3:
                self._set_animation('idle', self.current_direction)
            return
        else:
            self.idle_frames = 0
        
        # Determine direction based on movement
        new_direction = self.current_direction
        if abs(dx) > abs(dy):
            new_direction = 'r' if dx > 0 else 'l'
        else:
            new_direction = 'f' if dy > 0 else 'b'
        
        self._set_animation('walk', new_direction)
    
    def _set_animation(self, state, direction):
        """Set the current animation."""
        if state == 'idle':
            new_anim = 'idle'
        else:
            new_anim = f'walk_{direction}'
        
        if new_anim != self.current_animation:
            self.current_animation = new_anim
            self.current_direction = direction
            anim = self.animations.get(new_anim)
            if anim:
                anim.reset()
                anim.play(loop=True)
    
    def get_current_frame(self):
        """Get the current animation frame."""
        anim = self.animations.get(self.current_animation)
        return anim.get_current_frame() if anim else None
    
    def should_flip(self):
        """Check if sprite should be flipped horizontally."""
        return False


class EnemyAnimator:
    """Manages animations for a single enemy."""
    
    def __init__(self, enemy_id, assets_path):
        self.enemy_id = enemy_id
        self.assets_path = os.path.join(assets_path, 'enemy1')
        self.animations = {}
        self.current_animation = 'walk_f'
        self.current_direction = 'f'
        self.last_pos_x = 0
        self.last_pos_y = 0
        self.position_history = []
        
        self._load_animations()
    
    def _load_animations(self):
        """Load all animations for the enemy."""
        for direction in ['fe', 'be', 'le', 're']:
            walk_anim = self._load_animation(f'{direction}_walk')
            if walk_anim:
                # Map enemy directions (fe, be, le, re) to standard directions (f, b, l, r)
                standard_dir = direction[0]  # Take first character
                self.animations[f'walk_{standard_dir}'] = walk_anim
    
    def _load_animation(self, name):
        """Load a single animation."""
        try:
            json_path = os.path.join(self.assets_path, f'{name}.json')
            png_path = os.path.join(self.assets_path, f'{name}.png')
            
            if os.path.exists(json_path) and os.path.exists(png_path):
                return AsepriteAnimation(json_path, png_path)
        except Exception as e:
            print(f"Error loading {name}: {e}")
        return None
    
    def update(self, dt, pos_x=None, pos_y=None):
        """Update animator state."""
        if pos_x is not None and pos_y is not None:
            self._update_from_position(dt, pos_x, pos_y)
        
        current_anim = self.animations.get(self.current_animation)
        if current_anim:
            current_anim.update(dt)
    
    def _update_from_position(self, dt, pos_x, pos_y):
        """Update based on position changes."""
        try:
            pos_x = float(pos_x)
            pos_y = float(pos_y)
        except (TypeError, ValueError):
            return
        
        dx = pos_x - self.last_pos_x
        dy = pos_y - self.last_pos_y
        
        self.last_pos_x = pos_x
        self.last_pos_y = pos_y
        
        # Only update direction if movement is significant (avoid jitter from tiny movements)
        movement_threshold = 0.5
        if abs(dx) > movement_threshold or abs(dy) > movement_threshold:
            # Determine direction based on movement
            new_direction = self.current_direction
            if abs(dx) > abs(dy):
                new_direction = 'r' if dx > 0 else 'l'
            else:
                new_direction = 'f' if dy > 0 else 'b'
            
            self._set_animation('walk', new_direction)
    
    def _set_animation(self, state, direction):
        """Set the current animation."""
        new_anim = f'walk_{direction}'
        
        if new_anim != self.current_animation:
            self.current_animation = new_anim
            self.current_direction = direction
            anim = self.animations.get(new_anim)
            if anim:
                anim.reset()
                anim.play(loop=True)
    
    def get_current_frame(self):
        """Get the current animation frame."""
        anim = self.animations.get(self.current_animation)
        return anim.get_current_frame() if anim else None


class AnimationManager:
    """Manages animations for all players and enemies."""
    
    def __init__(self):
        self.animators = {}
        self.enemy_animators = {}
        self.assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'entities')
    
    def get_or_create_animator(self, player_id):
        """Get or create animator for a player."""
        if player_id not in self.animators:
            self.animators[player_id] = PlayerAnimator(player_id, self.assets_path)
        return self.animators[player_id]
    
    def get_or_create_enemy_animator(self, enemy_id):
        """Get or create animator for an enemy."""
        if enemy_id not in self.enemy_animators:
            self.enemy_animators[enemy_id] = EnemyAnimator(enemy_id, self.assets_path)
        return self.enemy_animators[enemy_id]
    
    def update_local_player(self, player_id, dt, keys_pressed):
        """Update local player animation."""
        animator = self.get_or_create_animator(player_id)
        animator.update(dt, keys_pressed=keys_pressed)
    
    def update_remote_player(self, player_id, dt, pos_x, pos_y):
        """Update remote player animation."""
        animator = self.get_or_create_animator(player_id)
        animator.update(dt, pos_x=pos_x, pos_y=pos_y)
    
    def update_enemy(self, enemy_id, dt, pos_x, pos_y):
        """Update enemy animation."""
        animator = self.get_or_create_enemy_animator(enemy_id)
        animator.update(dt, pos_x=pos_x, pos_y=pos_y)
    
    def remove_player(self, player_id):
        """Remove player animations from memory."""
        if player_id in self.animators:
            del self.animators[player_id]
    
    def remove_enemy(self, enemy_id):
        """Remove enemy animations from memory."""
        if enemy_id in self.enemy_animators:
            del self.enemy_animators[enemy_id]
