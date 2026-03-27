# Nivix Fallback Loader v2.1
# Added debugging for repair stage v2.1.

import json
from config.models import MODEL_PRIORITY
from core.parser.request import send_request
from core.repair.json_fixer import fix_json_syntax

def call_with_fallback(prompt):
    """
    Attempts to parse a prompt using models in order of priority.
    Employs the JSON Repair Layer to salvage malformed results.
    """
    for model in MODEL_PRIORITY:
        try:
            # 1. Dispatch Request
            response = send_request(model, prompt)
            
            # 2. Syntax Check / Repair Path
            try:
                json.loads(response)
            except json.JSONDecodeError:
                print(f"--- [REPAIR] Salvaging malformed output from {model}... ---")
                repaired = fix_json_syntax(response)
                print(f"--- [DEBUG] Repaired String: {repaired[:100]}... ---")
                # Attempt to validate repaired string
                json.loads(repaired)
                response = repaired # Accept the repaired block
            
            print(f"Using: {model} (Generation Validated)")
            return response
            
        except Exception as e:
            print(f"{model} generation failed or irrepairable: {e}")
            
    raise Exception("Critical failure: All configured models failed to produce valid IR.")
