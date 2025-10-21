"""
Game state management.
"""

class GameState:
    """Manages the current game state and all game objects."""
    
    def __init__(self):
        """Initialize the game state."""
        self.game_objects = []
        self.player_id = None
        self.player_object = None
        self.other_players = {}  # player_id -> GameObject mapping
        self.projectiles = {}  # projectile_id -> GameObject mapping
        self.connected = False
    
    def add_object(self, game_object):
        """
        Add a game object to the state.
        
        Args:
            game_object: GameObject instance to add
        """
        self.game_objects.append(game_object)
        return game_object
    
    def remove_object(self, game_object):
        """
        Remove a game object from the state.
        
        Args:
            game_object: GameObject instance to remove
        """
        if game_object in self.game_objects:
            game_object.destroy()
            self.game_objects.remove(game_object)
    
    def get_objects_with_tag(self, tag):
        """
        Get all objects with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of GameObjects with the tag
        """
        return [obj for obj in self.game_objects if obj.has_tag(tag) and obj.active]
    
    def get_objects_with_component(self, component_type):
        """
        Get all objects that have a specific component.
        
        Args:
            component_type: Type of component to search for
            
        Returns:
            List of GameObjects with the component
        """
        return [obj for obj in self.game_objects 
                if obj.has_component(component_type) and obj.active]
    
    def update(self, dt):
        """
        Update all game objects.
        
        Args:
            dt: Delta time in milliseconds
        """
        # Update all active objects
        for obj in list(self.game_objects):
            if obj.active:
                obj.update(dt)
        
        # Clean up destroyed objects
        self.game_objects = [obj for obj in self.game_objects if obj.active]
    
    def clear(self):
        """Clear all game objects."""
        for obj in list(self.game_objects):
            obj.destroy()
        self.game_objects.clear()
        self.other_players.clear()
        self.projectiles.clear()
