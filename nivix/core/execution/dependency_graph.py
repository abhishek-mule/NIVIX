# Nivix Dependency Graph Builder v5.0
# Constructs deterministic DAG from node relationships for compiler-grade scheduling

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

class DependencyType(Enum):
    """Semantic dependency types."""
    AFTER = "AFTER"           # B starts after A ends
    BEFORE = "BEFORE"         # B starts before A ends
    WITH = "WITH"             # Simultaneous
    SYNCHRONIZED = "SYNCHRONIZED"  # Exact same timing
    DURING = "DURING"          # B fully contained in A
    CONTAINS = "CONTAINS"      # A fully contains B
    EXCLUDES = "EXCLUDES"      # Cannot overlap
    CENTER_WITH = "CENTER_WITH"    # Center alignment

@dataclass
class DAGNode:
    """Node in the execution DAG."""
    id: str
    type: str
    spawn_frame: int = 0
    destroy_frame: int = 120
    position: Tuple[float, float] = (0.0, 0.0)
    role: str = "context"
    focus_score: float = 0.5
    in_degree: int = 0
    out_edges: List[str] = field(default_factory=list)

@dataclass
class DependencyEdge:
    """Directed edge in DAG."""
    from_node: str
    to_node: str
    dep_type: DependencyType
    constraint: Optional[Dict[str, Any]] = None

class DependencyGraph:
    """
    Directed Acyclic Graph (DAG) for deterministic execution.
    
    Transforms:
        - Node relationships -> DAG edges
        - Temporal constraints -> Topological order
        - Parallel execution groups
    
    Enables:
        - Parallel reasoning-safe scheduling
        - Auto-layout timing correction
        - Multi-track composition stability
    """
    
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
        self.edges: List[DependencyEdge] = []
        self.execution_order: List[str] = []
        self.parallel_tracks: List[List[str]] = []
        self.cycle_detected: bool = False
    
    def add_node(self, node: DAGNode) -> None:
        self.nodes[node.id] = node
    
    def add_edge(self, edge: DependencyEdge) -> None:
        self.edges.append(edge)
        
        if edge.from_node in self.nodes:
            self.nodes[edge.from_node].out_edges.append(edge.to_node)
        if edge.to_node in self.nodes:
            self.nodes[edge.to_node].in_degree += 1
    
    def _topological_sort(self) -> List[str]:
        """Kahn's algorithm for topological sort."""
        in_degree = {nid: n.in_degree for nid, n in self.nodes.items()}
        queue = deque([nid for nid, d in in_degree.items() if d == 0])
        result = []
        
        while queue:
            node_id = queue.popleft()
            result.append(node_id)
            
            for neighbor in self.nodes[node_id].out_edges:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self.nodes):
            self.cycle_detected = True
            return list(self.nodes.keys())
        
        return result
    
    def _compute_parallel_tracks(self) -> List[List[str]]:
        """Group nodes that can execute in parallel."""
        tracks = []
        assigned = set()
        
        for node_id in self.execution_order:
            if node_id in assigned:
                continue
            
            track = [node_id]
            assigned.add(node_id)
            
            node = self.nodes[node_id]
            spawn = node.spawn_frame
            destroy = node.destroy_frame
            
            for other_id in self.execution_order:
                if other_id in assigned:
                    continue
                
                other = self.nodes[other_id]
                other_spawn = other.spawn_frame
                other_destroy = other.destroy_frame
                
                can_parallel = True
                for edge in self.edges:
                    if edge.from_node == other_id and edge.to_node == node_id:
                        if edge.dep_type in [DependencyType.AFTER, DependencyType.BEFORE]:
                            can_parallel = False
                    if edge.from_node == node_id and edge.to_node == other_id:
                        if edge.dep_type in [DependencyType.AFTER, DependencyType.BEFORE]:
                            can_parallel = False
                
                if can_parallel and not (other_spawn < destroy and other_destroy > spawn):
                    track.append(other_id)
                    assigned.add(other_id)
            
            if track:
                tracks.append(track)
        
        return tracks
    
    def build(self, cir: Dict[str, Any]) -> "DependencyGraph":
        """Build DAG from CIR."""
        print("--- [DEPENDENCY GRAPH] Building from CIR ---")
        
        graph = DependencyGraph()
        
        nodes = cir.get("nodes", [])
        position_map = cir.get("_position_map", {})
        frame_schedule = cir.get("_frame_schedule", {})
        intent_graph = cir.get("_intent_graph", {})
        roles = intent_graph.get("roles", {})
        focus_scores = intent_graph.get("focus_scores", {})
        
        for node in nodes:
            node_id = node.get("id", "")
            
            schedule = frame_schedule.get(node_id, (0, 120))
            position = position_map.get(node_id, (0.0, 0.0))
            role = roles.get(node_id, "context")
            focus = focus_scores.get(node_id, 0.5)
            
            dag_node = DAGNode(
                id=node_id,
                type=node.get("type", "object"),
                spawn_frame=schedule[0],
                destroy_frame=schedule[1],
                position=position,
                role=role,
                focus_score=focus
            )
            graph.add_node(dag_node)
        
        relationships = intent_graph.get("relationships", [])
        for rel in relationships:
            dep_type = DependencyType.WITH
            if rel.get("type", "").upper() in [e.value for e in DependencyType]:
                dep_type = DependencyType(rel.get("type", "").upper())
            
            edge = DependencyEdge(
                from_node=rel.get("node_a", ""),
                to_node=rel.get("node_b", ""),
                dep_type=dep_type
            )
            graph.add_edge(edge)
        
        constraints = cir.get("constraints", [])
        for c in constraints:
            ctype = c.get("type", "")
            nodes_list = c.get("nodes", [])
            
            if ctype == "hierarchical" and len(nodes_list) >= 2:
                for i in range(len(nodes_list) - 1):
                    edge = DependencyEdge(
                        from_node=nodes_list[i],
                        to_node=nodes_list[i + 1],
                        dep_type=DependencyType.AFTER
                    )
                    graph.add_edge(edge)
            
            elif ctype == "alignment" and len(nodes_list) >= 2:
                edge = DependencyEdge(
                    from_node=nodes_list[0],
                    to_node=nodes_list[1],
                    dep_type=DependencyType.WITH
                )
                graph.add_edge(edge)
        
        graph.execution_order = graph._topological_sort()
        graph.parallel_tracks = graph._compute_parallel_tracks()
        
        print(f"--- [DEPENDENCY GRAPH] Built {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        print(f"--- [DEPENDENCY GRAPH] Execution order: {' -> '.join(graph.execution_order)}")
        print(f"--- [DEPENDENCY GRAPH] Parallel tracks: {len(graph.parallel_tracks)}")
        
        return graph
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "dependency_graph": {
                "nodes": {
                    nid: {
                        "type": n.type,
                        "spawn_frame": n.spawn_frame,
                        "destroy_frame": n.destroy_frame,
                        "position": {"x": n.position[0], "y": n.position[1]},
                        "role": n.role,
                        "focus_score": n.focus_score,
                        "out_edges": n.out_edges
                    }
                    for nid, n in self.nodes.items()
                },
                "edges": [
                    {"from": e.from_node, "to": e.to_node, "type": e.dep_type.value}
                    for e in self.edges
                ],
                "execution_order": self.execution_order,
                "parallel_tracks": self.parallel_tracks,
                "cycle_detected": self.cycle_detected
            }
        }


def build_dependency_graph(cir: Dict[str, Any]) -> DependencyGraph:
    """Build dependency graph from CIR."""
    graph = DependencyGraph()
    return graph.build(cir)