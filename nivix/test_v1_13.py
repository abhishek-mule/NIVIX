
import json
from core.parser.parser import parse_prompt
from core.repair.json_fixer import safe_parse
from core.repair.schema_normalizer import produce_normalized_intent
from core.validator.validator import validate
from core.policy.semantic_map import normalize_semantics
from core.policy.defaults import apply_defaults
from core.ir.lowering_pass import produce_execution_ir
from core.scheduler.track_scheduler import schedule_tracks
from core.compiler.scene_segmenter import segment_scenes
from core.optimizer.timeline_optimizer import optimize_timeline
from core.layout.layout_engine import apply_layout
from core.camera.camera_engine import apply_camera
from core.scenegraph.builder import build
from core.renderers.renderer_pass import produce_video
from renderers.manim_adapter.manim_adapter import ManimAdapter

def test_pipeline():
    print("--- [TEST] Nivix v1.13 Rendering Pipeline ---")
    
    # Mock Input
    prompt = "show title Hello. show equation E=mc^2. fade to square."
    
    # 1. Pipeline
    print("Step 1: Parsing...")
    # Skipping real parse for speed, using mock normalized intent
    normalized_intent = {
        "title": "v1.13 Test",
        "objects": [
            {"id": "title_1", "type": "text", "content": "Hello", "style": "title"},
            {"id": "eq_1", "type": "math", "equation": "E=mc^2"},
            {"id": "sq_1", "type": "square", "color": "blue", "_trigger_new_scene": True}
        ],
        "scene_transitions": [
            {"from_scene": 0, "to_scene": 1, "type": "fade", "duration": 1.5}
        ]
    }
    
    # 2-6. Standard Passes
    semantic_ir = normalize_semantics(normalized_intent)
    full_semantic_ir = apply_defaults(semantic_ir)
    optimized_ir = optimize_timeline(full_semantic_ir)
    laid_out_ir = apply_layout(optimized_ir)
    
    # 7. CAMERA Intelligence (v1.12+)
    camera_aware_ir = apply_camera(laid_out_ir)
    
    # 8. SCHEDULER
    timed_ir = schedule_tracks(camera_aware_ir)
    
    # 9. SEGMENTER
    segmented_ir = segment_scenes(timed_ir)
    
    # 10. LOWERING
    execution_ir = produce_execution_ir(segmented_ir)
    
    # 11. BUILDER
    scene_graph = build(execution_ir)
    
    # 12. RENDERER (v1.13)
    print("\n--- [DISPATCHING TO MANIM ADAPTER] ---")
    renderer = ManimAdapter()
    output = produce_video(scene_graph, renderer)
    
    print("\n[RESULT]:", output)

if __name__ == "__main__":
    test_pipeline()
