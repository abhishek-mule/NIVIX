# Nivix Default Policy Engine
# Ensures all levels of the hierarchical scene graph have deterministic states.

# Global Defaults for Scene Modules (Hierarchical & Scalable)
SCENE_DEFAULTS = {
    # 1. Advanced Camera IR (Position + Target + Zoom)
    "camera": {
        "type": "orthographic",
        "position": [0, 0, 10],   # Z=10 for standard Manim view
        "target": [0, 0, 0],     # Focus on world origin
        "zoom": 1.0,
        "projection": "perspective_off"
    },
    # 2. Track-based Timeline Logic
    "timeline": {
        "duration": 5.0,
        "fps": 30,
        "tracks": []             # Future: multi-parallel track support
    },
    "background": {
        "color": "black"
    }
}

# Object Defaults for Animation States (Confidence-Wrapped)
OBJECT_DEFAULTS = {
    "motion": {"value": "none", "confidence": 1.0, "source": "policy_default"},
    "duration": {"value": 1.0, "confidence": 1.0, "source": "policy_default"},
    "color": {"value": "white", "confidence": 1.0, "source": "policy_default"},
    "scale": {"value": 1.0, "confidence": 1.0, "source": "policy_default"},
    "track_id": {"value": 0, "confidence": 1.0, "source": "policy_default"} # Essential for parallel sync
}

def apply_defaults(scene):
    """
    Applies global default policies to the hierarchical Nivix scene graph.
    This stage also aggregates confidence scores for diagnostics.
    """
    # 1. Root Level Validation (Hierarchy Enforcement)
    if "scene" not in scene:
        scene = {"scene": scene}
        
    # 2. Module Defaults (Camera, Timeline, Background)
    for module, default_data in SCENE_DEFAULTS.items():
        if module not in scene["scene"]:
            scene["scene"][module] = default_data.copy()
        else:
            # If the module exists, deep-fill sub-fields
            for k, v in default_data.items():
                if k not in scene["scene"][module]:
                    scene["scene"][module][k] = v
                    
    # 3. Object-Level Defaults & Wrap Confidence
    if "objects" not in scene["scene"]:
        scene["scene"]["objects"] = []
        
    # Aggregate scene-level confidence tracking
    scene_conf_sum = 0
    obj_count = 0
        
    for obj in scene["scene"]["objects"]:
        obj_conf_sum = 0
        trait_count = 0
        
        # Fill in missing properties from OBJECT_DEFAULTS
        for key, default_wrapper in OBJECT_DEFAULTS.items():
            if key not in obj:
                obj[key] = default_wrapper.copy()
            elif not isinstance(obj[key], dict) or "value" not in obj[key]:
                # Wrap existing raw values from parser in a confidence object
                obj[key] = {
                    "value": obj[key],
                    "confidence": 0.9,
                    "source": "intent_extraction"
                }
            
            # Aggregate object-level confidence
            obj_conf_sum += obj[key].get("confidence", 0.9)
            trait_count += 1
                
        # Calculate Object-Level Aggregate Confidence
        obj["_confidence"] = obj_conf_sum / max(trait_count, 1)
        scene_conf_sum += obj["_confidence"]
        obj_count += 1
        
        # Internal consistency: lowercase strings (recursive)
        _recursively_lowercase(obj)
        
    # 4. Final Scene-Level Confidence Metadata (Invisible to Renderer)
    scene["_diagnostics"] = {
        "aggregate_confidence": scene_conf_sum / max(obj_count, 1),
        "intent_source": "hybrid_compiler"
    }
                
    return scene

def _recursively_lowercase(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "value" and isinstance(v, str):
                data[k] = v.lower()
            elif isinstance(v, (dict, list)):
                _recursively_lowercase(v)
    elif isinstance(data, list):
        for itm in data:
            _recursively_lowercase(itm)
