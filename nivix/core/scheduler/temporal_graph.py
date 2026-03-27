# Nivix Temporal Dependency DAG
# Implements a topological scheduler to resolve complex animation ordering constraints.

class TemporalGraph:
    """
    Manages a directed acyclic graph of animation nodes and their dependencies.
    Used by the scheduler to calculate deterministic start times based on ordering constraints.
    """
    def __init__(self):
        self.nodes = {} # node_id -> {duration, start_time}
        self.edges = {} # node_id -> [list of dependencies]
        
    def add_node(self, node_id, duration=1.0):
        """Adds a node representating an animation step."""
        self.nodes[node_id] = {
            "duration": duration,
            "start_time": 0.0
        }
        
    def add_edge(self, dependency_id, target_id):
        """
        Adds a directed edge: dependency_id -> target_id.
        Meaning: target_id starts AFTER dependency_id finishes.
        """
        if target_id not in self.edges:
            self.edges[target_id] = []
        self.edges[target_id].append(dependency_id)
        
    def compute_all_start_times(self):
        """
        Topological scheduling pass. Calculates the start_time for every node
        to satisfy the constraint: start(B) = max(end(all_dependencies(B))).
        """
        # We use a simple iterative approach for the DAG
        # In a real compiler, we'd use Kahn's algorithm or DFS-based topo-sort.
        # But for animation graphs, recursive dependencies are rare and depth is low.
        
        visited = set()
        
        def resolve_node(node_id):
            if node_id in visited:
                return self.nodes[node_id]["start_time"]
            
            deps = self.edges.get(node_id, [])
            if not deps:
                self.nodes[node_id]["start_time"] = 0.0
            else:
                # Start time is the maximum of (start + duration) of all dependencies
                max_end = max(resolve_node(d) + self.nodes[d]["duration"] for d in deps)
                self.nodes[node_id]["start_time"] = max_end
                
            visited.add(node_id)
            return self.nodes[node_id]["start_time"]

        for node_id in self.nodes:
            resolve_node(node_id)
            
    def get_schedule(self):
        """Returns the fully resolved temporal schedule."""
        self.compute_all_start_times()
        return self.nodes
