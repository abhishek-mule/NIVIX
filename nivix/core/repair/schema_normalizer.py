# Nivix Schema Normalization Layer v2
# Handles alias resolution and structural re-mapping of hallucinated LLM keys.

# Common LLM Hallucinated Key -> Nivix Internal Key
SCHEMA_REMAP = {
    # Sequence/Time
    "track": "track_id",
    "lane": "track_id",
    "time": "duration",
    "length": "duration",
    "start": "start_time",
    "begin": "start_time",
    "at": "start_time",
    
    # Motion/Direction
    "upward": "up",
    "downward": "down",
    "leftward": "left",
    "rightward": "right",
    "forwards": "right",
    "backwards": "left",
    "sideways": "right",
    "velocity": "speed",
    "action": "motion",
    "shape": "type"
}

def normalize_keys(scene_dict):
    """
    Recursively descends into the scene dictionary and normalizes hallucinated keys.
    Also handles top-level objects array flattening.
    """
    if isinstance(scene_dict, dict):
        new_dict = {}
        for k, v in scene_dict.items():
            # Apply individual property re-mapping (normalized keys)
            # We map 'upward' to 'up' if it's a value, but here it maps keys.
            normalized_k = SCHEMA_REMAP.get(k.lower(), k)
            # Recurse: Ensure nested objects in arrays are also normalized
            new_dict[normalized_k] = normalize_keys(v)
            
        return new_dict
        
    elif isinstance(scene_dict, list):
        # 3. List traversal for arrays like 'objects'
        return [normalize_keys(item) for item in scene_dict]
        
    elif isinstance(scene_dict, str):
        # Value-level normalization (alias resolution for values)
        # Handle "upward" value if it is used in "motion": "upward"
        return SCHEMA_REMAP.get(scene_dict.lower(), scene_dict)
        
    return scene_dict

def produce_normalized_intent(scene_dict):
    """
    Final Schema Normalization Pass before the validator.
    """
    return normalize_keys(scene_dict)
