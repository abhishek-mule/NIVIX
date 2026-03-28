# Nivix Camera Solver v5.0
# Semantic camera reasoning for cinematic execution

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class CameraMode(Enum):
    """Camera operation modes."""
    STATIC = "static"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    PAN = "pan"
    FOLLOW = "follow"
    EMPHASIS = "emphasis"
    TRANSITION = "transition"

@dataclass
class CameraAction:
    """Single camera action in timeline."""
    mode: CameraMode
    target_node: Optional[str] = None
    start_frame: int = 0
    end_frame: int = 30
    zoom_level: float = 1.0
    pan_offset: Tuple[float, float] = (0.0, 0.0)
    duration: float = 1.0

class CameraSolver:
    """
    Resolves camera intent from semantic relationships.
    
    Input:
        - Intent graph (subject, result, context roles)
        - Focus windows
        - Comparison/derive/emphasize intents
    
    Output:
        - Camera timeline with semantic actions
        - Zoom targets on emphasis moments
        - Pan paths between subjects
    """
    
    def __init__(self):
        self.actions: List[CameraAction] = []
        self.current_zoom = 1.0
        self.current_position = (0.0, 0.0)
    
    def _infer_camera_intent_from_prompt(self, cir: Dict[str, Any]) -> str:
        """Infer camera intent from prompt."""
        meta = cir.get("meta", {})
        prompt = meta.get("prompt", "").lower()
        
        if "compare" in prompt or "vs" in prompt:
            return "comparison"
        elif "derive" in prompt or "calculate" in prompt:
            return "derivation"
        elif "emphasize" in prompt or "highlight" in prompt:
            return "emphasis"
        elif "show" in prompt:
            return "reveal"
        else:
            return "overview"
    
    def _find_subject_node(self, intent_graph: Dict[str, Any]) -> Optional[str]:
        """Find the subject node (first focus)."""
        roles = intent_graph.get("roles", {})
        focus_scores = intent_graph.get("focus_scores", {})
        
        # First prioritize by role, then by focus score
        for node_id, role in roles.items():
            if role == "subject":
                return node_id
        
        # Fall back to highest focus
        if focus_scores:
            return max(focus_scores.keys(), key=lambda x: focus_scores.get(x, 0))
        return None
    
    def _find_result_node(self, intent_graph: Dict[str, Any]) -> Optional[str]:
        """Find the result node."""
        roles = intent_graph.get("roles", {})
        
        for node_id, role in roles.items():
            if role == "result":
                return node_id
        return None
    
    def _build_camera_actions(self, cir: Dict[str, Any]) -> List[CameraAction]:
        """Build camera actions based on intent."""
        camera_intent = self._infer_camera_intent_from_prompt(cir)
        intent_graph = cir.get("_intent_graph", {})
        
        actions = []
        
        if camera_intent == "comparison":
            # For comparison: focus subject first, then pan to show both
            subject = self._find_subject_node(intent_graph)
            if subject:
                actions.append(CameraAction(
                    mode=CameraMode.EMPHASIS,
                    target_node=subject,
                    start_frame=0,
                    end_frame=30,
                    zoom_level=1.5
                ))
                actions.append(CameraAction(
                    mode=CameraMode.PAN,
                    target_node=subject,
                    start_frame=30,
                    end_frame=60,
                    zoom_level=1.0
                ))
        
        elif camera_intent == "derivation":
            # For derivation: zoom subject -> show process -> zoom result
            subject = self._find_subject_node(intent_graph)
            result = self._find_result_node(intent_graph)
            
            if subject:
                actions.append(CameraAction(
                    mode=CameraMode.ZOOM_IN,
                    target_node=subject,
                    start_frame=0,
                    end_frame=30,
                    zoom_level=1.5
                ))
            
            if result:
                actions.append(CameraAction(
                    mode=CameraMode.ZOOM_IN,
                    target_node=result,
                    start_frame=60,
                    end_frame=90,
                    zoom_level=1.5
                ))
        
        elif camera_intent == "emphasis":
            # Direct emphasis on focus nodes
            focus_scores = intent_graph.get("focus_scores", {})
            for node_id, score in focus_scores.items():
                if score > 0.7:
                    actions.append(CameraAction(
                        mode=CameraMode.EMPHASIS,
                        target_node=node_id,
                        start_frame=0,
                        end_frame=30,
                        zoom_level=1.3
                    ))
        
        elif camera_intent == "reveal":
            # Reveal: start wide, zoom in to result
            result = self._find_result_node(intent_graph)
            if result:
                actions.append(CameraAction(
                    mode=CameraMode.ZOOM_IN,
                    target_node=result,
                    start_frame=30,
                    end_frame=60,
                    zoom_level=1.5
                ))
        
        else:
            # Default: overview
            actions.append(CameraAction(
                mode=CameraMode.STATIC,
                start_frame=0,
                end_frame=120,
                zoom_level=1.0
            ))
        
        return actions
    
    def solve(self, cir: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve camera intent and return CIR with camera_timeline.
        """
        print("--- [CAMERA SOLVER] Resolving camera intent ---")
        
        camera_intent = self._infer_camera_intent_from_prompt(cir)
        print(f"--- [CAMERA SOLVER] Intent detected: {camera_intent} ---")
        
        self.actions = self._build_camera_actions(cir)
        
        print(f"--- [CAMERA SOLVER] Generated {len(self.actions)} camera actions:")
        for action in self.actions:
            print(f"    {action.mode.value} on {action.target_node} @ [{action.start_frame}-{action.end_frame}] zoom={action.zoom_level}")
        
        # Build camera timeline
        camera_timeline = []
        for action in self.actions:
            camera_timeline.append({
                "mode": action.mode.value,
                "target_node": action.target_node,
                "start_frame": action.start_frame,
                "end_frame": action.end_frame,
                "zoom": action.zoom_level,
                "pan_offset": {"x": action.pan_offset[0], "y": action.pan_offset[1]}
            })
        
        resolved_cir = cir.copy()
        resolved_cir["_solver"] = "camera_solver"
        resolved_cir["_camera_timeline"] = camera_timeline
        
        return resolved_cir
    
    def validate(self, cir: Dict[str, Any]) -> bool:
        """Validate camera actions are valid."""
        return len(self.actions) > 0