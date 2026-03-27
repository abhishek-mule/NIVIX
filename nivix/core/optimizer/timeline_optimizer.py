# Nivix Timeline Optimizer v1.3
# Automatic Parallelization and Narrative Compression Pass (v1.9).

class TimelineOptimizer:
    """
    Optimizes the animation storyboard by identifying independent actions.
    Specifically detects parallelizable entrances and synchronized object motions.
    """
    def __init__(self, semantic_ir):
         self.ir = semantic_ir
         
    def optimize(self):
        if "scene" not in self.ir:
             return self.ir
             
        scene = self.ir["scene"]
        # Rule: Sequence Mode Optimization
        # If 'sequential' mode is ON, objects normally wait for the previous step.
        # We can 'parallelize' by marking independent actions to start together.
        
        objects = scene.get("objects", [])
        
        print("--- [NIVIX OPTIMIZER] Narrative Analysis & Parallel Fusion Active ---")
        
        # Identification Pass: Find parallelizable entrance clumps
        if scene.get("sequence_mode") == "sequential":
             print("--- [DEBUG] Performing Automatic Parallelization on Sequential Sequence... ---")
             
             # Any object that just 'appears' (motion=none) and is at the START of the list
             # can be parallelized with other start-appearances.
             # In v1.9 Prototype: We use a heuristic. 
             # Adjacent 'motion:none' blocks of DIFFERENT objects are parallelized.
             
             last_obj_id = None
             for i in range(1, len(objects)):
                  curr = objects[i]; prev = objects[i-1]
                  
                  # If both are 'none' motions and different IDs, they can be merged
                  if curr.get("motion") == "none" and prev.get("motion") == "none":
                       if curr.get("id") != prev.get("id"):
                            print(f"--- [OPTIMIZER] Fusing entrances for {prev.get('id')} and {curr.get('id')} ---")
                            # By setting '_no_seq_wait' = True, we tell the scheduler to skip 
                            # the implicit dependency on 'last_global_node'.
                            curr["_no_seq_wait"] = True

                  # If both are motions of DIFFERENT objects, they are parallelizable 
                  # (UNLESS the user prompt explicitly said 'then').
                  # Since the intent arrived from the LLM, we assume if they are adjacent
                  # but have DIFFERENT IDs, the engine can suggest parallelization.
                  if curr.get("motion") != "none" and prev.get("motion") != "none":
                       if curr.get("id") != prev.get("id"):
                            print(f"--- [OPTIMIZER] Parallelizing motions for {prev.get('id')} and {curr.get('id')} ---")
                            curr["_no_seq_wait"] = True

        return self.ir

def optimize_timeline(semantic_ir):
    return TimelineOptimizer(semantic_ir).optimize()
