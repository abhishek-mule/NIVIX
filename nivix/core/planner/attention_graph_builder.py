# Nivix Attention Graph Builder v2.6
# Viewer Intent Orchestrator: Predicts Gaze Trajectory.

class AttentionGraphBuilder:
    """
    Constructs a timeline of 'Attention Weights' across the narrative.
    Tells the camera where the viewer SHOULD be looking at any given second.
    Consumes: Intent Graph, Object Graph, Transformation Graph.
    """
    
    def predict_attention_trajectory(self, intent_graph, object_graph, transformations):
        """
        Calculates a 'gaze point' timeline for the camera planner.
        Output: List of { time, focus_id, focus_weight, camera_hint }.
        """
        print("--- [NIVIX ATTENTION] Modeling Viewer Gaze Trajectory (v2.6 Architecture) ---")
        
        gaze_timeline = []
        
        # 0. Base Attention (Narrative Scenes)
        for i, node in enumerate(intent_graph["nodes"]):
            # Heuristic: Focus on the Primary Object of each scene
            # (In a real system: we follow the logic flow of the pedagogical goal)
            gaze_event = {
                "scene_id": node["id"],
                "focus_id": f"focus_{i}",
                "priority": node.get("visual_priority", "medium"),
                "dwell_hint": node.get("duration_hint", 3.0),
                "motion_prediction": node.get("camera_strategy")
            }
            gaze_timeline.append(gaze_event)
            
        # 1. Action-Triggered Attention Shifts (v2.6+)
        # If a transformation happens (Square -> Triangle), 
        # the gaze point SHOULD center on the morph even if it's not the 'main' scene object.
        for trans in transformations:
             # Add a higher-priority gaze shift for the duration of the transition
             pass
             
        return gaze_timeline

def build_attention_plan(intent_graph, object_graph, transformations):
    return AttentionGraphBuilder().predict_attention_trajectory(intent_graph, object_graph, transformations)
