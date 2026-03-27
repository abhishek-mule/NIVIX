import json
from core.fallback.loader import call_with_fallback

def parse_prompt(semantic_plan):
    """
    Parses a high-level pedagogical PLAN into a detailed animation IR.
    Focuses on IDENTIFYING scene transitions and narrative flow between plan scenes.
    """
    plan_str = json.dumps(semantic_plan, indent=2)
    
    schema = f"""
Task: Convert a pedagogical animation plan into Nivix Animation IR.
Input: A structured JSON planning document.
Output: Nivix Animation IR JSON.

Rules:
1. Every plan scene must map to at least ONE Nivix scene.
2. Ensure clear 'scene_transitions' between scenes.
3. Every scene starts with a '_trigger_new_scene': true.
4. If an equation transform is mentioned, include it in 'equation_transforms'.

Input Plan:
{plan_str}

Constraint: Output "objects", "text_objects", "math_objects", "equation_transforms", "group_objects", "scene_transitions", and "camera" arrays.

Animation IR:
"""
    return call_with_fallback(schema)
