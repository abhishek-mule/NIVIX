# Nivix Repair Stage Unit Test
# Directly tests the fault-tolerance layer against hostile JSON input.

import json
from core.repair.json_fixer import safe_parse
from core.repair.schema_normalizer import produce_normalized_intent

# Hostile JSON Scenario (Markdown, Unquoted keys/values, Trailing commas, String literals)
HOSTILE_JSON = """
```json
{
 objects:[
   {shape:square action:move_right,},
   {shape:circle action:move_up duration:two}
 ]
}
```
"""

def test_repair():
    print("--- 1. Testing Syntax Fix (v2.1) ---")
    try:
        repaired_dict = safe_parse(HOSTILE_JSON)
        print("Syntax Fix: SUCCESS")
        print("Parsed Result:", json.dumps(repaired_dict, indent=2))
        
        print("\n--- 2. Testing Schema Normalizer (v2) ---")
        normalized = produce_normalized_intent(repaired_dict)
        print("Schema Norm: SUCCESS")
        print("Normalized Result:", json.dumps(normalized, indent=2))
        
    except Exception as e:
        print(f"Repair Logic Failed: {e}")

if __name__ == "__main__":
    test_repair()
