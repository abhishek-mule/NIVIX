# Nivix Deterministic Timeline Solver v7.0
# Dependency-driven temporal scheduling engine

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque

@dataclass
class TimelineSlot:
    """Scheduled time slot for execution."""
    node_id: str
    start_frame: int
    end_frame: int
    depth: int = 0
    track: int = 0

class DeterministicTimelineSolver:
    """
    Resolves timeline from dependency graph using topological ordering.
    
    Before (heuristic):
        spawn = 0
        spawn = 15
        spawn = 30
    
    After (dependency-driven):
        a           depth=0 → frame 0
        b           depth=0 → frame 0  
        a+b         depth=1 → frame 20
        (a+b)^2    depth=2 → frame 40
        expansion   depth=3 → frame 60
    """
    
    def __init__(self, frame_unit: int = 20, overlap_penalty: int = 5):
        self.frame_unit = frame_unit
        self.overlap_penalty = overlap_penalty
        self.slots: List[TimelineSlot] = []
    
    def solve(self, cir: Dict[str, Any], normalized: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Solve timeline from dependency graph.
        
        Returns CIR with resolved frame schedules.
        """
        print("--- [TIMELINE SOLVER] Computing deterministic schedule ---")
        
        symbol_graph = normalized.get("_canonical_symbols", {}) if normalized else {}
        index = normalized.get("_symbol_index", {}) if normalized else {}
        
        nodes = cir.get("nodes", [])
        
        if not nodes:
            print("--- [TIMELINE SOLVER] No nodes to schedule ---")
            return cir
        
        graph = self._build_dependency_graph(symbol_graph, nodes)
        
        execution_order = self._topological_sort(graph)
        
        frame_assignments = self._compute_frames(execution_order, graph)
        
        assignments_str = {}
        total_duration = 0
        for node_id, frame in frame_assignments.items():
            assignments_str[node_id] = {"start": frame, "end": frame + self.frame_unit}
            total_duration = max(total_duration, frame + self.frame_unit)
        
        print(f"--- [TIMELINE SOLVER] Execution order: {' -> '.join(execution_order)}")
        print(f"--- [TIMELINE SOLVER] Frame assignments: {assignments_str}")
        print(f"--- [TIMELINE SOLVER] Total duration: {total_duration} frames")
        
        resolved_cir = cir.copy()
        resolved_cir["_frame_schedule"] = assignments_str
        resolved_cir["_execution_order"] = execution_order
        resolved_cir["_total_duration"] = total_duration
        
        for node in resolved_cir.get("nodes", []):
            node_id = node.get("id", "")
            if node_id in frame_assignments:
                node["lifecycle"] = {
                    "spawn": frame_assignments[node_id],
                    "destroy": frame_assignments[node_id] + self.frame_unit
                }
        
        return resolved_cir
    
    def _build_dependency_graph(self, symbol_graph: Dict, nodes: List[Dict]) -> Dict[str, List[str]]:
        """Build dependency edges from symbol relationships."""
        graph = defaultdict(list)
        
        node_order = {n.get("id"): i for i, n in enumerate(nodes)}
        
        for node in nodes:
            node_id = node.get("id", "")
            sym = symbol_graph.get(node_id, {})
            
            if sym.get("children"):
                for child_id in sym.get("children", []):
                    graph[child_id].append(node_id)
            else:
                graph[node_id] = []
        
        for node in nodes:
            node_id = node.get("id", "")
            label = node.get("label", "")
            
            if node_id not in graph:
                graph[node_id] = []
            
            if "+" in label or "-" in label:
                for other in nodes:
                    if other.get("id") != node_id:
                        other_label = other.get("label", "")
                        if any(t in other_label for t in ["a", "b", "x", "y"] if t in label):
                            if other.get("id") in graph and node_id not in graph[other.get("id")]:
                                graph[other.get("id")].append(node_id)
        
        return dict(graph)
    
    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Kahn's algorithm for topological sort."""
        in_degree = defaultdict(int)
        all_nodes = set(graph.keys())
        
        for node, deps in graph.items():
            if node not in in_degree:
                in_degree[node] = 0
            for dep in deps:
                in_degree[dep] = in_degree.get(dep, 0) + 1
        
        queue = deque([n for n, d in in_degree.items() if d == 0])
        order = []
        
        while queue:
            node = queue.popleft()
            order.append(node)
            
            for neighbor, deps in graph.items():
                if node in deps:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        missing = all_nodes - set(order)
        for m in missing:
            order.append(m)
        
        return order
    
    def _compute_frames(self, order: List[str], graph: Dict[str, List[str]]) -> Dict[str, int]:
        """Compute frame offsets from dependency depth - parallel when same depth."""
        depth_map = {}
        
        for node in order:
            deps = graph.get(node, [])
            if not deps:
                depth_map[node] = 0
            else:
                max_depth = 0
                for dep in deps:
                    if dep in depth_map:
                        max_depth = max(max_depth, depth_map[dep] + 1)
                depth_map[node] = max_depth
        
        frame_map = {}
        for node in order:
            depth = depth_map.get(node, 0)
            frame_map[node] = depth * self.frame_unit
        
        return frame_map
    
    def detect_overlaps(self, frame_assignments: Dict[str, int]) -> List[Dict]:
        """Detect and report frame overlaps."""
        overlaps = []
        
        for node_a, frame_a in frame_assignments.items():
            for node_b, frame_b in frame_assignments.items():
                if node_a != node_b:
                    if (frame_a < frame_b + self.frame_unit and 
                        frame_a + self.frame_unit > frame_b):
                        overlaps.append({
                            "nodes": [node_a, node_b],
                            "frame_a": frame_a,
                            "frame_b": frame_b
                        })
        
        return overlaps


def solve_timeline(cir: Dict, normalized: Optional[Dict] = None) -> Dict:
    """Convenience function."""
    return DeterministicTimelineSolver().solve(cir, normalized)