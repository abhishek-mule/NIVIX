# Nivix Adapter Interface v4.0
# Universal contract for all renderer adapters (Remotion, Shotstack, Manim, etc.)

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json

class NivixAdapter(ABC):
    """
    Universal Adapter Interface for Nivix v4.0
    
    Contract: CIR (Canonical Intermediate Representation) -> Renderer-Specific JSON -> MP4
    
    Adapters are interchangeable. The compiler doesn't know or care which renderer is used.
    This inverts the dependency: renderers depend on CIR, not the other way around.
    """
    
    @abstractmethod
    def supports(self, capability: str) -> bool:
        """Check if adapter supports a specific capability."""
        pass
    
    @abstractmethod
    def to_renderer_format(self, cir: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Nivix CIR to renderer-specific JSON format."""
        pass
    
    @abstractmethod
    def export(self, cir: Dict[str, Any], output_path: str, options: Optional[Dict] = None) -> str:
        """Export CIR to MP4. Returns path to rendered video."""
        pass
    
    @abstractmethod
    def validate_cir(self, cir: Dict[str, Any]) -> bool:
        """Validate CIR conforms to schema before rendering."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return list of supported capabilities."""
        return []

class AdapterRegistry:
    """
    Registry for Nivix adapters. Allows dynamic loading of renderers.
    """
    
    _adapters: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, adapter_class: type):
        """Register an adapter by name."""
        cls._adapters[name] = adapter_class
    
    @classmethod
    def get(cls, name: str) -> Optional[type]:
        """Get adapter class by name."""
        return cls._adapters.get(name)
    
    @classmethod
    def list_adapters(cls) -> List[str]:
        """List all registered adapter names."""
        return list(cls._adapters.keys())

def create_adapter(adapter_name: str, cir: Dict[str, Any]) -> Optional[NivixAdapter]:
    """Factory function to create adapter instances."""
    adapter_class = AdapterRegistry.get(adapter_name.lower())
    if adapter_class:
        return adapter_class(cir)
    return None

def discover_adapters():
    """Auto-discover and register all available adapters."""
    try:
        from .shotstack_adapter import ShotstackAdapter
        AdapterRegistry.register("shotstack", ShotstackAdapter)
    except ImportError:
        pass
    
    try:
        from .remotion_adapter import RemotionAdapter
        AdapterRegistry.register("remotion", RemotionAdapter)
    except ImportError:
        pass
    
    try:
        from nivix.renderers.manim_adapter.manim_adapter import ManimAdapter
        AdapterRegistry.register("manim", ManimAdapter)
    except ImportError:
        pass