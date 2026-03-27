# Nivix Backend Capability Matrix v2.8
# Feature Negotiation & Polyfill Orchestrator.

from enum import Enum
from typing import Dict, List, Any

class Feature(Enum):
    SYMBOLIC_MORPH = "morph"
    CAMERA_TRACKING = "track"
    LAYOUT_ANCHORS = "anchor"
    GROUP_TRANSFORMS = "group"
    SYNCHRONOUS_EXECUTION = "sync"

class RendererCapability:
    """Registry of what a backend can support."""
    
    CAPABILITIES = {
        "manim": [
            Feature.SYMBOLIC_MORPH,
            Feature.CAMERA_TRACKING,
            Feature.LAYOUT_ANCHORS,
            Feature.GROUP_TRANSFORMS,
            Feature.SYNCHRONOUS_EXECUTION
        ],
        "remotion": [
            Feature.CAMERA_TRACKING,
            Feature.SYNCHRONOUS_EXECUTION
        ],
        "svg_static": [] # Minimalist
    }

    def can_handle(self, backend: str, feature: Feature) -> bool:
        """Returns True if the backend supports the specified feature."""
        return feature in self.CAPABILITIES.get(backend, [])

    def negotiate_ir(self, backend: str, cir_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rewrites CIR events if the backend lacks required capabilities.
        Example: morph -> [fade_out, fade_in]
        """
        print(f"--- [NIVIX NEGOTIATOR] Negotiating IR for backend: {backend} ---")
        
        negotiated_timeline = []
        for event in cir_plan.get("timeline", []):
            if event["type"] == "morph" and not self.can_handle(backend, Feature.SYMBOLIC_MORPH):
                 # POLYFILL: Morph becomes Fade+Spawn
                 print(f"--- [NEGOTIATOR] Polyfilling Morph for {backend} ---")
                 negotiated_timeline.append({"type": "fade", "target": event["target"], "t": event["t"], "d": event["d"]/2})
                 negotiated_timeline.append({"type": "spawn", "target": event["target"], "t": event["t"] + event["d"]/2, "d": event["d"]/2})
            else:
                 negotiated_timeline.append(event)
                 
        cir_plan["timeline"] = negotiated_timeline
        return cir_plan

def negotiate(backend, cir_plan):
    return RendererCapability().negotiate_ir(backend, cir_plan)
