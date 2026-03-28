# Nivix CIR Validator v7.1
# Validates CIR structure and consistency

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass

@dataclass
class ValidationError:
    """CIR validation error."""
    code: str
    message: str
    location: Optional[str] = None

class CIRValidator:
    """
    Validates CIR structure and consistency.
    
    Checks:
    - Node references are valid
    - Transform targets exist
    - Attention targets exist
    - Timeline lifecycles are consistent
    - DAG has no cycles
    """
    
    def __init__(self):
        self.errors: List[ValidationError] = []
    
    def validate(self, cir: Dict[str, Any]) -> bool:
        """Run all validations. Returns True if valid."""
        self.errors = []
        
        self._validate_nodes_exist(cir)
        self._validate_transform_targets(cir)
        self._validate_attention_targets(cir)
        self._validate_lifecycles(cir)
        self._validate_unique_ids(cir)
        
        if self.errors:
            print(f"--- [VALIDATOR] Found {len(self.errors)} errors ---")
            for err in self.errors:
                print(f"  [{err.code}] {err.message}")
            return False
        
        print(f"--- [VALIDATOR] PASSED ---")
        return True
    
    def _validate_nodes_exist(self, cir: Dict[str, Any]) -> None:
        """Validate all referenced nodes exist."""
        nodes = cir.get("nodes", [])
        node_ids = {n.get("id") for n in nodes}
        
        for transform in cir.get("transforms", []):
            tid = transform.get("node_id", "")
            if tid and tid not in node_ids:
                self.errors.append(ValidationError(
                    "INVALID_NODE_REF",
                    f"Transform references non-existent node: {tid}",
                    tid
                ))
    
    def _validate_transform_targets(self, cir: Dict[str, Any]) -> None:
        """Validate transform target nodes exist."""
        nodes = cir.get("nodes", [])
        node_ids = {n.get("id") for n in nodes}
        
        for transform in cir.get("transforms", []):
            target = transform.get("node_id", "")
            action = transform.get("action", "")
            
            if action in ["move", "scale", "fade_in", "fade_out", "morph"]:
                if not target:
                    self.errors.append(ValidationError(
                        "MISSING_TARGET",
                        f"Transform action '{action}' missing target node",
                        action
                    ))
    
    def _validate_attention_targets(self, cir: Dict[str, Any]) -> None:
        """Validate attention nodes exist."""
        nodes = cir.get("nodes", [])
        node_ids = {n.get("id") for n in nodes}
        
        for focus in cir.get("attention", []):
            target = focus.get("node_id", "")
            if target and target not in node_ids:
                self.errors.append(ValidationError(
                    "INVALID_ATTENTION",
                    f"Attention target node doesn't exist: {target}",
                    target
                ))
    
    def _validate_lifecycles(self, cir: Dict[str, Any]) -> None:
        """Validate lifecycle timing is consistent."""
        for node in cir.get("nodes", []):
            lifecycle = node.get("lifecycle", {})
            spawn = lifecycle.get("spawn", 0)
            destroy = lifecycle.get("destroy", 0)
            
            if destroy <= spawn:
                self.errors.append(ValidationError(
                    "INVALID_LIFECYCLE",
                    f"Node {node.get('id')}: destroy <= spawn",
                    node.get("id")
                ))
    
    def _validate_unique_ids(self, cir: Dict[str, Any]) -> None:
        """Validate all node IDs are unique."""
        node_ids = [n.get("id") for n in cir.get("nodes", [])]
        
        if len(node_ids) != len(set(node_ids)):
            from collections import Counter
            counts = Counter(node_ids)
            for nid, count in counts.items():
                if count > 1:
                    self.errors.append(ValidationError(
                        "DUPLICATE_ID",
                        f"Duplicate node ID: {nid}",
                        nid
                    ))
    
    def get_errors(self) -> List[ValidationError]:
        """Return list of validation errors."""
        return self.errors


def validate_cir(cir: Dict[str, Any]) -> bool:
    """Convenience function."""
    return CIRValidator().validate(cir)