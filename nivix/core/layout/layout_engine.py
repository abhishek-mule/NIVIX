# Nivix Layout Engine v1.0
# Semantic Spatial Reasoning and Collision Avoidance (v1.11).

class LayoutEngine:
    """
    Computes optimal spatial coordinates for all actors in a scene.
    Enforces semantic zones: Titles (Top), Equations (Center), Captions (Bottom).
    """
    def __init__(self, semantic_ir):
        self.ir = semantic_ir
        
    def apply(self):
        if "scene" not in self.ir:
             return self.ir
             
        scene = self.ir["scene"]
        # Layers to Layout
        objects = scene.get("objects", [])
        text_objects = scene.get("text_objects", [])
        math_objects = scene.get("math_objects", [])
        
        print("--- [NIVIX LAYOUT] Semantic Placement & Collision Avoidance Active ---")
        
        # 1. ZONE ASSIGNMENT Logic
        # Titles go to the TOP
        for txt in text_objects:
             if txt.get("style") == "title" or "title" in txt.get("content", "").lower():
                  txt["position"] = [0, 3, 0] # Top Center
             elif txt.get("style") == "caption":
                  txt["position"] = [0, -3, 0] # Bottom Center
             elif "label" in txt.get("style", ""):
                  pass # Labels are usually anchored (handled by renderer next_to)
        
        # 2. COLLISION AVOIDANCE (Primitive)
        # If multiple 'objects' (geometry) exist, spread them horizontally
        # so they don't appear in the same [0,0,0] spot.
        geom_count = 0
        for obj in objects:
             # Default spread: 0, -3, 3, -6, 6...
             offset = (geom_count // 2 + 1) * 3 if geom_count > 0 else 0
             direction = 1 if geom_count % 2 == 1 else -1 if geom_count > 0 else 0
             obj["position"] = [offset * direction, 0, 0]
             geom_count += 1
             
        # 3. MATH FOCUS Center
        # Most math derivations should occur in the vertical center.
        for math in math_objects:
             math["position"] = [0, 0, 0] # Center

        # 4. BOUNDING BOX & FOCUS RESOLVER (v1.12 Camera Pass)
        # Every actor gets a bounding box and a default focus target.
        all_lists = [objects, text_objects, math_objects]
        for actor_list in all_lists:
             for actor in actor_list:
                  # Assign Position if missing
                  pos = actor.get("position", [0,0,0])
                  
                  # Size Heuristics
                  width, height = 2, 2 # Default for geometry
                  if "content" in actor or "equation" in actor: # Text/Math
                       content = actor.get("content", actor.get("equation", ""))
                       width = max(len(content) * 0.4, 2)
                       height = 1.2
                  
                  # Compute Bounding Box: [min_x, min_y, max_x, max_y]
                  actor["bounding_box"] = [
                       pos[0] - width/2, pos[1] - height/2,
                       pos[0] + width/2, pos[1] + height/2
                  ]
                  
                  # Focus Target Resolver: By default, an action focuses on its own actor.
                  actor["focus_target"] = actor.get("id")

        return self.ir

def apply_layout(semantic_ir):
    return LayoutEngine(semantic_ir).apply()
