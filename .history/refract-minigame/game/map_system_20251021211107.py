import pygame
import json
import os
from game_constants import TILE_WIDTH, TILE_HEIGHT, WALL_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT


class TileSprite:
    def __init__(self, json_path, image_path):
        self.surface = None
        self.width = TILE_WIDTH
        self.height = TILE_HEIGHT
        self._load_tile(json_path, image_path)
    
    def _load_tile(self, json_path, image_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            sprite_sheet = pygame.image.load(image_path)
            try:
                sprite_sheet = sprite_sheet.convert_alpha()
            except pygame.error:
                pass
            
            if data['frames']:
                frame_info = data['frames'][0]['frame']
                self.width = frame_info['w']
                self.height = frame_info['h']
                
                self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                self.surface.blit(sprite_sheet, (0, 0), 
                                (frame_info['x'], frame_info['y'], 
                                 frame_info['w'], frame_info['h']))
        except Exception as e:
            print(f"Error loading tile: {e}")
            self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.surface.fill((255, 0, 255))


class MapRenderer:
    def __init__(self):
        self.tiles = {}
        self.floor_tiles = []
        self.wall_tiles = []
        self.wall_rects = []
        self.assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'map')
        self._load_tiles()
        self._generate_map()
    
    def _load_tiles(self):
        tile_names = ['floor', 't_wall', 'd_wall', 'l_wall', 'r_wall', 
                     'tl_corner', 'tr_corner', 'dl_corner', 'dr_corner']
        
        for name in tile_names:
            json_path = os.path.join(self.assets_path, f'{name}.json')
            png_path = os.path.join(self.assets_path, f'{name}.png')
            
            if os.path.exists(json_path) and os.path.exists(png_path):
                self.tiles[name] = TileSprite(json_path, png_path)
    
    def _generate_map(self):
        if 'floor' not in self.tiles:
            return
        
        floor = self.tiles['floor']
        
        rows = (WORLD_HEIGHT // TILE_HEIGHT) + 1
        cols = (WORLD_WIDTH // TILE_WIDTH) + 1
        
        for row in range(rows):
            for col in range(cols):
                x = col * TILE_WIDTH
                y = row * TILE_HEIGHT
                self.floor_tiles.append((x, y, 'floor'))
        
        wall_row_top = 0
        wall_row_bottom = rows - 1
        wall_col_left = 0
        wall_col_right = cols - 1
        
        for col in range(cols):
            x = col * TILE_WIDTH
            self.wall_tiles.append((x, 0, 't_wall'))
            self.wall_tiles.append((x, wall_row_bottom * TILE_HEIGHT, 'd_wall'))
            self.wall_rects.append(pygame.Rect(x, 0, TILE_WIDTH, WALL_HEIGHT))
            self.wall_rects.append(pygame.Rect(x, wall_row_bottom * TILE_HEIGHT, TILE_WIDTH, WALL_HEIGHT))
        
        for row in range(rows):
            y = row * TILE_HEIGHT
            self.wall_tiles.append((0, y, 'l_wall'))
            self.wall_tiles.append((wall_col_right * TILE_WIDTH, y, 'r_wall'))
            self.wall_rects.append(pygame.Rect(0, y, TILE_WIDTH, TILE_HEIGHT))
            self.wall_rects.append(pygame.Rect(wall_col_right * TILE_WIDTH, y, TILE_WIDTH, TILE_HEIGHT))
        
        self.wall_tiles.append((0, 0, 'tl_corner'))
        self.wall_tiles.append((wall_col_right * TILE_WIDTH, 0, 'tr_corner'))
        self.wall_tiles.append((0, wall_row_bottom * TILE_HEIGHT, 'dl_corner'))
        self.wall_tiles.append((wall_col_right * TILE_WIDTH, wall_row_bottom * TILE_HEIGHT, 'dr_corner'))
    
    def render(self, surface, camera_x, camera_y):
        for x, y, tile_name in self.floor_tiles:
            screen_x = int(x - camera_x)
            screen_y = int(y - camera_y)
            
            if -TILE_WIDTH <= screen_x <= surface.get_width() and -TILE_HEIGHT <= screen_y <= surface.get_height():
                tile = self.tiles.get(tile_name)
                if tile and tile.surface:
                    surface.blit(tile.surface, (screen_x, screen_y))
        
        for x, y, tile_name in self.wall_tiles:
            screen_x = int(x - camera_x)
            screen_y = int(y - camera_y)
            
            if -TILE_WIDTH <= screen_x <= surface.get_width() and -TILE_HEIGHT <= screen_y <= surface.get_height():
                tile = self.tiles.get(tile_name)
                if tile and tile.surface:
                    surface.blit(tile.surface, (screen_x, screen_y))
    
    def check_wall_collision(self, rect):
        for wall_rect in self.wall_rects:
            if rect.colliderect(wall_rect):
                return True
        return False
