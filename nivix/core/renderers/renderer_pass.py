# Nivix Renderer Pass v1.13
# Coordinates the dispatch of Execution IR to the chosen Renderer Adapter.

def produce_video(execution_graph, renderer_adapter):
    """
    Orchestrator for the final Rendering phase.
    Decouples cross-platform Scene IR from specific Renderer implementation.
    """
    print("\n--- [NIVIX PRODUCER] Dispatching Multi-Phase Execution Graph to Renderer... ---")
    
    # 1. Initialization
    scenes = execution_graph.get("scenes", [])
    if not scenes:
        print("--- [ERROR] Empty Execution Graph. No scenes to render. ---")
        return None
        
    renderer_adapter.setup(execution_graph.get("metadata", {}))
    
    # 2. Multi-Phase Rendering Cycle
    for i, scene in enumerate(scenes):
        print(f"--- [NIVIX PRODUCER] Commencing Scene {i}: {scene.get('id', i)} ---")
        
        # Dispatch Transitions
        for trans in scene.get("transitions_in", []):
            renderer_adapter.render_transition(trans)
        
        # Dispatch Objects
        for obj in scene.get("objects", []): renderer_adapter.render_object(obj)
        for txt in scene.get("text_objects", []): renderer_adapter.render_object(txt)
        for math in scene.get("math_objects", []): renderer_adapter.render_object(math)
        
        # Dispatch Animations/Motions
        # (In a real system, we'd interleave them by start_time)
        for obj in (scene.get("objects", []) + scene.get("text_objects", []) + scene.get("math_objects", [])):
            if obj.get("motion") != "none":
                renderer_adapter.render_animation(obj)
                
        # Dispatch Transitions/Transforms
        for trans in scene.get("equation_transforms", []):
             renderer_adapter.render_animation(trans)
             
        # Dispatch Camera Motions (The NEW v1.12 Layer)
        motions = scene.get("camera", {}).get("motions", [])
        for cm in motions:
            renderer_adapter.render_camera(cm)
            
    # 3. Finalization
    return renderer_adapter.finalize()
