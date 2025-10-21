"""
GameObject base class for all game entities.
"""

class GameObject:
    """Base class for all game objects using component-based architecture."""
    
    def __init__(self, x=0, y=0):
        """
        Initialize a game object.
        
        Args:
            x: Initial X position
            y: Initial Y position
        """
        self.x = x
        self.y = y
        self.components = {}
        self.active = True
        self.tags = set()
    
    def add_component(self, component_type, component):
        """
        Add a component to this game object.
        
        Args:
            component_type: Type/class of the component
            component: The component instance
        """
        component.owner = self
        self.components[component_type] = component
        return component
    
    def get_component(self, component_type):
        """
        Get a component by type.
        
        Args:
            component_type: Type/class of the component
            
        Returns:
            The component instance or None
        """
        return self.components.get(component_type)
    
    def has_component(self, component_type):
        """
        Check if this object has a component of the given type.
        
        Args:
            component_type: Type/class of the component
            
        Returns:
            True if the component exists
        """
        return component_type in self.components
    
    def remove_component(self, component_type):
        """
        Remove a component by type.
        
        Args:
            component_type: Type/class of the component
        """
        if component_type in self.components:
            self.components[component_type].destroy()
            del self.components[component_type]
    
    def update(self, dt):
        """
        Update all components.
        
        Args:
            dt: Delta time in milliseconds
        """
        if not self.active:
            return
        
        for component in list(self.components.values()):
            if component.enabled:
                component.update(dt)
    
    def destroy(self):
        """Destroy this game object and all its components."""
        self.active = False
        for component in list(self.components.values()):
            component.destroy()
        self.components.clear()
    
    def add_tag(self, tag):
        """Add a tag to this object for identification."""
        self.tags.add(tag)
    
    def has_tag(self, tag):
        """Check if this object has a specific tag."""
        return tag in self.tags
    
    def remove_tag(self, tag):
        """Remove a tag from this object."""
        self.tags.discard(tag)
