# Nivix Intent Resolver v5.0
# Semantic Intent Resolution Engine
# Resolves WHY objects are animated based on narrative relationships

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from ..solver import BaseSolver, Constraint, ExecutionSlot, SolverMode

class IntentType(Enum):
    """Semantic intent types for animation."""
    COMPARE = "compare"
    EMPHASIZE = "emphasize"
    TRANSFORM = "transform"
    REVEAL = "reveal"
    HIGHLIGHT = "highlight"
    SEQUENCE = "sequence"
    DERIVE = "derive"

class IntentGraph:
    """
    Represents semantic relationships between objects.
    
    Current behavior:
        - Timeline-based sequential animations
    
    Future behavior:
        - relationship(A, B) = comparison
        - camera_intent = emphasize_difference
        - layout_constraint = horizontal_symmetry
        - semantic_role(A) = subject
    """
    
    def __init__(self):
        self.intents: Dict[str, IntentType] = {}
        self.relationships: List[Dict[str, Any]] = []
        self.roles: Dict[str, str] = {}
        self.focus_scores: Dict[str, float] = {}
    
    def add_intent(self, node_id: str, intent: IntentType) -> None:
        self.intents[node_id] = intent
    
    def add_relationship(self, node_a: str, node_b: str, rel_type: str) -> None:
        self.relationships.append({
            "node_a": node_a,
            "node_b": node_b,
            "type": rel_type
        })
    
    def add_role(self, node_id: str, role: str) -> None:
        self.roles[node_id] = role
    
    def set_focus(self, node_id: str, score: float) -> None:
        self.focus_scores[node_id] = score
    
    def get_focus_order(self) -> List[str]:
        return sorted(self.focus_scores.keys(), 
                     key=lambda x: self.focus_scores.get(x, 0), 
                     reverse=True)

class IntentResolver(BaseSolver):
    """
    Resolves semantic intents from planner output.
    
    Pipeline:
        1. Extract intent from prompt/topic
        2. Build intent graph (relationships, roles)
        3. Infer camera intent from narrative
        4. Apply focus scores automatically
    """
    
    def __init__(self, mode: SolverMode = SolverMode.EAGER):
        super().__init__(mode)
        self.intent_graph = IntentGraph()
    
    def add_constraint(self, constraint: Constraint) -> None:
        """Add intent constraint."""
        if constraint.type == "intent":
            self.constraints.append(constraint)
    
    def _infer_intents_from_prompt(self, cir: Dict[str, Any]) -> None:
        """Infer intents from meta prompt."""
        meta = cir.get("meta", {})
        prompt = meta.get("prompt", "").lower()
        
        if "compare" in prompt or "difference" in prompt or "vs" in prompt:
            self.intent_graph.add_relationship("first", "second", "comparison")
        
        if "emphasize" in prompt or "highlight" in prompt:
            self.intent_graph.add_intent("focus", IntentType.EMPHASIZE)
        
        if "derive" in prompt or "show" in prompt:
            self.intent_graph.add_intent("result", IntentType.REVEAL)
    
    def _infer_roles_from_nodes(self, cir: Dict[str, Any]) -> None:
        """Infer semantic roles from node structure."""
        nodes = cir.get("nodes", [])
        attention = cir.get("attention", [])
        
        for i, node in enumerate(nodes):
            node_id = node.get("id", f"node_{i}")
            
            if i == 0:
                self.intent_graph.add_role(node_id, "subject")
            elif i == len(nodes) - 1:
                self.intent_graph.add_role(node_id, "result")
            else:
                self.intent_graph.add_role(node_id, "context")
        
        for focus in attention:
            node_id = focus.get("node_id")
            score = focus.get("focus_score", 0.5)
            if node_id:
                self.intent_graph.set_focus(node_id, score)
    
    def _transform_to_intent(self, transform: Dict[str, Any]) -> IntentType:
        """Map transform action to intent type."""
        action = transform.get("action", "")
        
        mapping = {
            "move": IntentType.TRANSFORM,
            "fade_in": IntentType.REVEAL,
            "fade_out": IntentType.REVEAL,
            "scale": IntentType.EMPHASIZE,
            "morph": IntentType.TRANSFORM,
            "highlight": IntentType.HIGHLIGHT,
        }
        
        return mapping.get(action, IntentType.SEQUENCE)
    
    def _build_intent_graph(self, cir: Dict[str, Any]) -> None:
        """Build complete intent graph from CIR."""
        self._infer_intents_from_prompt(cir)
        self._infer_roles_from_nodes(cir)
        
        transforms = cir.get("transforms", [])
        for transform in transforms:
            node_id = transform.get("node_id")
            intent = self._transform_to_intent(transform)
            if node_id:
                self.intent_graph.add_intent(node_id, intent)
    
    def solve(self, cir: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve semantic intents and return enriched CIR.
        
        Pipeline:
            1. Extract intent from prompt
            2. Build intent graph
            3. Apply automatic focus scoring
            4. Attach narrative structure
        """
        print("--- [INTENT RESOLVER] Resolving semantic intents ---")
        
        self._build_intent_graph(cir)
        
        meta = cir.get("meta", {})
        
        relationships = self.intent_graph.relationships
        if relationships:
            print(f"--- [INTENT RESOLVER] Relationships found: {len(relationships)}")
            for rel in relationships:
                print(f"    {rel['node_a']} --[{rel['type']}]--> {rel['node_b']}")
        
        roles = self.intent_graph.roles
        if roles:
            print(f"--- [INTENT RESOLVER] Roles assigned:")
            for node_id, role in roles.items():
                print(f"    {node_id}: {role}")
        
        focus_order = self.intent_graph.get_focus_order()
        if focus_order:
            print(f"--- [INTENT RESOLVER] Focus order: {' > '.join(focus_order)}")
        
        resolved_cir = cir.copy()
        resolved_cir["_solver"] = "intent_resolver"
        intents_serialized = {}
        for k, v in self.intent_graph.intents.items():
            if hasattr(v, 'value'):
                intents_serialized[k] = v.value
            else:
                intents_serialized[k] = str(v)
        
        resolved_cir["_intent_graph"] = {
            "intents": intents_serialized,
            "relationships": self.intent_graph.relationships,
            "roles": self.intent_graph.roles,
            "focus_scores": self.intent_graph.focus_scores
        }
        
        return resolved_cir
    
    def validate(self, cir: Dict[str, Any]) -> bool:
        """Validate that intents are resolvable."""
        self._build_intent_graph(cir)
        
        nodes = cir.get("nodes", [])
        for node in nodes:
            node_id = node.get("id")
            if node_id and node_id not in self.intent_graph.roles:
                return False
        
        return True

# Auto-register
try:
    from nivix.core.solver import SolverRegistry
    SolverRegistry.register("intent", IntentResolver)
except ImportError:
    pass