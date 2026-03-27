# Nivix Scene Segmenter v0.9.4
# Orchestrates Multi-Phase Timeline IR with Geometry, Text, Math, Groups, and Cinematic Transitions.

class SceneSegmenter:
    """
    Identifies logical boundaries in the animation timeline and segments them
    into a hierarchical 'scenes' array.
    """
    def __init__(self, execution_ir):
        self.ir = execution_ir
        
    def segment(self):
        if "scene" not in self.ir:
            return self.ir
            
        scene_data = self.ir["scene"]
        # Source layers
        objects = scene_data.get("objects", [])
        text_objects = scene_data.get("text_objects", [])
        math_objects = scene_data.get("math_objects", [])
        transforms = scene_data.get("equation_transforms", [])
        group_objects = scene_data.get("group_objects", [])
        transitions = scene_data.get("scene_transitions", [])
        camera_motions = scene_data.get("camera", {}).get("motions", [])
        
        scenes = []
        grouped_scenes = {}
        
        def get_scene(s_id):
            if s_id not in grouped_scenes:
                grouped_scenes[s_id] = {
                    "id": s_id,
                    "objects": [],
                    "text_objects": [],
                    "math_objects": [],
                    "equation_transforms": [],
                    "group_objects": [],
                    "transitions_in": [],
                    "camera": {"motions": []},
                    "background": scene_data.get("background", {"color": "black"}),
                    "timeline": scene_data.get("timeline", {"fps": 30}),
                    "sequence_mode": scene_data.get("sequence_mode", "parallel")
                }
            return grouped_scenes[s_id]

        # Dispatch all actors as normal
        for obj in objects: get_scene(obj.get("scene_id", 0))["objects"].append(obj)
        for txt in text_objects: get_scene(txt.get("scene_id", 0))["text_objects"].append(txt)
        for math in math_objects: get_scene(math.get("scene_id", 0))["math_objects"].append(math)
        for trans in transforms: get_scene(trans.get("scene_id", 0))["equation_transforms"].append(trans)
        for group in group_objects: get_scene(group.get("scene_id", 0))["group_objects"].append(group)
        for motion in camera_motions: get_scene(motion.get("scene_id", 0))["camera"]["motions"].append(motion)
        
        # TRANSITION DISPATCH (v1.7)
        # Transitions bridge 'from' and 'to'. We store them in 'to_scene' as 'transitions_in'.
        for trans in transitions:
             to_sid = trans.get("to_scene")
             get_scene(to_sid)["transitions_in"].append(trans)
            
        # Reconstruct sequence
        for s_id in sorted(grouped_scenes.keys()):
            scenes.append(grouped_scenes[s_id])
            
        return {
            "scenes": scenes if scenes else [scene_data],
            "metadata": self.ir.get("metadata", {})
        }

def segment_scenes(execution_ir):
    return SceneSegmenter(execution_ir).segment()
