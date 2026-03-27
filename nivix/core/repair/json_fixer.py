# Nivix JSON Syntax Repair Layer v2.2
# Advanced fault-tolerance for LLM structural fragments with robust unquoted key/value resolution.

import re
import json

# Word-to-Number Mapping for literal duration normalization
NUMERIC_MAP = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, 
    "five": 5, "ten": 10, "point five": 0.5
}

def fix_json_syntax(raw_text):
    """
    Compiler-grade syntax repair for LLM-hallucinated structural fragments.
    Uses an assertive approach to key/value quoting and comma insertion.
    """
    # 1. Cleanup: Strip markdown blocks and extra junk
    raw_text = re.sub(r"```[a-z]*\s*(.*?)\s*```", r"\1", raw_text, flags=re.DOTALL)
    raw_text = raw_text.strip()
    
    # 2. Fix: Unquoted Keys
    # Look for any word followed by a colon, unless it's already quoted
    raw_text = re.sub(r"(?<!\")\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?=\s*:)", r'"\1"', raw_text)
    
    # 3. Fix: Unquoted Values
    # Look for any word that follows a colon, unless it's already quoted
    # Handles space-terminated and punctuation-terminated values
    raw_text = re.sub(r":\s*(?!\")\b([a-zA-Z_][a-zA-Z0-9_]*)\b", r': "\1"', raw_text)
    
    # 4. Fix: Missing Commas between Key-Value pairs 
    # { "a": 1 "b": 2 } -> { "a": 1, "b": 2 }
    raw_text = re.sub(r"(\"|\d|true|false|null)\s+\"", r'\1, "', raw_text)
    
    # 5. Fix: Trailing commas
    raw_text = re.sub(r",\s*([\]}])", r"\1", raw_text)
    
    # 6. Balancing: Ensuring matching braces
    for opener, closer in [("{", "}"), ("[", "]")]:
        diff = raw_text.count(opener) - raw_text.count(closer)
        if diff > 0:
            raw_text += closer * diff
            
    return raw_text

def normalize_literals(scene_dict):
    """
    Deep traversal to convert alphanumeric literals (e.g., 'two') to numbers.
    """
    if isinstance(scene_dict, dict):
        return {k: normalize_literals(v) for k, v in scene_dict.items()}
    elif isinstance(scene_dict, list):
        return [normalize_literals(item) for item in scene_dict]
    elif isinstance(scene_dict, str):
        # Convert 'two' -> 2
        return NUMERIC_MAP.get(scene_dict.lower(), scene_dict)
    return scene_dict

def safe_parse(raw_text):
    """
    The fault-tolerant entry point for the Nivix pipeline.
    """
    try:
        # 1. Clean Path
        return normalize_literals(json.loads(raw_text))
    except (json.JSONDecodeError, TypeError):
        # 2. Repair Path
        try:
            repaired = fix_json_syntax(raw_text)
            parsed = json.loads(repaired)
            return normalize_literals(parsed)
        except Exception as e:
            # 3. Emergency Wrap-around Path
            if ":" in raw_text and not (raw_text.startswith("{") or raw_text.startswith("[")):
                 try:
                     repaired = fix_json_syntax("{" + raw_text + "}")
                     return normalize_literals(json.loads(repaired))
                 except: pass
            raise Exception(f"Compiler Fault: Irrepairable JSON output. Recovery failed: {e}. Repaired String: {repaired[:100]}...")
