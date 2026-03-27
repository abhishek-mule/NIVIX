# Nivix Canonical Intermediate Representation (CIR) v2.7
# Standardized Execution Language for the Nivix Compiler.

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

class CIREventType(Enum):
    SPAWN = "spawn"
    FADE = "fade"
    TRANSFORM = "transform"
    MORPH = "morph"
    TRACK = "track"
    ANCHOR = "anchor"
    HIGHLIGHT = "highlight"
    WAIT = "wait"
    # Relational Primitives (v2.9)
    GROUP = "group"
    UNGROUP = "ungroup"
    COMPARE = "compare"
    SEQUENCE = "sequence"
    EMPHASIZE = "emphasize"
    MASK = "mask"
    REVEAL = "reveal"
    # Alignment & Distribution (v3.2 - v3.6)
    ALIGN = "align"
    DISTRIBUTE = "distribute"

@dataclass
class CIREvent:
    event_type: CIREventType
    object_id: str
    start_time: float
    duration: float
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: float = 1.0

@dataclass
class CanonicalIR:
    """
    The stabilized execution blueprint for any Nivix backend.
    Everything upstream compiles to CIR. Everything downstream reads CIR.
    """
    version: str = "2.7"
    objects: List[Dict[str, Any]] = field(default_factory=list)
    timeline: List[CIREvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "version": self.version,
            "objects": self.objects,
            "timeline": [
                {
                    "type": e.event_type.value,
                    "target": e.object_id,
                    "t": e.start_time,
                    "d": e.duration,
                    "params": e.parameters
                } for e in self.timeline
            ],
            "metadata": self.metadata
        }

def create_cir(plan_data):
    """Factory: Normalizes multi-graph plan into a flat CIR."""
    cir = CanonicalIR()
    cir.objects = plan_data.get("global_objects", [])
    # (Mapping logic will expand in the Pass Manager)
    return cir
