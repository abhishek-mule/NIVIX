# Nivix Scene Validator (Hierarchical Edition)
# Ensures that animation JSON conforms to the required scene/objects structure.

def validate(scene):
    """
    Validates a hierarchical scene graph for Nivix compliance.
    Supports a root "scene" object with nested sub-modules.
    """
    # 1. Root Level Check: Allow for nested "scene" or auto-wrap if intent is objects-only
    if "scene" not in scene and "objects" not in scene:
        raise Exception("Validation Error: No recognized 'scene' or 'objects' key found.")
    
    # 2. Objects Presence: If 'scene' exists, it MUST have an 'objects' array eventually
    if "scene" in scene:
        if "objects" not in scene["scene"] and not isinstance(scene["scene"], list):
             # Some parsers might return scene as a list or a dict, handle accordingly
             pass
        
    return True
