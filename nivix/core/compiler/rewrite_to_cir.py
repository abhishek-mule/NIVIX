# Nivix Rewrite to CIR Compiler v6.4
# Bridge between algebraic rewrite engine and CIR timeline

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class CIREntity:
    """CIR entity (node in timeline)."""
    id: str
    type: str = "text"
    spawn_frame: int = 0
    destroy_frame: Optional[int] = None
    position: tuple = (0.0, 0.0)

@dataclass
class CIRTransform:
    """CIR transform (animation)."""
    node_id: str
    action: str
    start_frame: int
    end_frame: int
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CIRAttention:
    """CIR attention/focus."""
    node_id: str
    focus_score: float
    start_frame: int
    end_frame: int
    camera_params: Dict[str, Any] = field(default_factory=dict)

class RewriteToCIRCompiler:
    """
    Converts rewrite engine outputs into CIR timeline.
    
    Rewrite steps:
        [
            {step:1, action:"show", target:"a^2"},
            {step:2, action:"show", target:"2ab"},
            ...
        ]
    
    CIR entities:
        - nodes with lifecycles
        - transforms with timing
        - attention with focus scores
        - camera actions
    
    Enables automatic derivation animations.
    """
    
    def __init__(self):
        self.frame_duration = 15  # frames per step
        self.default_destroy = 90
    
    def compile(self, rewrite_steps: List[Dict], meta: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Compile rewrite steps into CIR.
        
        Args:
            rewrite_steps: Output from AlgebraicRewriter
            meta: Optional metadata (prompt, task, etc.)
        
        Returns:
            Complete CIR ready for rendering
        """
        print("--- [REWRITE->CIR] Compiling derivation to CIR ---")
        
        cir = {
            "nodes": [],
            "transforms": [],
            "constraints": [],
            "attention": [],
            "meta": meta or {}
        }
        
        current_frame = 0
        entities_by_type = {}
        
        for step in rewrite_steps:
            action = step.get("action", "show")
            target = step.get("target", "")
            
            if action == "show":
                node = self._create_entity(target, current_frame)
                cir["nodes"].append(node)
                entities_by_type[target] = node
                
                current_frame += self.frame_duration
            
            elif action == "fade_out":
                node_id = self._find_node_id(target, cir["nodes"])
                if node_id:
                    transform = {
                        "node_id": node_id,
                        "action": "fade_out",
                        "start_frame": current_frame,
                        "end_frame": current_frame + 10
                    }
                    cir["transforms"].append(transform)
                    current_frame += 10
            
            elif action == "combine":
                node = self._create_entity(target, current_frame)
                cir["nodes"].append(node)
                
                transform = {
                    "node_id": node["id"],
                    "action": "combine",
                    "start_frame": current_frame,
                    "end_frame": current_frame + self.frame_duration
                }
                cir["transforms"].append(transform)
                
                current_frame += self.frame_duration
        
        cir["attention"] = self._generate_attention(cir["nodes"])
        
        print(f"--- [REWRITE->CIR] Generated {len(cir['nodes'])} nodes, {len(cir['transforms'])} transforms")
        
        return cir
    
    def _create_entity(self, target: str, spawn_frame: int) -> Dict[str, Any]:
        """Create CIR node from target string."""
        node_id = self._sanitize_id(target)
        
        node_type = "text"
        if "^2" in target or "^" in target:
            node_type = "text"
        elif any(op in target for op in ["+", "-", "*"]):
            node_type = "text"
        
        return {
            "id": node_id,
            "type": node_type,
            "label": target,
            "lifecycle": {
                "spawn": spawn_frame,
                "destroy": spawn_frame + self.default_destroy
            }
        }
    
    def _find_node_id(self, target: str, nodes: List[Dict]) -> Optional[str]:
        """Find node ID by target label."""
        san_target = self._sanitize_id(target)
        for node in nodes:
            if node.get("label", "").replace(" ", "") in target.replace(" ", ""):
                return node.get("id")
        return None
    
    def _sanitize_id(self, target: str) -> str:
        """Convert target string to valid ID."""
        return target.replace(" ", "").replace("^", "pow").replace("+", "plus").replace("-", "minus").replace("*", "mul")
    
    def _generate_attention(self, nodes: List[Dict]) -> List[Dict]:
        """Generate attention/focus from nodes."""
        attention = []
        
        for i, node in enumerate(nodes):
            label = node.get("label", "")
            spawn = node.get("lifecycle", {}).get("spawn", 0)
            
            focus_score = 1.0 if i == len(nodes) - 1 else 0.6
            
            cam_params = {}
            if i == 0:
                cam_params = {"zoom": 1.3}
            elif "combine" in label:
                cam_params = {"zoom": 1.5}
            
            attention.append({
                "node_id": node.get("id"),
                "focus_score": focus_score,
                "start_frame": spawn,
                "end_frame": spawn + 30,
                "camera_params": cam_params
            })
        
        return attention
    
    def compile_derivation(self, expression: str) -> Dict[str, Any]:
        """Convenience: Parse -> Rewrite -> CIR in one call."""
        from nivix.core.parser.expression_parser import parse_expression
        from nivix.core.rewrite import AlgebraicRewriter
        
        ast = parse_expression(expression)
        rewriter = AlgebraicRewriter()
        rewritten = rewriter.rewrite(ast.to_dict())
        
        steps = rewritten.get("animation_steps", [])
        meta = {"prompt": expression, "task": "derivation", "formula": rewritten.get("formula", expression)}
        
        return self.compile(steps, meta)


def compile_rewrite_to_cir(rewrite_steps: List[Dict], meta: Optional[Dict] = None) -> Dict[str, Any]:
    """Convenience function."""
    return RewriteToCIRCompiler().compile(rewrite_steps, meta)