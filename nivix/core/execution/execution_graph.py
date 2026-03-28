# Nivix Execution Graph Builder v5.0
# Merges solver outputs into deterministic execution plan

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field

@dataclass
class ExecutionNode:
    """Executable node in the execution graph."""
    id: str
    type: str  # shape, text, math, highlight
    spawn_frame: int = 0
    destroy_frame: int = 120
    position: Tuple[float, float] = (0.0, 0.0)
    transforms: List[Dict[str, Any]] = field(default_factory=list)
    focus_score: float = 0.0
    role: str = "context"  # subject, result, context

@dataclass 
class DependencyEdge:
    """Temporal/spatial dependency between nodes."""
    from_node: str
    to_node: str
    type: str  # AFTER, WITH, SYNCHRONIZED, EXCLUDES
    constraint: Optional[Dict[str, Any]] = None

@dataclass
class FocusWindow:
    """Attention focus window."""
    node_id: str
    start_frame: int
    end_frame: int
    zoom: float = 1.0
    emphasis: str = "normal"  # normal, highlight, transition

@dataclass
class CameraTarget:
    """Camera position target."""
    focus_node: Optional[str] = None
    position: Tuple[float, float] = (0.0, 0.0)
    zoom: float = 1.0
    start_frame: int = 0
    end_frame: int = 120

class ExecutionGraph:
    """
    Unified execution plan combining all solver outputs.
    
    Merges:
        - intent_graph (WHY)
        - position_map (WHERE)
        - frame_schedule (WHEN)
        - camera_targets (HOW)
    
    Produces:
        - executable execution_graph
        - dependency_edges
        - focus_windows
        - camera_timeline
    """
    
    def __init__(self):
        self.nodes: Dict[str, ExecutionNode] = {}
        self.dependencies: List[DependencyEdge] = []
        self.focus_windows: List[FocusWindow] = []
        self.camera_targets: List[CameraTarget] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_node(self, node: ExecutionNode) -> None:
        self.nodes[node.id] = node
    
    def add_dependency(self, dep: DependencyEdge) -> None:
        self.dependencies.append(dep)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for CIR."""
        return {
            "execution_graph": {
                "nodes": {
                    nid: {
                        "type": n.type,
                        "spawn_frame": n.spawn_frame,
                        "destroy_frame": n.destroy_frame,
                        "position": {"x": n.position[0], "y": n.position[1]},
                        "transforms": n.transforms,
                        "focus_score": n.focus_score,
                        "role": n.role
                    }
                    for nid, n in self.nodes.items()
                },
                "dependencies": [
                    {"from": d.from_node, "to": d.to_node, "type": d.type}
                    for d in self.dependencies
                ],
                "focus_windows": [
                    {"node_id": fw.node_id, "start": fw.start_frame, "end": fw.end_frame, "zoom": fw.zoom, "emphasis": fw.emphasis}
                    for fw in self.focus_windows
                ],
                "camera_targets": [
                    {"focus_node": ct.focus_node, "position": {"x": ct.position[0], "y": ct.position[1]}, 
                     "zoom": ct.zoom, "start": ct.start_frame, "end": ct.end_frame}
                    for ct in self.camera_targets
                ]
            },
            "metadata": self.metadata
        }


def build_execution_graph(cir: Dict[str, Any]) -> ExecutionGraph:
    """
    Build execution graph from solved CIR.
    
    Pipeline:
        1. Merge nodes from CIR with position_map
        2. Add frame_schedule timing
        3. Attach intent roles and focus scores
        4. Build dependency edges
        5. Extract focus windows
    """
    print("--- [EXECUTION GRAPH] Building from solved CIR ---")
    
    graph = ExecutionGraph()
    
    # 1. Get solver outputs
    position_map = cir.get("_position_map", {})
    frame_schedule = cir.get("_frame_schedule", {})
    intent_graph = cir.get("_intent_graph", {})
    roles = intent_graph.get("roles", {})
    focus_scores = intent_graph.get("focus_scores", {})
    relationships = intent_graph.get("relationships", [])
    
    # 2. Build nodes
    nodes = cir.get("nodes", [])
    for node in nodes:
        node_id = node.get("id", "")
        nid = node.get("id", "")
        
        # Get timing from frame_schedule or default
        if node_id in frame_schedule:
            start, end = frame_schedule[node_id]
        else:
            lifecycle = node.get("lifecycle", {})
            start = lifecycle.get("spawn", 0)
            end = lifecycle.get("destroy", 120)
        
        # Get position from layout_solver
        position = position_map.get(node_id, (0.0, 0.0))
        
        # Get role from intent_resolver
        role = roles.get(node_id, "context")
        
        # Get focus score
        focus_score = focus_scores.get(node_id, 0.5)
        
        exec_node = ExecutionNode(
            id=node_id,
            type=node.get("type", "object"),
            spawn_frame=start,
            destroy_frame=end,
            position=position,
            focus_score=focus_score,
            role=role
        )
        
        graph.add_node(exec_node)
    
    # 3. Build dependencies from relationships
    for rel in relationships:
        dep = DependencyEdge(
            from_node=rel.get("node_a", ""),
            to_node=rel.get("node_b", ""),
            type=rel.get("type", "WITH").upper()
        )
        graph.add_dependency(dep)
    
    # 4. Build focus windows from attention
    attention = cir.get("attention", [])
    for focus in attention:
        fw = FocusWindow(
            node_id=focus.get("node_id", ""),
            start_frame=focus.get("start_frame", 0),
            end_frame=focus.get("end_frame", 120),
            zoom=focus.get("camera_params", {}).get("zoom", 1.0),
            emphasis="highlight" if focus.get("focus_score", 0) > 0.7 else "normal"
        )
        graph.focus_windows.append(fw)
    
    # 5. Extract metadata
    graph.metadata = {
        "prompt": cir.get("meta", {}).get("prompt", ""),
        "template": cir.get("meta", {}).get("template", ""),
        "solver_version": "5.0"
    }
    
    print(f"--- [EXECUTION GRAPH] Built {len(graph.nodes)} nodes, {len(graph.dependencies)} dependencies ---")
    
    return graph


def merge_with_camera(cir: Dict[str, Any]) -> ExecutionGraph:
    """Build execution graph including camera targets."""
    graph = build_execution_graph(cir)
    
    # Add camera targets from attention/camera entries
    attention = cir.get("attention", [])
    if attention:
        for focus in attention:
            ct = CameraTarget(
                focus_node=focus.get("node_id"),
                zoom=focus.get("camera_params", {}).get("zoom", 1.0),
                start_frame=focus.get("start_frame", 0),
                end_frame=focus.get("end_frame", 120)
            )
            graph.camera_targets.append(ct)
    
    return graph