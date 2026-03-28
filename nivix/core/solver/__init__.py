# Nivix Solver Layer v5.0
# Constraint-Based Cinematic Execution Engine
# Separates intent resolution from rendering for deterministic output

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

class SolverMode(Enum):
    """Solver execution modes."""
    LAZY = "lazy"           # Minimal computation
    EAGER = "eager"        # Full constraint solve
    INCREMENTAL = "incremental"  # Resume from partial

@dataclass
class Constraint:
    """Represents a cinematic constraint to satisfy."""
    id: str
    type: str  # temporal, spatial, intent
    target: str  # node_id or relationship
    params: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # Higher = more important
    satisfied: bool = False

@dataclass
class ExecutionSlot:
    """A resolved time slot for animation execution."""
    node_id: str
    start_frame: int
    end_frame: int
    track: int = 0
    constraints_used: List[str] = field(default_factory=list)

class BaseSolver(ABC):
    """
    Abstract base for all Nivix solvers.
    Solvers sit between Planner and Renderer to ensure deterministic output.
    """
    
    def __init__(self, mode: SolverMode = SolverMode.EAGER):
        self.mode = mode
        self.constraints: List[Constraint] = []
        self.solved_slots: List[ExecutionSlot] = []
    
    @abstractmethod
    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to solve."""
        pass
    
    @abstractmethod
    def solve(self, cir: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve constraints and return enriched CIR with execution slots.
        """
        pass
    
    @abstractmethod
    def validate(self, cir: Dict[str, Any]) -> bool:
        """
        Validate that all constraints are satisfiable.
        """
        pass

class SolverRegistry:
    """
    Registry for available solvers.
    """
    _solvers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, solver_class: type):
        cls._solvers[name] = solver_class
    
    @classmethod
    def get(cls, name: str) -> Optional[type]:
        return cls._solvers.get(name)
    
    @classmethod
    def list_solvers(cls) -> List[str]:
        return list(cls._solvers.keys())

def create_solver(solver_name: str, mode: SolverMode = SolverMode.EAGER) -> Optional[BaseSolver]:
    """Factory function to create solver instances."""
    solver_class = SolverRegistry.get(solver_name.lower())
    if solver_class:
        return solver_class(mode)
    return None