# Nivix Timeline Solver v5.0
# Constraint-Based Temporal Execution Engine
# Resolves WHEN animations execute based on temporal relationships

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from ..solver import BaseSolver, Constraint, ExecutionSlot, SolverMode

@dataclass
class TemporalConstraint:
    """Temporal relationship between nodes."""
    type: str  # AFTER, BEFORE, WITH, DURING, SYNCHRONIZED, EXCLUDES
    node_a: str
    node_b: Optional[str] = None
    window_a: Optional[Tuple[int, int]] = None
    window_b: Optional[Tuple[int, int]] = None

class TimelineSolver(BaseSolver):
    """
    Solves temporal constraints to produce deterministic execution schedule.
    
    Current behavior:
        - Append animations sequentially
        - Resolve overlaps heuristically
    
    Future behavior:
        - start(A) AFTER appear(B)
        - align(text) WITH midpoint(animation)
        - duration(A) = duration(B)  // synchronized
        - overlap(A, B) = NONE       // exclusion
    """
    
    def __init__(self, mode: SolverMode = SolverMode.EAGER):
        super().__init__(mode)
        self.temporal_constraints: List[TemporalConstraint] = []
        self.frame_schedule: Dict[str, Tuple[int, int]] = {}
    
    def add_constraint(self, constraint: Constraint) -> None:
        """Add temporal constraint."""
        if constraint.type in ["temporal", "after", "before", "with", "during", "synchronized", "excludes"]:
            self.constraints.append(constraint)
    
    def _infer_temporal_constraints(self, cir: Dict[str, Any]) -> None:
        """Infer temporal constraints from CIR structure."""
        nodes = cir.get("nodes", [])
        transforms = cir.get("transforms", [])
        
        for i, node in enumerate(nodes):
            lifecycle = node.get("lifecycle", {})
            spawn = lifecycle.get("spawn", i * 30)
            destroy = lifecycle.get("destroy", 120)
            self.frame_schedule[node["id"]] = (spawn, destroy)
        
        for transform in transforms:
            node_id = transform.get("node_id")
            start = transform.get("start_frame", 0)
            end = transform.get("end_frame", 30)
            if node_id:
                self.frame_schedule[node_id] = (start, end)
    
    def _resolve_after_constraint(self, constraint: Dict[str, Any]) -> Tuple[int, int]:
        """Resolve A AFTER B constraint."""
        node_a = constraint.get("node_a")
        node_b = constraint.get("node_b")
        
        if node_b in self.frame_schedule:
            _, b_end = self.frame_schedule[node_b]
            if node_a in self.frame_schedule:
                a_start, a_end = self.frame_schedule[node_a]
                if a_start < b_end + 5:
                    self.frame_schedule[node_a] = (b_end + 5, a_end + 5)
        
        return self.frame_schedule.get(node_a, (0, 30))
    
    def _resolve_with_constraint(self, constraint: Dict[str, Any]) -> Tuple[int, int]:
        """Resolve A WITH B (synchronized) constraint."""
        node_a = constraint.get("node_a")
        node_b = constraint.get("node_b")
        
        if node_a in self.frame_schedule and node_b in self.frame_schedule:
            a_start, a_end = self.frame_schedule[node_a]
            b_start, b_end = self.frame_schedule[node_b]
            self.frame_schedule[node_a] = (b_start, b_start + (a_end - a_start))
            self.frame_schedule[node_b] = (b_start, b_start + (b_end - b_start))
        
        return self.frame_schedule.get(node_a, (0, 30))
    
    def _resolve_excludes_constraint(self, constraint: Dict[str, Any]) -> Tuple[int, int]:
        """Resolve A EXCLUDES B (no overlap) constraint."""
        node_a = constraint.get("node_a")
        node_b = constraint.get("node_b")
        
        if node_a in self.frame_schedule and node_b in self.frame_schedule:
            a_start, a_end = self.frame_schedule[node_a]
            b_start, b_end = self.frame_schedule[node_b]
            
            if not (a_end <= b_start or b_end <= a_start):
                if a_start < b_start:
                    self.frame_schedule[node_b] = (a_end + 1, b_end + (a_end + 1 - b_start))
                else:
                    self.frame_schedule[node_a] = (b_end + 1, a_end + (b_end + 1 - a_start))
        
        return self.frame_schedule.get(node_a, (0, 30))
    
    def solve(self, cir: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve temporal constraints and return enriched CIR with resolved slots.
        
        Pipeline:
            1. Infer constraints from CIR structure
            2. Apply constraint resolution rules
            3. Produce deterministic frame schedule
            4. Attach execution_slots to nodes
        """
        print("--- [TIMELINE SOLVER] Resolving temporal constraints ---")
        
        self._infer_temporal_constraints(cir)
        
        for constraint in self.constraints:
            if constraint.type == "after":
                self._resolve_after_constraint(constraint.params)
            elif constraint.type == "with":
                self._resolve_with_constraint(constraint.params)
            elif constraint.type == "excludes":
                self._resolve_excludes_constraint(constraint.params)
        
        resolved_cir = cir.copy()
        resolved_cir["_solver"] = "timeline_solver"
        resolved_cir["_frame_schedule"] = self.frame_schedule
        
        print("--- [TIMELINE SOLVER] Frame schedule resolved:")
        for node_id, (start, end) in self.frame_schedule.items():
            print(f"    {node_id}: [{start}, {end}]")
        
        return resolved_cir
    
    def validate(self, cir: Dict[str, Any]) -> bool:
        """Validate that temporal constraints are satisfiable."""
        self._infer_temporal_constraints(cir)
        
        for node_a, (a_start, a_end) in self.frame_schedule.items():
            for node_b, (b_start, b_end) in self.frame_schedule.items():
                if node_a != node_b:
                    if not (a_end <= b_start or b_end <= a_start):
                        for constraint in self.constraints:
                            if constraint.params.get("node_a") == node_a and constraint.params.get("node_b") == node_b:
                                if constraint.type == "excludes":
                                    return False
        
        return True

# Auto-register
try:
    from nivix.core.solver import SolverRegistry
    SolverRegistry.register("timeline", TimelineSolver)
except ImportError:
    pass