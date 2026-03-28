# Nivix Layout Solver v5.0
# Constraint-Based Spatial Execution Engine
# Resolves WHERE objects are placed based on spatial relationships

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from ..solver import BaseSolver, Constraint, ExecutionSlot, SolverMode

@dataclass
class SpatialConstraint:
    """Spatial relationship between nodes."""
    type: str  # ALIGNS_WITH, CENTER_OF, DISTANCE, PROPORTION
    node_a: str
    node_b: Optional[str] = None
    axis: str = "horizontal"  # horizontal, vertical
    offset: float = 0.0

class LayoutSolver(BaseSolver):
    """
    Solves spatial constraints to produce deterministic layout positions.
    
    Current behavior:
        - Manual coordinate assignment
        - Heuristic positioning
    
    Future behavior:
        - align(A) WITH center(B)
        - distance(A, B) = 100px
        - A.horizontal_center == B.horizontal_center
        - proportion(A, B) = 0.5
    """
    
    def __init__(self, mode: SolverMode = SolverMode.EAGER):
        super().__init__(mode)
        self.spatial_constraints: List[SpatialConstraint] = []
        self.position_map: Dict[str, Tuple[float, float]] = {}
        self.default_spacing = 50.0
    
    def add_constraint(self, constraint: Constraint) -> None:
        """Add spatial constraint."""
        if constraint.type in ["spatial", "alignment", "center", "distance", "proportion"]:
            self.constraints.append(constraint)
    
    def _infer_spatial_constraints(self, cir: Dict[str, Any]) -> None:
        """Infer spatial constraints from CIR constraints."""
        constraints = cir.get("constraints", [])
        
        for c in constraints:
            ctype = c.get("type", "")
            nodes = c.get("nodes", [])
            
            if ctype == "alignment":
                if len(nodes) >= 2:
                    self.spatial_constraints.append(SpatialConstraint(
                        type="ALIGNS_WITH",
                        node_a=nodes[0],
                        node_b=nodes[1],
                        axis="horizontal"
                    ))
            elif ctype == "hierarchical":
                if len(nodes) >= 2:
                    self.spatial_constraints.append(SpatialConstraint(
                        type="ALIGNS_WITH",
                        node_a=nodes[0],
                        node_b=nodes[1],
                        axis="vertical"
                    ))
    
    def _infer_positions(self, cir: Dict[str, Any]) -> None:
        """Infer initial positions from nodes."""
        nodes = cir.get("nodes", [])
        
        x_offset = -200.0
        for node in nodes:
            node_id = node.get("id", f"node_{len(self.position_map)}")
            self.position_map[node_id] = (x_offset, 0.0)
            x_offset += self.default_spacing
    
    def _resolve_alignment(self, constraint: Dict[str, Any]) -> None:
        """Resolve alignment constraint."""
        axis = constraint.get("axis", "horizontal")
        node_a = constraint.get("node_a")
        node_b = constraint.get("node_b")
        
        if node_a in self.position_map and node_b in self.position_map:
            ax, ay = self.position_map[node_a]
            bx, by = self.position_map[node_b]
            
            if axis == "horizontal":
                self.position_map[node_a] = (bx, ay)
            else:
                self.position_map[node_a] = (ax, by)
    
    def _resolve_hierarchical(self, nodes: List[str], axis: str) -> None:
        """Resolve hierarchical stack layout."""
        if axis == "vertical":
            y_offset = 100.0
            for node_id in nodes:
                if node_id in self.position_map:
                    x, _ = self.position_map[node_id]
                    self.position_map[node_id] = (x, y_offset)
                    y_offset -= self.default_spacing
        else:
            x_offset = -100.0
            for node_id in nodes:
                if node_id in self.position_map:
                    _, y = self.position_map[node_id]
                    self.position_map[node_id] = (x_offset, y)
                    x_offset += self.default_spacing
    
    def solve(self, cir: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve spatial constraints and return enriched CIR with resolved positions.
        
        Pipeline:
            1. Infer constraints from CIR structure
            2. Apply layout resolution rules
            3. Produce deterministic position map
            4. Attach resolved positions to nodes
        """
        print("--- [LAYOUT SOLVER] Resolving spatial constraints ---")
        
        self._infer_spatial_constraints(cir)
        self._infer_positions(cir)
        
        for constraint in self.constraints:
            if constraint.type == "spatial" or constraint.type == "alignment":
                self._resolve_alignment(constraint.params)
        
        constraints = cir.get("constraints", [])
        for c in constraints:
            if c.get("type") == "hierarchical":
                self._resolve_hierarchical(c.get("nodes", []), "vertical")
            elif c.get("type") == "alignment":
                self._resolve_hierarchical(c.get("nodes", []), "horizontal")
        
        resolved_cir = cir.copy()
        resolved_cir["_solver"] = "layout_solver"
        resolved_cir["_position_map"] = self.position_map
        
        print("--- [LAYOUT SOLVER] Positions resolved:")
        for node_id, (x, y) in self.position_map.items():
            print(f"    {node_id}: ({x:.1f}, {y:.1f})")
        
        return resolved_cir
    
    def validate(self, cir: Dict[str, Any]) -> bool:
        """Validate that spatial constraints are satisfiable."""
        self._infer_spatial_constraints(cir)
        
        for node_id in self.position_map:
            x, y = self.position_map[node_id]
            if abs(x) > 2000 or abs(y) > 2000:
                return False
        
        return True

# Auto-register
try:
    from nivix.core.solver import SolverRegistry
    SolverRegistry.register("layout", LayoutSolver)
except ImportError:
    pass