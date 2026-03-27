# Nivix Renderer Abstraction Layer v1.13
# Standard Interface for all Renderer Adapters (Manim, Remotion, SVG, etc.)

from abc import ABC, abstractmethod

class BaseRenderer(ABC):
    """
    Abstract Base Class for all Nivix renderers.
    Forces a standard contract so the compiler doesn't need to know implementation details.
    """
    
    @abstractmethod
    def setup(self, scene_metadata):
        """Pre-render configuration (background, FPS, etc.)"""
        pass

    @abstractmethod
    def render_object(self, obj_entry):
        """Converts a Scenegraph Object entry into a renderer-specific primitive."""
        pass

    @abstractmethod
    def render_animation(self, animation_entry):
        """Handles motions/transforms/entrances."""
        pass

    @abstractmethod
    def render_transition(self, transition_entry):
        """Handles cinematic scene transitions (fades, cuts)."""
        pass

    @abstractmethod
    def render_camera(self, camera_entry):
        """Processes semantic camera_actions (pan, zoom, follow)."""
        pass

    @abstractmethod
    def finalize(self):
        """Bake the final video or file."""
        pass
