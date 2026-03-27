# Priority Map for Attention-Driven Framing (v1.12+)
PRIORITY_MAP = {
    "title": 100,
    "equation": 90,
    "graph": 80,
    "label": 40,
    "geometry": 30
}

class CameraEngine:
    """
    Computes camera keyframes based on the focus targets determined by the Layout Engine.
    Operates on the Semantic IR before Scheduling.
    """
    def __init__(self, semantic_ir):
        self.ir = semantic_ir
        
    def _get_priority(self, actor):
        # Default priority based on style or type
        if actor.get("style") == "title": return PRIORITY_MAP["title"]
        if "equation" in actor: return PRIORITY_MAP["equation"]
        if actor.get("type") == "graph": return PRIORITY_MAP["graph"]
        if "label" in actor.get("style", ""): return PRIORITY_MAP["label"]
        return PRIORITY_MAP["geometry"]

    def apply(self):
        if "scene" not in self.ir:
             return self.ir
             
        scene = self.ir["scene"]
        # Layers for Focus Tracking
        objects = scene.get("objects", [])
        text_objects = scene.get("text_objects", [])
        math_objects = scene.get("math_objects", [])
        group_objects = scene.get("group_objects", [])
        
        # 1. COMPUTE GROUP BOUNDING BOXES
        id_to_actor = {a.get("id"): a for a in (objects + text_objects + math_objects)}
        for grp in group_objects:
             members = grp.get("members", [])
             if not members:
                  grp["bounding_box"] = [0, 0, 0, 0]
                  continue
             
             min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
             for m_id in members:
                  if m_id in id_to_actor:
                       bbox = id_to_actor[m_id].get("bounding_box", [0,0,0,0])
                       min_x = min(min_x, bbox[0]); min_y = min(min_y, bbox[1])
                       max_x = max(max_x, bbox[2]); max_y = max(max_y, bbox[3])
             
             grp["bounding_box"] = [min_x, min_y, max_x, max_y]
             grp["focus_target"] = grp.get("id")

        # 2. SEQUENCE ANALYZER (Interleaved Priority Pass)
        # Instead of just going list-by-list, we look at the 'intent' Order.
        # For v1.13 prototype, we use the merged list.
        all_actors = objects + text_objects + math_objects + group_objects
        
        motions = []
        current_focus_id = None
        current_bbox = [-7, -4, 7, 4] # Standard Viewport
        visible_ids = set()
        
        print("--- [NIVIX CAMERA] Priority-Based Attention Analysis Active ---")
        
        for action in all_actors:
             visible_ids.add(action.get("id"))
             
             # FIND HIGHEST PRIORITY VISIBLE FOCUS
             # We want the camera to focus on the 'most important' thing currently appearing.
             candidates = [id_to_actor.get(vid) for vid in visible_ids if vid in id_to_actor]
             candidates += [g for g in group_objects if g.get("id") in visible_ids]
             candidates = [c for c in candidates if c]
             
             if not candidates: continue
             
             # Resolve focus: action itself has priority, but check if something higher exists
             # RECENCY BONUS: The current action object gets a small priority boost 
             # to ensure the camera tracks the narrative flow.
             def get_score(actor):
                  score = self._get_priority(actor)
                  if actor.get("id") == action.get("id"):
                       score += 15 # Narrative Recency Bonus
                  return score

             best_target = max(candidates, key=lambda x: get_score(x))
             target_id = best_target.get("id")
             target_bbox = best_target.get("bounding_box")
             
             # 3. DELTA CAMERA LOGIC (v1.13)
             # Should we move?
             if target_id != current_focus_id:
                  # Compute Delta
                  cp = [(current_bbox[0]+current_bbox[2])/2, (current_bbox[1]+current_bbox[3])/2]
                  tp = [(target_bbox[0]+target_bbox[2])/2, (target_bbox[1]+target_bbox[3])/2]
                  dist = ((tp[0]-cp[0])**2 + (tp[1]-cp[1])**2)**0.5
                  
                  area_prev = (current_bbox[2]-current_bbox[0]) * (current_bbox[3]-current_bbox[1])
                  area_curr = (target_bbox[2]-target_bbox[0]) * (target_bbox[3]-target_bbox[1])
                  area_delta = abs(area_curr - area_prev) / max(area_prev, 0.001)
                  
                  # DEAD-ZONE / STAY STATIC Logic:
                  # If move is tiny and area change is negligible, skip.
                  if dist < 0.5 and area_delta < 0.1:
                       print(f"--- [DEBUG] Camera skipping move to {target_id} (Delta too small) ---")
                       continue

                  # Determine style
                  style = "pan" if area_delta < 0.3 else "zoom"
                  
                  # 4. CANONICAL CAMERA IR SCHEMA
                  motion = {
                       "type": "camera_move",
                       "style": style,
                       "target": target_id,
                       "anchor_to": target_id,
                       "duration": 1.5,
                       "easing": "smooth",
                       "bounding_box": target_bbox
                  }
                  
                  if best_target.get("_trigger_new_scene"):
                       motion["_sync_with_transition"] = True
                  
                  motions.append(motion)
                  current_focus_id = target_id
                  current_bbox = target_bbox
        
        if "camera" not in scene: scene["camera"] = {}
        scene["camera"]["motions"] = motions
        return self.ir

def apply_camera(semantic_ir):
    return CameraEngine(semantic_ir).apply()
