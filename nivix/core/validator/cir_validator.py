import json
import os
import jsonschema
from jsonschema import validate, ValidationError

# Get the path to the schema file dynamically based on this file's location
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(CURRENT_DIR, "..", "..", "schema", "cir_schema.json")

def load_schema():
    """Loads the CIR JSON Schema from disk."""
    with open(SCHEMA_PATH, "r") as file:
        return json.load(file)

def validate_cir(cir_data):
    """
    Validates a generated CIR object against the strict v4.0 JSON schema.
    Returns (True, None) if valid, or (False, error_message) if invalid.
    """
    schema = load_schema()
    try:
        validate(instance=cir_data, schema=schema)
        return True, "Valid CIR format."
    except ValidationError as e:
        # Give a readable error path for debugging
        path = " -> ".join([str(p) for p in e.path])
        error_msg = f"CIR Validation failed at [{path}]: {e.message}"
        return False, error_msg

if __name__ == "__main__":
    # Test block
    print("--- [NIVIX VALIDATOR] Testing CIR Schema ---")
    mock_cir = {
        "nodes": [
            {
                "id": "node_1",
                "type": "object",
                "lifecycle": {"spawn": 0, "destroy": 100}
            }
        ],
        "transforms": [],
        "constraints": [],
        "attention": [],
        "meta": {
            "prompt": "Test the validator",
            "version": "4.0"
        }
    }
    
    is_valid, msg = validate_cir(mock_cir)
    print("Status:", msg)
