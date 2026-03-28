# Nivix Shotstack Adapter v1.0
# Converts CIR to Shotstack timeline JSON for cloud video rendering.

from typing import Dict, Any, Optional, List
from .adapter_interface import NivixAdapter, AdapterRegistry
import json
import time

class ShotstackAdapter(NivixAdapter):
    """
    Shotstack adapter for Nivix v4.0
    
    Shotstack is a timeline-driven JSON video engine that maps well to CIR:
    - tracks -> scene layers
    - clips -> objects/animations
    - transitions -> CIR transitions
    - assets -> nodes/shapes
    
    API: https://shotstack.io/docs/api/
    """
    
    def __init__(self, cir: Dict[str, Any]):
        self.cir = cir
        self.api_key: Optional[str] = None
        self.endpoint: str = "https://api.shotstack.io/v4"
    
    def supports(self, capability: str) -> bool:
        """Shotstack capabilities."""
        supported = [
            "text_overlays",
            "shape_animations",
            "transitions",
            "timeline",
            "cloud_render",
            "mp4_output",
            "webm_output",
            "image_assets",
            "audio_tracks"
        ]
        return capability in supported
    
    def get_capabilities(self) -> List[str]:
        return [
            "text_overlays",
            "shape_animations", 
            "transitions",
            "timeline",
            "cloud_render",
            "mp4_output",
            "webm_output",
            "image_assets",
            "audio_tracks"
        ]
    
    def validate_cir(self, cir: Dict[str, Any]) -> bool:
        """Validate CIR has required fields."""
        required = ["nodes", "transforms", "meta"]
        return all(k in cir for k in required)
    
    def to_renderer_format(self, cir: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert CIR to Shotstack timeline format.
        
        Shotstack timeline structure:
        {
            "timeline": {
                "tracks": [...],
                "background": "#000000"
            },
            "output": {
                "format": "mp4",
                "resolution": "1080"
            }
        }
        """
        timeline = {
            "tracks": [],
            "background": "#0d1117"
        }
        
        tracks = []
        
        objects = cir.get("nodes", [])
        transforms = cir.get("transforms", [])
        constraints = cir.get("constraints", [])
        attention = cir.get("attention", [])
        
        if objects:
            track = {"clips": []}
            
            for i, node in enumerate(objects):
                clip = self._node_to_clip(node, i)
                track["clips"].append(clip)
            
            tracks.append(track)
        
        if transforms:
            anim_track = {"clips": []}
            for transform in transforms:
                clip = self._transform_to_clip(transform)
                if clip:
                    anim_track["clips"].append(clip)
            tracks.append(anim_track)
        
        if attention:
            camera_track = {"clips": []}
            for focus in attention:
                clip = self._attention_to_clip(focus)
                if clip:
                    camera_track["clips"].append(clip)
            tracks.append(camera_track)
        
        timeline["tracks"] = tracks
        
        output = {
            "format": "mp4",
            "resolution": "1080",
            "fps": 30
        }
        
        return {
            "timeline": timeline,
            "output": output
        }
    
    def _node_to_clip(self, node: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Convert CIR node to Shotstack clip."""
        node_type = node.get("type", "object")
        node_id = node.get("id", f"node_{index}")
        label = node.get("label", "")
        
        clip = {
            "asset": {
                "type": "text",
                "text": label or node_id,
                "style": {
                    "font": "Roboto",
                    "size": 48,
                    "color": "#ffffff"
                }
            },
            "start": 0.0,
            "duration": 5.0,
            "transition": {
                "in": "fade",
                "out": "fade"
            }
        }
        
        if node_type in ["shape", "object"]:
            clip["asset"] = {
                "type": "shape",
                "shape": "rectangle",
                "width": 200,
                "height": 200,
                "color": self._get_node_color(node)
            }
        
        if node_type == "text":
            clip["asset"]["text"] = label or "Text"
        
        lifecycle = node.get("lifecycle", {})
        if "spawn" in lifecycle:
            clip["start"] = float(lifecycle["spawn"])
        
        return clip
    
    def _transform_to_clip(self, transform: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert CIR transform to Shotstack clip."""
        action = transform.get("action", "")
        node_id = transform.get("node_id", "")
        
        clip = {
            "asset": {
                "type": "text",
                "text": f"Transform: {action}",
                "style": {"font": "Roboto", "size": 36, "color": "#58a6ff"}
            },
            "start": float(transform.get("start_frame", 0)) / 30.0,
            "duration": float(transform.get("end_frame", 30)) / 30.0
        }
        
        return clip
    
    def _attention_to_clip(self, focus: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert CIR attention to Shotstack camera clip."""
        start = float(focus.get("start_frame", 0)) / 30.0
        end = float(focus.get("end_frame", 60)) / 30.0
        
        camera_params = focus.get("camera_params", {})
        
        clip = {
            "asset": {
                "type": "text",
                "text": "Camera Focus",
                "style": {"font": "Roboto", "size": 24, "color": "#d29922"}
            },
            "start": start,
            "duration": end - start
        }
        
        if camera_params.get("zoom"):
            clip["scale"] = camera_params["zoom"]
        
        return clip
    
    def _get_node_color(self, node: Dict[str, Any]) -> str:
        """Map node label/type to color."""
        label = node.get("label", "").lower()
        if "circle" in label:
            return "#1f6feb"
        elif "square" in label:
            return "#ff7b72"
        elif "triangle" in label:
            return "#a371f7"
        return "#238636"
    
    def export(self, cir: Dict[str, Any], output_path: str, options: Optional[Dict] = None) -> str:
        """
        Export CIR to MP4 via Shotstack cloud rendering.
        
        In production, this would:
        1. Send timeline JSON to Shotstack API
        2. Poll for render completion
        3. Download the rendered MP4
        """
        if not self.validate_cir(cir):
            raise ValueError("Invalid CIR: missing required fields")
        
        timeline_json = self.to_renderer_format(cir)
        
        print("--- [NIVIX SHOTSTACK] Timeline JSON generated ---")
        print(json.dumps(timeline_json, indent=2))
        
        render_id = f"nivix_render_{int(time.time())}"
        
        print(f"--- [NIVIX SHOTSTACK] Render job submitted: {render_id} ---")
        print(f"--- [NIVIX SHOTSTACK] Status: Processing (simulated) ---")
        
        output_file = output_path or f"output_{render_id}.mp4"
        
        print(f"--- [NIVIX SHOTSTACK] Render complete ---")
        print(f"Output: {output_file}")
        
        return output_file

AdapterRegistry.register("shotstack", ShotstackAdapter)

if __name__ == "__main__":
    mock_cir = {
        "nodes": [
            {"id": "a", "type": "shape", "label": "Square", "lifecycle": {"spawn": 0}},
            {"id": "b", "type": "shape", "label": "Circle", "lifecycle": {"spawn": 1}}
        ],
        "transforms": [
            {"node_id": "a", "action": "move", "start_frame": 30, "end_frame": 90}
        ],
        "constraints": [
            {"type": "alignment", "nodes": ["a", "b"]}
        ],
        "attention": [
            {"node_id": "a", "focus_score": 1.0, "start_frame": 0, "end_frame": 120,
             "camera_params": {"zoom": 1.5}}
        ],
        "meta": {"prompt": "test", "version": "4.0"}
    }
    
    adapter = ShotstackAdapter(mock_cir)
    adapter.export(mock_cir, "test_output.mp4")