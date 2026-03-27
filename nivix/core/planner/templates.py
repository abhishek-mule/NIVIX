SCENE_TEMPLATES = {
    # INTRO Blocks
    "title_card": {
        "type": "title",
        "goal": "identify_topic",
        "visual_priority": "high",
        "camera_strategy": "static_center",
        "requires": [],
        "produces": ["topic_title"]
    },
    "concept_hook": {
        "type": "concept_intro",
        "goal": "establish_intuition",
        "visual_priority": "medium",
        "camera_strategy": "pan_wide",
        "requires": ["topic_title"],
        "produces": ["concept_intuition"]
    },
    
    # CORE Block Types
    "equation_intro": {
        "type": "equation",
        "goal": "introduce_formula",
        "visual_priority": "center_focus",
        "camera_strategy": "zoom_center",
        "requires": ["concept_intuition"],
        "produces": ["equation_object"]
    },
    "symbol_breakdown": {
        "type": "annotation",
        "goal": "label_variables",
        "visual_priority": "focused_labels",
        "camera_strategy": "follow",
        "requires": ["equation_object"],
        "produces": ["labeled_symbols"]
    },
    "geometric_proof": {
        "type": "visualization",
        "goal": "visual_evidence",
        "visual_priority": "high",
        "camera_strategy": "pan",
        "requires": ["equation_object"],
        "produces": ["geometric_proof_state"]
    },
    "step_derivation": {
        "type": "transformation",
        "goal": "algebraic_derivation",
        "visual_priority": "high",
        "camera_strategy": "static",
        "requires": ["equation_object"],
        "produces": ["derived_equation"]
    },
    "graph_interpretation": {
        "type": "graph",
        "goal": "functional_mapping",
        "visual_priority": "high",
        "camera_strategy": "zoom_to_bounds",
        "requires": ["equation_object"],
        "produces": ["graph_visual"]
    },
    "concept_comparison": {
        "type": "comparison",
        "goal": "differentiate_concepts",
        "visual_priority": "side_by_side",
        "camera_strategy": "pan_between",
        "requires": ["concept_intuition"], # Needs at least 2 concepts technically
        "produces": ["comparison_insight"]
    },
    
    # OUTRO Blocks
    "summary_recap": {
        "type": "summary",
        "goal": "final_takeaway",
        "visual_priority": "medium",
        "camera_strategy": "zoom_out_wide",
        "requires": ["concept_intuition"],
        "produces": ["conclusion"]
    }
}

def get_scene_block(block_type):
    return SCENE_TEMPLATES.get(block_type, SCENE_TEMPLATES["concept_hook"])

def list_scene_types():
    return list(SCENE_TEMPLATES.keys())
