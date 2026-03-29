from nivix.core.planner.planner_router import route_planning
from nivix.core.planner.object_graph_builder import build_objects
from nivix.core.planner.transformation_graph_builder import build_transforms
from nivix.core.planner.attention_graph_builder import build_attention_plan

class SemanticPlanner:
    """
    Orchestrates the strategic planning of animation intent using a Cinematic Execution Graph.
    """
    def plan(self, prompt):
        # 1. ROUTE intent through fallback-aware Narrative Graph builder
        # Returns: { plan: { topic, intent_graph, lesson_type }, confidence, model, depth }
        result = route_planning(prompt)
        
        # 2. Extract Narrative Plan (Dependency Graph structure)
        plan_data = result["plan"]
        topic = plan_data.get("topic")
        intent_graph = plan_data.get("intent_graph")
        
        # 3. Build GLOBAL OBJECT GRAPH (v2.3)
        # We define objects BEFORE scene detailing to ensure cross-scene stability.
        objects = build_objects(topic, intent_graph["nodes"])
        plan_data["global_objects"] = objects
        
        # 4. Build TRANSFORMATION GRAPH (v2.4)
        # Models object lifecycle state transitions (before/after/morph).
        transforms = build_transforms(objects, intent_graph)
        plan_data["transformation_graph"] = transforms
        
        # 5. Build ATTENTION GAZE GRAPH (v2.6)
        # Predicts viewer gazepoints based on cinematic intent & state changes.
        attention = build_attention_plan(intent_graph, objects, transforms)
        plan_data["attention_plan"] = attention
        
        # 6. Patching & Validation (Narrative Safety Layer)
        intent_graph["nodes"] = self._apply_narrative_safety(intent_graph["nodes"], topic)
        
        # 7. SEMANTIC TIMING ESTIMATION (v2.4)
        # Predict duration for each scene based on intent/complexity.
        self._estimate_semantic_durations(intent_graph["nodes"])
        
        # 8. Dependency Validation
        self._validate_dependencies(intent_graph)
        
        # 9. COMPILER NORMALIZATION (v2.7)
        # Convert multi-graph symbolic structure into Canonical IR (CIR)
        from nivix.core.compiler.cir import create_cir
        cir_plan = create_cir(plan_data)
        
        # 10. CIR OPTIMIZATION PASSES (v2.7)
        # Strategic refinement on standardized execution primitives
        from nivix.core.compiler.pass_manager import optimize_cir
        optimized_cir = optimize_cir(cir_plan.to_dict(), backend="manim")
        
        # 11. Attach Confidence & Result
        plan_data["cir"] = optimized_cir
        plan_data["metadata"] = {
            "confidence": result["confidence"],
            "model_used": result["model"],
            "fallback_depth": result["fallback_depth"]
        }
        
        print(f"--- [NIVIX STRATEGY] Optimized CIR Finalized via {result['model']} ---")
        return plan_data

    def _estimate_semantic_durations(self, nodes):
        """Calculates narrative-based duration hints for the scheduler."""
        for node in nodes:
             # Basic Complexity Estimation Heuristic
             s_type = node.get("scene_type", "concept_intro")
             duration = {
                 "title": 2.5,
                 "equation": 4.5,
                 "transformation": 6.0,
                 "visualization": 5.5,
                 "comparison": 4.0,
                 "summary": 3.0
             }.get(s_type, 3.5)
             
             node["duration_hint"] = duration

    def _validate_dependencies(self, graph):
        """Topological integrity check for cinematic flow."""
        nodes = graph["nodes"]
        edges = graph["edges"]
        if not nodes: return
        
        for i, node in enumerate(nodes[1:]): # Skip title
             if not any(e[1] == node["id"] for e in edges):
                  edges.append([nodes[i]["id"], node["id"]])

    def _apply_narrative_safety(self, nodes, topic):
        """Rule Engine: Enforces pedagogical flow across the narrative chain."""
        if not nodes: return nodes
        
        # Rule: Always title-first
        if nodes[0].get("scene_type") != "title":
            from nivix.core.planner.templates import get_scene_block
            title_node = {
                "id": "scene_safety_title",
                "scene_type": "title",
                "goal": "identify_topic",
                "visual_priority": "high",
                "camera_strategy": "static_center",
                "instruction": f"Introduce the concept of {topic}"
            }
            nodes.insert(0, title_node)
            
        # Rule: Always summary-last
        if nodes[-1].get("scene_type") != "summary":
            summary_node = {
                "id": "scene_safety_summary",
                "scene_type": "summary",
                "goal": "final_takeaway",
                "visual_priority": "medium",
                "camera_strategy": "zoom_out_wide",
                "instruction": "Recap the core learning objective"
            }
            nodes.append(summary_node)
             
        return nodes

def plan_intent(prompt):
    return SemanticPlanner().plan(prompt)
