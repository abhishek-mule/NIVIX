# Nivix IR Lowering Pass
# Strips metadata (confidence, source, diagnostics, etc.) from Semantic IR to produce a clean Execution IR.

def strip_metadata(scene_ir):
    """
    Recursively descends into the Hierarchical IR and extracts only the 'value' fields.
    Also strips diagnostic keys (starting with '_').
    """
    if isinstance(scene_ir, dict):
        # 1. Detection: Confidence Wrapper (dict with 'value' and 'confidence')
        if "value" in scene_ir and ("confidence" in scene_ir or "source" in scene_ir):
            return strip_metadata(scene_ir["value"])
            
        # 2. Key-level Stripping: Remove any key that starts with '_' (e.g., _confidence, _diagnostics)
        return {k: strip_metadata(v) for k, v in scene_ir.items() if not k.startswith("_")}
        
    elif isinstance(scene_ir, list):
        # 3. List traversal for arrays like 'objects' or 'tracks'
        return [strip_metadata(item) for item in scene_ir]
        
    # 4. Base Case: Plain values (int, float, str, bool) remain untouched
    return scene_ir

def produce_execution_ir(semantic_ir):
    """
    The final 'Lowering Pass' before the Scene Graph is handed to the Renderer Adapter.
    """
    return strip_metadata(semantic_ir)
