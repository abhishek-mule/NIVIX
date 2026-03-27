# Nivix Request Dispatcher v1.9
# Bridge between the Nivix Parser Engine and AI models.
# Upgraded with Timeline Optimization Mocking (v1.9 Expansion).

import os
import json
import requests
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

def send_request(model_name, prompt):
    """
    Routes a parsing request to the appropriate AI provider or local model.
    """
    user_prompt = prompt.split("User Prompt:")[-1].strip() if "User Prompt:" in prompt else prompt
    p_lower = user_prompt.lower()
    
    if "Circular Dependency Test" in p_lower:
         return _produce_cyclic_mock()

    # 1. Routing: Timeline Optimization Stress Sequence (v1.9 Expansion)
    if "show square" in p_lower and "show circle" in p_lower and "move" in p_lower:
         return _produce_optimization_mock(p_lower)

    # 2. Routing: Scene Transition
    if "fade to" in p_lower or "transition to" in p_lower:
         return _produce_transition_mock(p_lower)

    # 3. Routing: Hierarchical Grouping
    if ("group" in p_lower or "combine" in p_lower) and ("scene" in p_lower or "nested" in p_lower):
         return _produce_nested_group_mock(p_lower)

    # 4. Routing: Object Grouping (Flat)
    if "group" in p_lower or "combine" in p_lower:
         return _produce_group_mock(p_lower)

    # 5. Routing: Anchored Transform
    if ("label" in p_lower or "attach" in p_lower) and "transform" in p_lower:
         return _produce_anchored_transform_mock(p_lower)

    return _mock_ai_response(model_name, p_lower)

def _produce_optimization_mock(prompt):
    """
    Mocks an unoptimized sequential intent.
    'show square, show circle, move square right, move circle right'
    The optimizer should parallelize these into 2 synchronized stages.
    """
    print(f"--- [DEBUG] Simulating Unoptimized Sequential Intent (v1.9 Active) ---")
    
    objects = [
        { "id": "sq_0", "type": "square", "motion": "none", "duration": 1.0 },
        { "id": "ci_0", "type": "circle", "motion": "none", "duration": 1.0 },
        # Individual moves (should be parallelized)
        { "id": "sq_0", "type": "square", "motion": "right", "duration": 2.0 },
        { "id": "ci_0", "type": "circle", "motion": "right", "duration": 2.0 }
    ]
    
    # We provide them in 'sequential' mode.
    # The DAG scheduler would usually chain them 1 -> 2 -> 3 -> 4.
    # Total time: 1+1+2+2 = 6s.
    # Optimized time: 1 + 2 = 3s.
    
    mock_intent = {
        "scene": {
            "objects": objects,
            "sequence_mode": "sequential"
        }
    }
    return json.dumps(mock_intent)

def _produce_transition_mock(prompt):
    print(f"--- [DEBUG] Simulating Narrative Cinematic Transition (v1.7 Active) ---")
    m = [ { "id": "eq_0", "type": "mathtex", "content": "F=ma", "duration": 1.0 } ]
    o = [ { "id": "axis_x", "type": "square", "_trigger_new_scene": True } ]
    t = [ { "id": "T", "type": "transition", "style": "fade", "from_scene": 0, "to_scene": 1, "duration": 1.5 } ]
    return json.dumps({"scene": {"math_objects": m, "objects": o, "scene_transitions": t, "sequence_mode": "sequential"}})

def _produce_nested_group_mock(prompt):
    print(f"--- [DEBUG] Simulating Hierarchical Diagram Composition (v1.6 Active) ---")
    objects = [ { "id": "A", "type": "circle" }, { "id": "sq_0", "type": "square" } ]
    group_objects = [ { "id": "tri", "members": ["A"] }, { "id": "scene", "members": ["tri", "sq_0"], "motion": "right" } ]
    return json.dumps({ "scene": { "objects": objects, "group_objects": group_objects, "sequence_mode": "sequential" } })

def _produce_group_mock(prompt):
    objects = [ { "id": "sq_0", "type": "square" } ]
    group_objects = [ { "id": "G", "members": ["sq_0"], "motion": "right" } ]
    return json.dumps({"scene": {"objects": objects, "group_objects": group_objects, "sequence_mode": "sequential"}})

def _produce_anchored_transform_mock(prompt):
    math_objects = [ { "id": "eq_0", "type": "mathtex", "content": "F = ma", "duration": 1.0 } ]
    text_objects = [ { "id": "label_0", "type": "text", "content": "force", "anchor_to": "eq_0", "anchor_symbol": "F" } ]
    transforms = [ { "id": "trans_0", "type": "equation_transform", "source_id": "eq_0", "target_content": "a = \\frac{F}{m}" } ]
    return json.dumps({"scene": {"math_objects": math_objects, "text_objects": text_objects, "equation_transforms": transforms, "sequence_mode": "sequential"}})

def _mock_ai_response(model_name, prompt):
    return json.dumps({"scene": {"objects": [{"type": "square", "color": "red"}]}})

def _produce_cyclic_mock():
    return json.dumps({"scene": {"objects": [ { "id": "A", "type": "square", "after": "B" }, { "id": "B", "type": "circle", "after": "A" } ]}})
