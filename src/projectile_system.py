"""
Projectile system for handling shooting mechanics in the multiplayer game.
"""

import math
from game_constants import *


class Projectile:
    def __init__(self, projectile_id, x, y, direction_x, direction_y, owner_id):
        self.id = projectile_id
        self.x = x
        self.y = y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.owner_id = owner_id
        self.lifetime = PROJECTILE_LIFETIME
        
    def update(self):
        """Update projectile position and lifetime."""
        self.x += self.direction_x * PROJECTILE_SPEED
        self.y += self.direction_y * PROJECTILE_SPEED
        self.lifetime -= 1
        
        # Check if projectile is out of bounds or expired
        if (self.x < 0 or self.x > WIDTH or 
            self.y < 0 or self.y > HEIGHT or 
            self.lifetime <= 0):
            return False  # Should be removed
        return True  # Still active
        
    def get_rect(self):
        """Get the projectile's collision rectangle."""
        return (self.x - PROJECTILE_SIZE // 2, 
                self.y - PROJECTILE_SIZE // 2,
                PROJECTILE_SIZE, 
                PROJECTILE_SIZE)


class ProjectileManager:
    def __init__(self):
        self.projectiles = {}  # projectile_id -> Projectile
        self.next_projectile_id = 0
        
    def create_projectile(self, start_x, start_y, direction_x, direction_y, owner_id):
        """Create a new projectile."""
        projectile_id = f"{owner_id}_{self.next_projectile_id}"
        self.next_projectile_id += 1
        
        projectile = Projectile(projectile_id, start_x, start_y, 
                              direction_x, direction_y, owner_id)
        self.projectiles[projectile_id] = projectile
        return projectile
        
    def update_projectiles(self):
        """Update all projectiles and remove expired ones."""
        expired_projectiles = []
        
        for projectile_id, projectile in self.projectiles.items():
            if not projectile.update():
                expired_projectiles.append(projectile_id)
                
        # Remove expired projectiles
        for projectile_id in expired_projectiles:
            del self.projectiles[projectile_id]
            
        return expired_projectiles
        
    def remove_projectile(self, projectile_id):
        """Remove a specific projectile."""
        if projectile_id in self.projectiles:
            del self.projectiles[projectile_id]
            
    def get_all_projectiles(self):
        """Get all active projectiles."""
        return self.projectiles
        
    def clear_projectiles_by_owner(self, owner_id):
        """Remove all projectiles owned by a specific player."""
        to_remove = [pid for pid, p in self.projectiles.items() if p.owner_id == owner_id]
        for pid in to_remove:
            del self.projectiles[pid]
        return to_remove