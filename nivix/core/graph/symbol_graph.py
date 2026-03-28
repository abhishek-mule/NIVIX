# Nivix Symbol Graph Builder v6.0
# Semantic dependency graph for causal animation reasoning

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

class NodeType(Enum):
    """Symbol node types."""
    ENTITY = "entity"          # Primary objects (shapes, text)
    OPERATOR = "operator"      # Operations (divide, multiply)
    DERIVED = "derived"       # Computed values
    LITERAL = "literal"      # Constant values
    VARIABLE = "variable"    # Bindable symbols

@dataclass
class SymbolNode:
    """Symbol in the semantic graph."""
    id: str
    node_type: NodeType
    value: Any = None
    depends_on: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    derivation: Optional[str] = None

class SymbolGraph:
    """
    Semantic dependency graph encoding why elements appear.
    
    Transforms timeline structure into causal structure:
    - Temporal DAG: When things appear
    - Semantic DAG: Why things appear
    """
    
    def __init__(self):
        self.nodes: Dict[str, SymbolNode] = {}
        self.errors: List[str] = []
    
    def add_node(self, node: SymbolNode) -> None:
        self.nodes[node.id] = node
    
    def get_dependencies(self, node_id: str) -> List[str]:
        """Get all dependencies recursively."""
        if node_id not in self.nodes:
            return []
        node = self.nodes[node_id]
        deps = list(node.depends_on)
        for dep in node.depends_on:
            deps.extend(self.get_dependencies(dep))
        return deps
    
    def topological_order(self) -> List[str]:
        """Return nodes in dependency-respecting order."""
        in_degree = defaultdict(int)
        for nid, node in self.nodes.items():
            in_degree[nid] = 0
        
        for nid, node in self.nodes.items():
            for dep in node.depends_on:
                in_degree[dep] = in_degree.get(dep, 0) + 1
        
        queue = deque([n for n, d in in_degree.items() if d == 0])
        order = []
        
        while queue:
            node_id = queue.popleft()
            order.append(node_id)
            
            for nid, node in self.nodes.items():
                if node_id in node.depends_on:
                    in_degree[nid] -= 1
                    if in_degree[nid] == 0:
                        queue.append(nid)
        
        return order
    
    def validate(self) -> List[str]:
        """Detect cycles, unbound symbols, dangling references."""
        errors = []
        visited = set()
        visiting = set()
        
        def dfs(node_id: str):
            if node_id in visiting:
                errors.append(f"Circular dependency: {node_id}")
                return
            if node_id in visited:
                return
            
            visiting.add(node_id)
            
            for dep in self.nodes.get(node_id, SymbolNode("", NodeType.ENTITY)).depends_on:
                if dep not in self.nodes:
                    errors.append(f"Dangling reference: {node_id} depends on {dep}")
                else:
                    dfs(dep)
            
            visiting.remove(node_id)
            visited.add(node_id)
        
        for node_id in self.nodes:
            dfs(node_id)
        
        self.errors = errors
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "symbol_graph": {
                "nodes": {
                    nid: {
                        "type": n.node_type.value,
                        "value": n.value,
                        "depends_on": n.depends_on,
                        "properties": n.properties,
                        "derivation": n.derivation
                    }
                    for nid, n in self.nodes.items()
                },
                "topological_order": self.topological_order(),
                "validation_errors": self.errors
            }
        }


class SymbolGraphBuilder:
    """
    Converts CIR into semantic dependency graph.
    
    Each node carries:
      - id
      - type (entity, operator, derived, literal)
      - depends_on (list of upstream node ids)
      - properties (key-value bindings)
      - derivation (optional: expression that produced this node)
    """
    
    def __init__(self):
        self.graph = SymbolGraph()
    
    def build(self, cir: Dict[str, Any]) -> SymbolGraph:
        """Build symbol graph from CIR."""
        print("--- [SYMBOL GRAPH] Building from CIR ---")
        
        graph = SymbolGraph()
        
        nodes = cir.get("nodes", [])
        constraints = cir.get("constraints", [])
        
        for node in nodes:
            node_id = node.get("id", "")
            node_type = NodeType.ENTITY
            
            label = node.get("label", "")
            if label.isdigit():
                node_type = NodeType.LITERAL
            elif "/" in str(label) or "*" in str(label) or "+" in str(label):
                node_type = NodeType.OPERATOR
            
            symbol_node = SymbolNode(
                id=node_id,
                node_type=node_type,
                value=node.get("label")
            )
            graph.add_node(symbol_node)
        
        for constraint in constraints:
            ctype = constraint.get("type", "")
            nodes_list = constraint.get("nodes", [])
            
            if ctype == "hierarchical" and len(nodes_list) >= 2:
                parent = nodes_list[0]
                for child in nodes_list[1:]:
                    if child in graph.nodes and parent in graph.nodes:
                        graph.nodes[child].depends_on.append(parent)
            
            elif ctype == "alignment" and len(nodes_list) >= 2:
                for i in range(1, len(nodes_list)):
                    if nodes_list[i] in graph.nodes and nodes_list[0] in graph.nodes:
                        graph.nodes[nodes_list[i]].depends_on.append(nodes_list[0])
        
        validation_errors = graph.validate()
        
        print(f"--- [SYMBOL GRAPH] Built {len(graph.nodes)} nodes")
        print(f"--- [SYMBOL GRAPH] Topological order: {' -> '.join(graph.topological_order())}")
        
        if validation_errors:
            print(f"--- [SYMBOL GRAPH] Errors: {validation_errors}")
        else:
            print(f"--- [SYMBOL GRAPH] Validation: PASSED")
        
        return graph
    
    def _infer_math_dependencies(self, cir: Dict[str, Any]) -> None:
        """Infer mathematical dependencies from expressions."""
        meta = cir.get("meta", {})
        task = meta.get("task", "")
        
        if task == "derivation":
            formula = meta.get("formula", "")
            if "/" in formula:
                parts = formula.split("=")
                if len(parts) == 2:
                    result_id = "result"
                    if result_id in self.graph.nodes:
                        self.graph.nodes[result_id].node_type = NodeType.DERIVED
                        self.graph.nodes[result_id].derivation = formula
    
    def _infer_semantic_dependencies(self, cir: Dict[str, Any]) -> None:
        """Infer semantic role dependencies."""
        intent = cir.get("_intent_graph", {})
        roles = intent.get("roles", {})
        
        for node_id, role in roles.items():
            if node_id in self.graph.nodes:
                self.graph.nodes[node_id].properties["role"] = role
                
                if role == "result":
                    for other_id, other_role in roles.items():
                        if other_role in ["subject", "context"]:
                            if other_id in self.graph.nodes:
                                self.graph.nodes[node_id].depends_on.append(other_id)


def build_symbol_graph(cir: Dict[str, Any]) -> SymbolGraph:
    """Convenience function."""
    builder = SymbolGraphBuilder()
    return builder.build(cir)