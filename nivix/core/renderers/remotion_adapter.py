# Nivix Remotion Adapter v1.0
# Converts CIR to Remotion timeline JSON for React-native video rendering.

from typing import Dict, Any, Optional, List
from .adapter_interface import NivixAdapter, AdapterRegistry
import json

class RemotionAdapter(NivixAdapter):
    """
    Remotion adapter for Nivix v4.0
    
    Remotion is a timeline-based React-native renderer that maps well to CIR:
    - objects -> composition elements
    - timeline -> keyframes/timeline
    - transforms -> animation properties
    - camera -> z-index/transforms
    
    Docs: https://www.remotion.dev/docs
    """
    
    def __init__(self, cir: Dict[str, Any]):
        self.cir = cir
        self.fps = 30
    
    def supports(self, capability: str) -> bool:
        """Remotion capabilities."""
        supported = [
            "react_composition",
            "keyframes",
            "transforms",
            "svg_export",
            "mp4_output",
            "webm_output",
            "lambda_render",
            "serverless"
        ]
        return capability in supported
    
    def get_capabilities(self) -> List[str]:
        return [
            "react_composition",
            "keyframes",
            "transforms",
            "svg_export",
            "mp4_output",
            "webm_output",
            "lambda_render",
            "serverless"
        ]
    
    def validate_cir(self, cir: Dict[str, Any]) -> bool:
        """Validate CIR has required fields."""
        required = ["nodes", "transforms", "meta"]
        return all(k in cir for k in required)
    
    def to_renderer_format(self, cir: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert CIR to Remotion composition format.
        
        Remotion composition structure:
        {
            "composition": {
                "id": "NivixScene",
                "fps": 30,
                "duration": 100,
                "height": 1080,
                "width": 1920
            },
            "layers": [...],
            "keyframes": [...]
        }
        """
        nodes = cir.get("nodes", [])
        transforms = cir.get("transforms", [])
        attention = cir.get("attention", [])
        
        layers = []
        keyframes = []
        
        for node in nodes:
            layer = self._node_to_layer(node)
            layers.append(layer)
        
        for transform in transforms:
            kf = self._transform_to_keyframe(transform)
            keyframes.append(kf)
        
        duration_frames = 120
        for focus in attention:
            end_frame = focus.get("end_frame", 120)
            if end_frame > duration_frames:
                duration_frames = end_frame
        
        composition = {
            "id": "NivixScene",
            "fps": self.fps,
            "durationInFrames": duration_frames,
            "height": 1080,
            "width": 1920
        }
        
        return {
            "composition": composition,
            "layers": layers,
            "keyframes": keyframes
        }
    
    def _node_to_layer(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Convert CIR node to Remotion layer."""
        node_type = node.get("type", "object")
        node_id = node.get("id", "node")
        label = node.get("label", "")
        
        layer = {
            "id": node_id,
            "type": node_type,
            "name": label or node_id,
            "duration": 120,
            "props": {}
        }
        
        if node_type in ["shape", "object"]:
            label_lower = label.lower()
            if "circle" in label_lower:
                layer["props"] = {"shape": "circle", "fill": "#1f6feb"}
            elif "square" in label_lower:
                layer["props"] = {"shape": "rectangle", "fill": "#ff7b72"}
            elif "triangle" in label_lower:
                layer["props"] = {"shape": "polygon", "fill": "#a371f7"}
            else:
                layer["props"] = {"shape": "rectangle", "fill": "#238636"}
        
        lifecycle = node.get("lifecycle", {})
        if "spawn" in lifecycle:
            layer["inPoint"] = int(lifecycle["spawn"] * self.fps)
        
        return layer
    
    def _transform_to_keyframe(self, transform: Dict[str, Any]) -> Dict[str, Any]:
        """Convert CIR transform to Remotion keyframe."""
        action = transform.get("action", "")
        node_id = transform.get("node_id", "node")
        start_frame = transform.get("start_frame", 0)
        end_frame = transform.get("end_frame", 30)
        
        keyframe = {
            "layerId": node_id,
            "property": "transform",
            "startFrame": start_frame,
            "endFrame": end_frame
        }
        
        params = transform.get("params", {})
        
        if action == "move":
            keyframe["type"] = "position"
            keyframe["from"] = params.get("from", {"x": 0, "y": 0})
            keyframe["to"] = params.get("to", {"x": 100, "y": 0})
        elif action == "scale":
            keyframe["type"] = "scale"
            keyframe["from"] = params.get("from", 1.0)
            keyframe["to"] = params.get("to", 1.5)
        elif action == "fade_in":
            keyframe["type"] = "opacity"
            keyframe["from"] = 0
            keyframe["to"] = 1
        elif action == "fade_out":
            keyframe["type"] = "opacity"
            keyframe["from"] = 1
            keyframe["to"] = 0
        elif action == "rotate":
            keyframe["type"] = "rotation"
            keyframe["from"] = params.get("from", 0)
            keyframe["to"] = params.get("to", 360)
        else:
            keyframe["type"] = action
        
        return keyframe
    
    def export(self, cir: Dict[str, Any], output_path: str, options: Optional[Dict] = None) -> str:
        """
        Export CIR to MP4 via Remotion.
        
        In production, this would:
        1. Generate Remotion project files (package.json, src/index.tsx)
        2. Run `npx remotion render` CLI
        3. Or deploy to Remotion Lambda for cloud rendering
        """
        if not self.validate_cir(cir):
            raise ValueError("Invalid CIR: missing required fields")
        
        remotion_json = self.to_renderer_format(cir)
        
        print("--- [NIVIX REMOTION] Composition JSON generated ---")
        print(json.dumps(remotion_json, indent=2))
        
        print("--- [NIVIX REMOTION] To render, use:")
        print("    npx remotion render src/index.tsx NivixScene out/video.mp4")
        
        output_file = output_path or "output_remotion.mp4"
        
        print(f"--- [NIVIX REMOTION] Export configuration prepared ---")
        print(f"Output: {output_file}")
        
        return output_file

AdapterRegistry.register("remotion", RemotionAdapter)

if __name__ == "__main__":
    mock_cir = {
        "nodes": [
            {"id": "a", "type": "shape", "label": "Square", "lifecycle": {"spawn": 0}},
            {"id": "b", "type": "shape", "label": "Circle", "lifecycle": {"spawn": 30}}
        ],
        "transforms": [
            {"node_id": "a", "action": "move", "start_frame": 30, "end_frame": 90, 
             "params": {"from": {"x": 0, "y": 0}, "to": {"x": 200, "y": 0}}}
        ],
        "attention": [
            {"node_id": "a", "focus_score": 1.0, "start_frame": 0, "end_frame": 120}
        ],
        "meta": {"prompt": "test", "version": "4.0"}
    }
    
    adapter = RemotionAdapter(mock_cir)
    adapter.export(mock_cir, "output_remotion.mp4")