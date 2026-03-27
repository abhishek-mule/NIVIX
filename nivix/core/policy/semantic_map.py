# Nivix Semantic Mapping Engine (Adaptive Lowering)
# Normalizes natural language descriptors into renderer-ready parameters with confidence tracking.

# Natural language adjective -> numerical mapping
SIZE_MAP = {
    "tiny": 0.25,
    "small": 0.5,
    "medium": 1.0,
    "normal": 1.0,
    "big": 2.0,
    "large": 2.0,
    "huge": 3.0,
    "massive": 4.0
}

# Speed descriptors -> velocity multiplier
SPEED_MAP = {
    "very slow": 0.25,
    "slow": 0.5,
    "medium": 1.0,
    "fast": 2.0,
    "very fast": 3.0,
    "blazing": 5.0
}

# Semantic direction synonyms -> normalized internal constants
DIRECTION_MAP = {
    "right": "right",
    "east": "right",
    "forward": "right",
    "left": "left",
    "west": "left",
    "back": "left",
    "up": "up",
    "north": "up",
    "down": "down",
    "south": "down"
}

def normalize_semantics(scene):
    """
    Lowering stage: Converts complex semantic adjectives into normalized parameters.
    Implements Adaptive Compiler Thinking with confidence tagging.
    """
    if "scene" not in scene or "objects" not in scene["scene"]:
        return scene
        
    for obj in scene["scene"]["objects"]:
        # 1. Normalize Size -> Scale
        if "size" in obj:
            adjective = obj["size"].lower()
            value = SIZE_MAP.get(adjective, 1.0)
            obj["scale"] = {
                "value": value,
                "confidence": 0.95 if adjective in SIZE_MAP else 0.5,
                "source": "semantic_map"
            }
            del obj["size"]
            
        # 2. Normalize Speed -> Velocity Multiplier
        if "speed" in obj:
            adjective = obj["speed"].lower()
            value = SPEED_MAP.get(adjective, 1.0)
            obj["speed_multiplier"] = {
                "value": value,
                "confidence": 0.95 if adjective in SPEED_MAP else 0.5,
                "source": "semantic_map"
            }
            del obj["speed"]
            
        # 3. Normalize Motion Synonyms
        if "motion" in obj:
            current_motion = obj["motion"].lower()
            normalized = DIRECTION_MAP.get(current_motion, current_motion)
            obj["motion"] = {
                "value": normalized,
                "confidence": 0.98 if current_motion in DIRECTION_MAP else 0.7,
                "source": "direction_map"
            }
                
    return scene
