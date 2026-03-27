# NIVIX - Animation & Visualization System
# Main Execution Engine and Pipeline Coordinator

import json
from core.parser.parser import parse_prompt
from core.validator.validator import validate
from core.policy.defaults import apply_defaults
from core.scenegraph.builder import build

def nivix_pipeline():
    """
    Main entry point for the Nivix animation pipeline.
    Connects Natural Language -> LLM Intent -> Validation -> Policy Engine -> Scene Graph Building.
    """
    print("\n--- Welcome to NIVIX Pipeline v0.1 ---")
    
    # Step 1: Input Natural Language Prompt
    # E.g., "make a red square"
    prompt = input("Enter animation prompt: ")
    
    # Step 2: Parse Prompt (Intent Extraction only)
    print("\n--- Parsing User Intent... ---")
    raw_response = parse_prompt(prompt)
    
    # Step 3: Convert String to Dictionary
    scene_json = json.loads(raw_response)
    
    # Step 4: Validate Scene Structure
    # Ensures the root level is valid (e.g., 'objects' array exists)
    print("--- Validating Intent Structure... ---")
    validate(scene_json)
    
    # Step 5: DEFAULTS POLICY ENGINE (NEW)
    # This layer ensures that the minimal intent is expanded into a complete runtime state.
    print("--- Applying Default Policies (Filling gaps + Enforcing Case)... ---")
    scene_with_defaults = apply_defaults(scene_json)
    
    # Step 6: Build Scene Graph for Renderer
    print("--- Building Scene Graph for Renderer... ---")
    scene_graph = build(scene_with_defaults)
    
    # Final Output Summaries
    print("\n[Parsed Intent]:")
    print(json.dumps(scene_json, indent=4))
    
    print("\n[Final Runtime Scene Graph (Policy-Enforced)]: ")
    print(json.dumps(scene_graph, indent=4))

if __name__ == "__main__":
    nivix_pipeline()
