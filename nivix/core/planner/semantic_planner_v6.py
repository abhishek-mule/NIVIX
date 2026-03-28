# Nivix Semantic Planner v6.0
# Automatic animation reasoning from natural language prompts

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class TaskType(Enum):
    """Animation task types."""
    DERIVE = "derive"           # Mathematical derivation
    COMPARE = "compare"        # Comparison between items
    EXPLAIN = "explain"       # Explanation flow
    HIGHLIGHT = "highlight"  # Feature highlight
    TRANSFORM = "transform"   # Shape/content transformation
    SEQUENCE = "sequence"      # Step-by-step process

@dataclass
class AnimationStep:
    """Single animation step in plan."""
    step_id: int
    action: str
    target: str
    transition: str = "fade"
    camera: str = "static"

class SemanticPlannerV6:
    """
    Automatically expands natural language prompts into CIR components.
    
    Input:
        "derive 3/4"
        "compare A and B"
        "explain how photosynthesis works"
    
    Output:
        nodes, constraints, attention, animation_steps
    
    Pipeline:
        Prompt -> Task Detection -> Node Expansion -> Constraint Generation -> Animation Steps
    """
    
    def __init__(self):
        self.task_type: TaskType = TaskType.SEQUENCE
    
    def plan(self, prompt: str) -> Dict[str, Any]:
        """
        Main planning entry point.
        """
        prompt_lower = prompt.lower().strip()
        
        print(f"--- [SEMANTIC PLANNER] Analyzing: {prompt} ---")
        
        self.task_type = self._detect_task(prompt_lower)
        print(f"--- [SEMANTIC PLANNER] Task: {self.task_type.value} ---")
        
        if self.task_type == TaskType.DERIVE:
            return self._plan_derivation(prompt_lower)
        elif self.task_type == TaskType.COMPARE:
            return self._plan_comparison(prompt_lower)
        elif self.task_type == TaskType.EXPLAIN:
            return self._plan_explanation(prompt_lower)
        elif self.task_type == TaskType.HIGHLIGHT:
            return self._plan_highlight(prompt_lower)
        elif self.task_type == TaskType.TRANSFORM:
            return self._plan_transform(prompt_lower)
        else:
            return self._plan_default(prompt_lower)
    
    def _detect_task(self, prompt: str) -> TaskType:
        """Detect animation task type from prompt."""
        if any(kw in prompt for kw in ["derive", "calculate", "compute", "solve", "result", "answer"]):
            return TaskType.DERIVE
        elif any(kw in prompt for kw in ["compare", "vs", "versus", "difference", "between"]):
            return TaskType.COMPARE
        elif any(kw in prompt for kw in ["explain", "how", "why", "what is"]):
            return TaskType.EXPLAIN
        elif any(kw in prompt for kw in ["highlight", "emphasize", "notice", "look at"]):
            return TaskType.HIGHLIGHT
        elif any(kw in prompt for kw in ["transform", "change", "morph", "convert"]):
            return TaskType.TRANSFORM
        else:
            return TaskType.SEQUENCE
    
    def _plan_derivation(self, prompt: str) -> Dict[str, Any]:
        """Plan mathematical derivation animation."""
        parts = prompt.replace("/", " ").replace("=", " ").split()
        nums = [p.strip() for p in parts if p.strip().isdigit() or p.strip().replace(".", "").isdigit()]
        
        if len(nums) >= 2:
            numerator = nums[0]
            denominator = nums[1]
            try:
                result = str(float(numerator) / float(denominator))
            except:
                result = "?"
        else:
            numerator = "a"
            denominator = "b"
            result = "a/b"
        
        nodes = [
            {"id": "numerator", "type": "text", "label": str(numerator), "lifecycle": {"spawn": 0}},
            {"id": "division", "type": "text", "label": "/", "lifecycle": {"spawn": 10}},
            {"id": "denominator", "type": "text", "label": str(denominator), "lifecycle": {"spawn": 20}},
            {"id": "equals", "type": "text", "label": "=", "lifecycle": {"spawn": 40}},
            {"id": "result", "type": "text", "label": result, "lifecycle": {"spawn": 50}}
        ]
        
        constraints = [
            {"type": "hierarchical", "nodes": ["numerator", "denominator"]},
            {"type": "alignment", "nodes": ["numerator", "equals", "result"], "params": {"axis": "horizontal"}}
        ]
        
        attention = [
            {"node_id": "numerator", "focus_score": 1.0, "start_frame": 0, "end_frame": 30, "camera_params": {"zoom": 1.5}},
            {"node_id": "denominator", "focus_score": 0.8, "start_frame": 20, "end_frame": 40},
            {"node_id": "result", "focus_score": 1.0, "start_frame": 50, "end_frame": 90, "camera_params": {"zoom": 1.5}}
        ]
        
        steps = [
            {"step_id": 1, "action": "spawn", "target": "numerator", "transition": "fade_in"},
            {"step_id": 2, "action": "spawn", "target": "division", "transition": "fade_in"},
            {"step_id": 3, "action": "spawn", "target": "denominator", "transition": "fade_in"},
            {"step_id": 4, "action": "spawn", "target": "equals", "transition": "fade_in"},
            {"step_id": 5, "action": "spawn", "target": "result", "transition": "scale_in", "camera": "zoom_in"}
        ]
        
        return {
            "nodes": nodes,
            "constraints": constraints,
            "attention": attention,
            "animation_steps": steps,
            "meta": {"task": "derivation", "formula": f"{numerator}/{denominator}={result}"}
        }
    
    def _plan_comparison(self, prompt: str) -> Dict[str, Any]:
        """Plan comparison animation."""
        items = prompt.replace("compare", "").replace("vs", " ").replace("versus", " ").replace("and", " ").split()
        items = [i.strip() for i in items if i.strip() and len(i.strip()) > 1]
        
        item_a = items[0] if items else "A"
        item_b = items[1] if len(items) > 1 else "B"
        
        nodes = [
            {"id": "item_a", "type": "text", "label": str(item_a), "lifecycle": {"spawn": 0}},
            {"id": "vs", "type": "text", "label": "vs", "lifecycle": {"spawn": 30}},
            {"id": "item_b", "type": "text", "label": str(item_b), "lifecycle": {"spawn": 30}}
        ]
        
        constraints = [
            {"type": "alignment", "nodes": ["item_a", "vs", "item_b"], "params": {"axis": "horizontal"}}
        ]
        
        attention = [
            {"node_id": "item_a", "focus_score": 1.0, "start_frame": 0, "end_frame": 45, "camera_params": {"zoom": 1.3}},
            {"node_id": "item_b", "focus_score": 1.0, "start_frame": 30, "end_frame": 90, "camera_params": {"zoom": 1.3}}
        ]
        
        steps = [
            {"step_id": 1, "action": "spawn", "target": "item_a", "transition": "fade_in"},
            {"step_id": 2, "action": "spawn", "target": "vs", "transition": "fade_in"},
            {"step_id": 3, "action": "spawn", "target": "item_b", "transition": "fade_in"},
            {"step_id": 4, "action": "highlight", "target": "item_a", "camera": "pan_left"},
            {"step_id": 5, "action": "highlight", "target": "item_b", "camera": "pan_right"}
        ]
        
        return {
            "nodes": nodes,
            "constraints": constraints,
            "attention": attention,
            "animation_steps": steps,
            "meta": {"task": "comparison", "items": [item_a, item_b]}
        }
    
    def _plan_explanation(self, prompt: str) -> Dict[str, Any]:
        """Plan explanation flow."""
        nodes = [
            {"id": "topic", "type": "text", "label": "Topic", "lifecycle": {"spawn": 0}},
            {"id": "explanation", "type": "text", "label": "Explanation", "lifecycle": {"spawn": 30}},
            {"id": "conclusion", "type": "text", "label": "Conclusion", "lifecycle": {"spawn": 60}}
        ]
        
        constraints = [
            {"type": "hierarchical", "nodes": ["topic", "explanation", "conclusion"]}
        ]
        
        attention = [
            {"node_id": "topic", "focus_score": 1.0, "start_frame": 0, "end_frame": 30},
            {"node_id": "explanation", "focus_score": 1.0, "start_frame": 30, "end_frame": 60},
            {"node_id": "conclusion", "focus_score": 1.0, "start_frame": 60, "end_frame": 90}
        ]
        
        steps = [
            {"step_id": 1, "action": "spawn", "target": "topic", "transition": "fade_in"},
            {"step_id": 2, "action": "spawn", "target": "explanation", "transition": "slide_in"},
            {"step_id": 3, "action": "spawn", "target": "conclusion", "transition": "scale_in"}
        ]
        
        return {"nodes": nodes, "constraints": constraints, "attention": attention, "animation_steps": steps, "meta": {"task": "explanation"}}
    
    def _plan_highlight(self, prompt: str) -> Dict[str, Any]:
        """Plan highlight animation."""
        nodes = [
            {"id": "feature", "type": "text", "label": "Feature", "lifecycle": {"spawn": 0}},
            {"id": "highlight_box", "type": "shape", "label": "Box", "lifecycle": {"spawn": 20}}
        ]
        
        attention = [
            {"node_id": "feature", "focus_score": 1.0, "start_frame": 0, "end_frame": 60, "camera_params": {"zoom": 1.5}}
        ]
        
        steps = [
            {"step_id": 1, "action": "spawn", "target": "feature", "transition": "fade_in"},
            {"step_id": 2, "action": "draw", "target": "highlight_box", "transition": "draw_in"}
        ]
        
        return {"nodes": nodes, "constraints": [], "attention": attention, "animation_steps": steps, "meta": {"task": "highlight"}}
    
    def _plan_transform(self, prompt: str) -> Dict[str, Any]:
        """Plan transformation animation."""
        nodes = [
            {"id": "from_shape", "type": "shape", "label": "Square", "lifecycle": {"spawn": 0}},
            {"id": "to_shape", "type": "shape", "label": "Circle", "lifecycle": {"spawn": 45}}
        ]
        
        constraints = [
            {"type": "alignment", "nodes": ["from_shape", "to_shape"]}
        ]
        
        attention = [
            {"node_id": "from_shape", "focus_score": 1.0, "start_frame": 0, "end_frame": 45},
            {"node_id": "to_shape", "focus_score": 1.0, "start_frame": 45, "end_frame": 90}
        ]
        
        steps = [
            {"step_id": 1, "action": "spawn", "target": "from_shape", "transition": "fade_in"},
            {"step_id": 2, "action": "morph", "target": "to_shape", "transition": "morph"}
        ]
        
        return {"nodes": nodes, "constraints": constraints, "attention": attention, "animation_steps": steps, "meta": {"task": "transform"}}
    
    def _plan_default(self, prompt: str) -> Dict[str, Any]:
        """Default plan."""
        nodes = [
            {"id": "obj1", "type": "text", "label": "Step 1", "lifecycle": {"spawn": 0}},
            {"id": "obj2", "type": "text", "label": "Step 2", "lifecycle": {"spawn": 30}}
        ]
        
        attention = [
            {"node_id": "obj1", "focus_score": 1.0, "start_frame": 0, "end_frame": 30},
            {"node_id": "obj2", "focus_score": 1.0, "start_frame": 30, "end_frame": 60}
        ]
        
        steps = [
            {"step_id": 1, "action": "spawn", "target": "obj1", "transition": "fade_in"},
            {"step_id": 2, "action": "spawn", "target": "obj2", "transition": "fade_in"}
        ]
        
        return {"nodes": nodes, "constraints": [], "attention": attention, "animation_steps": steps, "meta": {"task": "sequence"}}


def plan(prompt: str) -> Dict[str, Any]:
    """Convenience function."""
    return SemanticPlannerV6().plan(prompt)