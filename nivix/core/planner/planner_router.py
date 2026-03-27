import json
from core.fallback.loader import call_with_fallback
from core.planner.templates import get_scene_block, list_scene_types
from core.planner.intent_graph_builder import compose_graph

class PlannerRouter:
    """
    Acts as the entry point for lesson strategy. 
    Routes high-level intent to the best available LLM or Template for planning.
    """
    
    # Model Configuration by Fallback Stage
    FALLBACK_CHAIN = [
        {"model": "gpt-class", "level": 0},
        {"model": "mixtral-class", "level": 1},
        {"model": "rule-based-safety", "level": 2} # Final safety fallback
    ]

    def plan_intent(self, prompt):
        """
        Coordinates the planning process with a focus on narrative graph construction.
        Returns: { plan, confidence, model, fallback_depth }
        """
        print(f"\n--- [NIVIX ROUTER] Constructing Narrative Graph for: '{prompt[:40]}...' ---")
        
        # 1. Attempt Multi-Model Fallback
        for stage in self.FALLBACK_CHAIN:
            model = stage["model"]
            level = stage["level"]
            
            try:
                # SPECIAL: Rule-based safety fallback (Stage 2)
                if model == "rule-based-safety":
                    return self._safety_plan(prompt, level)
                
                # LLM PLanning (Stage 0-1)
                plan_data = self._llm_graph_planning(prompt, model)
                
                # Construct THE INTENT GRAPH (v2.2 Architecture)
                intent_graph = compose_graph(prompt, plan_data.get("suggested_scenes"))
                
                confidence = self._calculate_confidence(intent_graph, level)
                
                return {
                    "plan": {
                        "topic": prompt,
                        "intent_graph": intent_graph,
                        "lesson_type": plan_data.get("lesson_type", "explainer")
                    },
                    "confidence": confidence,
                    "model": model,
                    "fallback_depth": level
                }
                
            except Exception as e:
                print(f"--- [ROUTER] Stage {level} ({model}) Failed: {e} ---")
        
        # Hard-coded safety if all loops fail
        return self._safety_plan(prompt, 2)

    def _llm_graph_planning(self, prompt, model):
        """Dispatches to the fallback loader to get a narrative structure."""
        available_types = list_scene_types()
        
        planner_prompt = f"""
Task: Decompose a high-level educational intent into a pedagogical sequence.
User Intent: {prompt}
Available Atomic Scene Types: {available_types}

Rules:
1. Every plan must start with a 'title_card' and end with 'summary_recap'.
2. If multiple concepts are mentioned, include a 'concept_comparison'.
3. For math, include 'equation_intro' and 'step_derivation'.

Schema (JSON only):
{{
  "lesson_type": "multi_concept | single_concept | derivation",
  "suggested_scenes": ["title_card", "concept_hook", "...", "summary_recap"]
}}
"""
        from core.parser.request import send_request
        response = send_request(model, planner_prompt)
        return json.loads(response)

    def _calculate_confidence(self, graph, level):
        """Returns a score from 0.0 to 1.0 based on graph depth and fallback source."""
        score = 1.0 - (level * 0.2)
        if len(graph) < 3: score -= 0.1
        return max(score, 0.1)

    def _safety_plan(self, prompt, level):
        """The final deterministic fallback if all LLMs fail."""
        print("--- [ROUTER] CRITICAL: Using Deterministic Safety Graph ---")
        safe_scenes = ["title_card", "concept_hook", "equation_intro", "summary_recap"]
        intent_graph = compose_graph(prompt, safe_scenes)
        return {
            "plan": {
                "topic": prompt,
                "intent_graph": intent_graph,
                "lesson_type": "standard_safety"
            },
            "confidence": 0.4,
            "model": "rule-based-safety",
            "fallback_depth": level
        }

def route_planning(prompt):
    return PlannerRouter().plan_intent(prompt)
