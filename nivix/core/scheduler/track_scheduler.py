# Nivix Track Scheduler Engine v2.15
# Performance-Aware Orchestration with Hierarchy and CINEMATIC Transitions (v1.7/v1.9).

from nivix.core.scheduler.temporal_graph import TemporalGraph
from nivix.core.scheduler.conflict_detector import ConflictDetector, TemporalDependencyCycleError

def _unwrap(val):
    if isinstance(val, dict) and "value" in val: return val["value"]
    return val

def schedule_tracks(semantic_ir):
    """
    Unified Orchestrator for cinematic storyboards (v1.7).
    Now respects Optimizer Hints (_no_seq_wait) for Automatic Parallelization (v1.9).
    """
    if "scene" not in semantic_ir: return semantic_ir
        
    scene_data = semantic_ir["scene"]
    objects = scene_data.get("objects", [])
    text_objects = scene_data.get("text_objects", [])
    math_objects = scene_data.get("math_objects", [])
    group_objects = scene_data.get("group_objects", [])
    transforms = scene_data.get("equation_transforms", [])
    transitions = scene_data.get("scene_transitions", [])
    camera_motions = scene_data.get("camera", {}).get("motions", [])
    
    sequence_mode = _unwrap(scene_data.get("sequence_mode", "parallel"))
    
    dag = TemporalGraph()
    id_to_node = {} # actor_id -> node_id
    last_global_node = None 
    last_node_by_scene = {} # scene_id -> last node ID
    
    # 1. Collection (v1.12 Global Interleave)
    all_actors = []
    global_sid = 0
    
    # We collect them in a specific priority order to ensure scene breaks are caught
    all_lists = [
        (objects, "geo"), (text_objects, "txt"), (math_objects, "math"),
        (group_objects, "grp"), (transforms, "trans"), (camera_motions, "cam")
    ]
    
    for alist, prefix in all_lists:
        for i, a in enumerate(alist):
             # Note: If multiple lists have _trigger_new_scene, they should ideally 
             # be synchronized. For now, we increment global_sid.
             if _unwrap(a.get("_trigger_new_scene")): 
                  global_sid += 1
             a["scene_id"] = global_sid
             a["_type"] = prefix
             a["_idx"] = i
             all_actors.append(a)
    
    # Sort actors by Scene ID first
    all_actors.sort(key=lambda x: x["scene_id"])

    # --- PHASE 1: Registration (Performance-Aware Order) ---
    for i, actor in enumerate(all_actors):
        actor_id = _unwrap(actor.get("id", f"{actor['_type']}_{i}"))
        node_id = f"{actor['_type']}_{actor_id}_{i}"
        dag.add_node(node_id, duration=float(_unwrap(actor.get("duration", 1.0))))
        
        # 1. Intra-Scene: Structural / Relational
        for m_id in _unwrap(actor.get("members", [])):
             if m_id in id_to_node: dag.add_edge(id_to_node[m_id], node_id)
        
        anchor_id = _unwrap(actor.get("anchor_to"))
        if anchor_id and anchor_id in id_to_node: dag.add_edge(id_to_node[anchor_id], node_id)
        
        source_id = _unwrap(actor.get("source_id"))
        if source_id and source_id in id_to_node: dag.add_edge(id_to_node[source_id], node_id)

        # 2. Sequential / Narrative Logic (Optimized v1.9)
        # Rule: Sequence chaining is skipped if the Optimizer gave a _no_seq_wait hint.
        if sequence_mode == "sequential" and last_global_node and not actor.get("_no_seq_wait"):
             dag.add_edge(last_global_node, node_id)
        
        # Identity Persistence (A node waits for the previous version of itself)
        if actor_id in id_to_node:
             dag.add_edge(id_to_node[actor_id], node_id)

        # Update State
        id_to_node[actor_id] = node_id
        actor["_node_id"] = node_id
        # Wait! If this node was parallelized (no_seq_wait), 
        # should it update last_global_node?
        # Sequential mode says THE ENTIRE ROW follows the previous one. 
        # If A + B are fused, C follows both. 
        # So we update last_global_node to include both (but here I'll just track the chain).
        if not actor.get("_no_seq_wait"):
             last_global_node = node_id
             
        last_node_by_scene[actor["scene_id"]] = node_id

    # --- PHASE 2: Transitions & Boundary Cleanup ---
    for i, trans in enumerate(transitions):
         tn_id = f"trans_{i}"
         trans["_node_id"] = tn_id
         dag.add_node(tn_id, duration=float(_unwrap(trans.get("duration", 1.0))))
         # Boundary constraint: Transition follows the last node of from_scene
         fs = _unwrap(trans.get("from_scene"))
         if fs in last_node_by_scene: dag.add_edge(last_node_by_scene[fs], tn_id)
         
         # All actors in target scene follow transition
         ts = _unwrap(trans.get("to_scene"))
         for a in all_actors:
              if a["scene_id"] == ts:
                   # SPECIAL v1.12: If this is a camera move synced with transition,
                   # it should follow the SAME source as the transition (not the transition itself).
                   if a["_type"] == "cam" and a.get("_sync_with_transition"):
                        if fs in last_node_by_scene: 
                             dag.add_edge(last_node_by_scene[fs], a["_node_id"])
                             # Also, force the camera move duration to match the transition
                             dag.nodes[a["_node_id"]]["duration"] = dag.nodes[tn_id]["duration"]
                   else:
                        dag.add_edge(tn_id, a["_node_id"])

    # --- PHASE 3: Validation & Injection ---
    detector = ConflictDetector(dag.nodes, dag.edges)
    try: detector.validate()
    except TemporalDependencyCycleError as e: raise Exception(f"Animation Orchestration Error: {e}")
            
    schedule = dag.get_schedule()
    for a in all_actors:
         a["start_time"] = schedule[a["_node_id"]]["start_time"]
         a["track_id"] = {"geo": 0, "txt": 1, "math": 2, "grp": 3, "trans": 2, "cam": -1}.get(a["_type"], 0)
    for trans in transitions: 
         trans["start_time"] = schedule[trans.get("_node_id", "T")]["start_time"]
    
    return semantic_ir
