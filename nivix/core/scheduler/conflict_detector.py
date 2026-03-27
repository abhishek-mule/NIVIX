# Nivix Temporal Conflict Detector
# Ensures that the animation dependency graph is acyclic and structurally valid.

class TemporalDependencyCycleError(Exception):
    """Raised when the animation scheduler detects a circular dependency (e.g., A after B, B after A)."""
    pass

class ConflictDetector:
    """
    Checks for structural and temporal conflicts in the animation dependency graph.
    Used as an 'Execution Guard' before the renderer stage.
    """
    def __init__(self, nodes, edges):
        self.nodes = nodes # node_id -> metadata
        self.edges = edges # node_id -> [dependencies]
        
    def validate(self):
        """
        Runs a comprehensive validation suite on the dependency graph.
        Throws a TemporalDependencyCycleError if any conflict is found.
        """
        self._check_self_dependencies()
        self._check_for_cycles()
        
    def _check_self_dependencies(self):
        """Rejects objects that attempt to depend on themselves."""
        for target, deps in self.edges.items():
            if target in deps:
                raise TemporalDependencyCycleError(f"Self-dependency detected: {target} cannot depend on itself.")
                
    def _check_for_cycles(self):
        """Uses Depth-First Search (DFS) to detect circular dependencies (cycles)."""
        visited = set()
        recursion_stack = set()
        
        def has_cycle(node):
            if node in recursion_stack:
                return True
            if node in visited:
                return False
                
            visited.add(node)
            recursion_stack.add(node)
            
            # Recurse into dependencies (edges are dependency -> target, 
            # but our storage is target -> [dependencies])
            for neighbor in self.edges.get(node, []):
                if has_cycle(neighbor):
                    return True
                    
            recursion_stack.remove(node)
            return False

        for node in self.nodes:
            if node not in visited:
                if has_cycle(node):
                    # Find a path to illustrate the cycle for better error reporting
                    raise TemporalDependencyCycleError(f"Circular dependency detected in the animation timeline near: {node}")
                    
        return False
