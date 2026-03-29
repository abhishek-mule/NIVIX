# NIVIX - Animation & Visualization System
# Main Execution Engine and Pipeline Coordinator

import json
from nivix.core.parser.parser import parse_prompt
from nivix.core.planner.semantic_planner import plan_intent
from nivix.core.repair.json_fixer import safe_parse
from nivix.core.repair.schema_normalizer import produce_normalized_intent
from nivix.core.validator.validator import validate
from nivix.core.policy.semantic_map import normalize_semantics
from nivix.core.policy.defaults import apply_defaults
from nivix.core.ir.lowering_pass import produce_execution_ir
from nivix.core.scheduler.track_scheduler import schedule_tracks
from nivix.core.compiler.scene_segmenter import segment_scenes
from nivix.core.optimizer.timeline_optimizer import optimize_timeline
from nivix.core.layout.layout_engine import apply_layout
from nivix.core.camera.camera_engine import apply_camera
from nivix.core.scenegraph.builder import build
from nivix.core.renderers.renderer_pass import produce_video
from nivix.renderers.manim_adapter.manim_adapter import ManimAdapter

def nivix_pipeline():
    """
    Main entry point for the Nivix animation pipeline.
    Connects Natural Language -> Temporal DAG -> Multi-Scene Segmentation -> IR Lowering -> Build.
    """
    print("\n--- Welcome to NIVIX Pipeline v0.9 [Multi-Phase Segmentation] ---")
    
    # Step 1: Input Prompt
    prompt = input("Enter animation prompt: ")
    
    # Step 2: SEMANTIC PLANNING (v2.0 Strategy Layer)
    # Decomposes high-level intent into a pedagogical sequence.
    print("\n--- [NIVIX STRATEGY] Pedagogical Planning engine active... ---")
    semantic_plan = plan_intent(prompt)
    
    # Step 3: Intent Extraction (Plan to IR)
    print("\n--- Parsing Plan into Animation DSL... ---")
    raw_response = parse_prompt(semantic_plan)
    
    # Step 4: JSON REPAIR & Normalization
    print("--- Executing JSON Syntax Repair & Schema Normalization... ---")
    scene_json = safe_parse(raw_response)
    normalized_intent = produce_normalized_intent(scene_json)
    
    # Step 4: Validation
    validate(normalized_intent)
    
    # Step 5: Semantic Normalization
    print("--- Normalizing Semantics with Confidence Tagging... ---")
    semantic_ir = normalize_semantics(normalized_intent)
    
    # Step 6: Default Policies (Hierarchy)
    print("--- Applying Default Policies & Hierarchy Mapping... ---")
    full_semantic_ir = apply_defaults(semantic_ir)
    
    # Step 7: TIMELINE OPTIMIZER (v1.9 Performance Pass)
    # Identifies parallelization opportunities and compresses idle gaps.
    print("--- [NIVIX OPTIMIZER] Timeline Compression & Parallel Fusion active ---")
    optimized_ir = optimize_timeline(full_semantic_ir)
    
    # Step 8: LAYOUT ENGINE (v1.11 Spatial Pass)
    # Enforces semantic zones and collision avoidance.
    print("--- [NIVIX LAYOUT] Semantic Placement & Collision Avoidance active ---")
    laid_out_ir = apply_layout(optimized_ir)
    
    # Step 9: CAMERA ENGINE (v1.12 Intelligence Pass)
    # Focuses on attention blocks and cinematic moves.
    print("--- [NIVIX CAMERA] Attention-Driven Cinematic Planning active ---")
    camera_aware_ir = apply_camera(laid_out_ir)
    
    # Step 10: TRACK SCHEDULER (DAG Planning Engine)
    # Note: Scheduler now runs on camera-aware IR.
    print("--- Calculating Temporal Timeline (DAG Planning)... ---")
    timed_ir = schedule_tracks(camera_aware_ir)
    
    # Step 10: SCENE SEGMENTER (Segmentation Engine)
    # Stage: Use metadata cues to split timeline into cinematic shots.
    print("--- Segmenting Multi-Phase Timeline (Cinematic Cuts)... ---")
    segmented_ir = segment_scenes(timed_ir)
    
    # Step 9: EXECUTION IR LOWERING PASS (NEW PLACEMENT)
    # Stage: Strip all metadata wrappers and diagnostic keys (starting with '_').
    print("--- Executing Execution IR Lowering Pass (Cleaning Stage)... ---")
    execution_ir = produce_execution_ir(segmented_ir)
    
    # Step 11: Finalize Multi-Scene Execution Graph
    print("--- Finalizing Multi-Scene Execution Graph (Final Stage)... ---")
    scene_graph = build(execution_ir)
    
    # Step 12: RENDERER ADAPTER PASS (v1.13 Abstraction Layer)
    # Note: Transition from IR -> Adapter-specific execution. 
    # This enables renderer-portable bytecode.
    print("--- [NIVIX PRODUCER] Cross-Platform Animation Rendering Active ---")
    renderer = ManimAdapter() # User can choice which adapter to use here
    output = produce_video(scene_graph, renderer)
    
    # Debug Summary
    print(f"\n[NIVIX OUTPUT]: {output.get('file', 'Nivix Final Content Ready')}")

if __name__ == "__main__":
    nivix_pipeline()
