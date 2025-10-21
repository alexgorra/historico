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
            # Load JSON data
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Load sprite sheet image (don't convert if display not initialized)
            sprite_sheet = pygame.image.load(image_path)
            try:
                sprite_sheet = sprite_sheet.convert_alpha()
            except pygame.error:
                # Display not initialized yet, convert later
                pass
            
            # Extract frames from sprite sheet
            for frame_data in data['frames']:
                frame_info = frame_data['frame']
                duration = frame_data['duration']
                
                # Create surface for this frame
                frame_surface = pygame.Surface((frame_info['w'], frame_info['h']), pygame.SRCALPHA)
                frame_surface.blit(sprite_sheet, (0, 0), 
                                 (frame_info['x'], frame_info['y'], 
                                  frame_info['w'], frame_info['h']))
                
                self.frames.append({
                    'surface': frame_surface,
                    'duration': duration,  # Duration in milliseconds
                    'width': frame_info['w'],
                    'height': frame_info['h']
                })
            
            print(f"Loaded {len(self.frames)} animation frames from {json_path}")
            
        except Exception as e:
            print(f"Error loading animation: {e}")
            # Create a fallback single frame
            fallback_surface = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            fallback_surface.fill((255, 0, 255))  # Magenta for visibility
            self.frames = [{
                'surface': fallback_surface,
                'duration': 150,
                'width': PLAYER_SIZE,
                'height': PLAYER_SIZE
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
            return (PLAYER_SIZE, PLAYER_SIZE)
        current_frame_data = self.frames[self.current_frame]
        return (current_frame_data['width'], current_frame_data['height'])


class AnimationManager:
    """Manages animations for all players."""
    
    def __init__(self):
        """Initialize the animation manager."""
        self.player_animations = {}  # player_id -> animation data
        self.assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    
    def get_player_animation(self, player_id, direction='f'):
        """
        Get or create animation for a player.
        
        Args:
            player_id: Player identifier
            direction: Direction character ('f', 'b', 'l', 'r')
        """
        if player_id not in self.player_animations:
            self.player_animations[player_id] = {
                'current_direction': direction,
                'animations': {}
            }
        
        player_data = self.player_animations[player_id]
        
        # Load animation for this direction if not already loaded
        if direction not in player_data['animations']:
            anim = self._load_direction_animation(direction)
            if anim:
                player_data['animations'][direction] = anim
        
        return player_data['animations'].get(direction)
    
    def _load_direction_animation(self, direction):
        """Load animation for a specific direction."""
        try:
            json_file = f'{direction}_walk.json'
            png_file = f'{direction}_walk.png'
            
            json_path = os.path.join(self.assets_path, json_file)
            png_path = os.path.join(self.assets_path, png_file)
            
            if os.path.exists(json_path) and os.path.exists(png_path):
                anim = AsepriteAnimation(json_path, png_path)
                anim.play(loop=True)
                return anim
        except Exception as e:
            print(f"Error loading {direction} animation: {e}")
        
        return None
    
    def get_idle_animation(self, player_id):
        """Get idle animation for a player."""
        try:
            json_path = os.path.join(self.assets_path, 'f_idle.json')
            png_path = os.path.join(self.assets_path, 'f_idle.png')
            
            if os.path.exists(json_path) and os.path.exists(png_path):
                anim = AsepriteAnimation(json_path, png_path)
                anim.play(loop=True)
                return anim
        except Exception as e:
            print(f"Error loading idle animation: {e}")
        
        return None
    
    def remove_player(self, player_id):
        """Remove player animations from memory."""
        if player_id in self.player_animations:
            del self.player_animations[player_id]
