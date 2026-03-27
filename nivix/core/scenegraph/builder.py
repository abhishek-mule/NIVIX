# Nivix Scene Graph Builder v0.9
# Orchestrates Multi-Phase Scene Graph Construction.

def build(segmented_ir):
    """
    Constructs the final Execution Graph for the Multi-Phase Renderer Adapter.
    Supports both Single-Scene (v0.1-0.8) and Multi-Scene (v0.9) IRs.
    """
    # 1. Structural Resolution: Determine if the IR is segmented or flat.
    scenes = segmented_ir.get("scenes", [])
    
    # 2. Composition
    final_execution_graph = {
        "scenes": scenes,
        "metadata": {
            "diagnostics": segmented_ir.get("metadata", {}).get("diagnostics", {}),
            "compiler_version": "0.9-MultiPhase"
        }
    }
    
    # Backward Compatibility: if scenes is empty, fallback to single 'scene'
    if not scenes and "scene" in segmented_ir:
        final_execution_graph["scenes"] = [segmented_ir["scene"]]
        
    return final_execution_graph
