"""
Component base class for component-based architecture.
"""

class Component:
    """Base class for all components."""
    
    def __init__(self, owner=None):
        """
        Initialize the component.
        
        Args:
            owner: The GameObject that owns this component
        """
        self.owner = owner
        self.enabled = True
    
    def update(self, dt):
        """
        Update the component.
        
        Args:
            dt: Delta time in milliseconds
        """
        if not self.enabled:
            return
    
    def destroy(self):
        """Clean up the component."""
        self.enabled = False
        self.owner = None
