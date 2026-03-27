# Nivix Object Graph Builder v2.3
# Geometry & Entity Orchestrator: Ensures universal object identity across scenes.

class ObjectGraphBuilder:
    """
    Identifies all physical/mathematical entities required for the lesson.
    Prevents object 'teleportation' or identity mismatch between scenes.
    """
    
    def build_object_graph(self, prompt, intent_graph):
        """
        Extracts entities from the prompt and the planned intent graph.
        Returns: List of canonical objects.
        """
        print(f"--- [NIVIX OBJECTS] Building Global Object Graph for concept: {prompt[:30]} ---")
        
        objects = []
        
        # 1. Heuristic Entity Recognition (Based on Scene Types)
        for node in intent_graph:
            s_type = node.get("scene_type")
            
            if s_type == "equation":
                objects.append({"id": "main_eq", "type": "equation", "persistence": "global"})
            elif s_type == "visualization":
                 objects.append({"id": "main_geo", "type": "geometry", "persistence": "scene_set"})
            elif s_type == "comparison":
                 objects.append({"id": "comp_target_1", "type": "placeholder", "persistence": "ephemeral"})
                 objects.append({"id": "comp_target_2", "type": "placeholder", "persistence": "ephemeral"})
                 
        return objects

def build_objects(prompt, intent_graph):
    return ObjectGraphBuilder().build_object_graph(prompt, intent_graph)
