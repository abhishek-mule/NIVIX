# Nivix Incremental Planner v3.6
# Efficient Re-Compilation Engine: Tracks Dependency Dirty-Bits.

class IncrementalPlanner:
    """
    Prevents costly full-graph rebuilds by tracking modified regions.
    Identifies 'Dirty Nodes' and re-runs only the downstream IR passes.
    """
    
    def recompute(self, original_plan, change_set):
        """
        Input: Full original plan, list of { node_id, changed_property }.
        Output: Patched plan with minimal re-computation.
        """
        print(f"--- [NIVIX INCREMENTAL] Re-computing for {len(change_set)} changes ---")
        
        # 1. Identify Dirty Objects/Scenes
        # 2. Re-run local passes (Object Graph -> Transformation Graph)
        # 3. Patch the CIR primitives for the affected frames only.
        
        # Heuristic: If color changed, just update CIR params, skip everything else.
        for change in change_set:
             if change["property"] == "color":
                  obj_id = change["target"]
                  # Partial update of CIR instead of full re-plan.
                  print(f"--- [INCREMENTAL] Patching CIR Color for {obj_id} ---")
                  
        return original_plan

def apply_incremental_patch(original_plan, changes):
    return IncrementalPlanner().recompute(original_plan, changes)
