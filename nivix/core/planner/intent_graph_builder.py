from core.planner.templates import get_scene_block

class IntentGraphBuilder:
    """
    Constructs a multi-scene intent graph for complex prompts.
    Translates high-level mission goals into a DAG of cinematic 'intent nodes'.
    """
    
    def build_graph(self, prompt, suggested_blocks=None):
        """
        Input: Prompt string, or a list of scene types from LLM.
        Output: { nodes, edges } Narrative Dependency Graph.
        """
        print(f"--- [NIVIX GRAPH] Building Narrative Dependency DAG for: {prompt[:30]}... ---")
        
        # 1. Blocks
        if not suggested_blocks:
            suggested_blocks = ["title_card", "concept_hook", "summary_recap"]
            
        nodes = []
        edges = []
        produced_capabilities = set()
        
        # 2. Composition with Dependency Resolution
        for i, block_type in enumerate(suggested_blocks):
            base_node = get_scene_block(block_type)
            node_id = f"scene_{i}"
            
            node = {
                "id": node_id,
                "scene_type": base_node["type"],
                "goal": base_node["goal"],
                "visual_priority": base_node["visual_priority"],
                "camera_strategy": base_node["camera_strategy"],
                "instruction": f"Pedagogical focus: {block_type}",
                "requires": base_node.get("requires", []),
                "produces": base_node.get("produces", [])
            }
            nodes.append(node)
            
            # 3. Dynamic Edge Matching (v2.3 Dependency Logic)
            # Find previous nodes that satisfy our requirements
            for req in node["requires"]:
                 for prev in nodes[:-1]:
                      if req in prev["produces"]:
                           edges.append([prev["id"], node_id])
            
            # Linear narrative fallback (If no dependency edges, follow previous)
            if i > 0 and not any(e[1] == node_id for e in edges):
                 edges.append([nodes[i-1]["id"], node_id])
                 
        return {
            "nodes": nodes,
            "edges": edges
        }

def compose_graph(prompt, suggested_blocks=None):
    return IntentGraphBuilder().build_graph(prompt, suggested_blocks)
