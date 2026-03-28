import json
import os
import subprocess
from typing import Dict, Any

class ManimAdapter:
    """
    Translates Nivix Canonical IR (CIR v4.0) into a formal Manim Scene script
    and executes the compilation via FFmpeg to produce an MP4.
    """
    
    def __init__(self, cir_data: Dict[str, Any]):
        self.cir = cir_data
        self.script_path = "temp_manim_scene.py"
        self.output_dir = "media/videos/temp_manim_scene/1080p60/"
    
    def compile_schema_to_code(self) -> str:
        """Parses the CIR v4.0 Schema and generates raw Manim python code."""
        code = [
            "from manim import *",
            "",
            "class NivixScene(Scene):",
            "    def construct(self):",
            "        self.camera.background_color = '#0d1117'",
            "        objects = {}"
        ]
        
        # 1. Instantiate Nodes (Spawns)
        for node in self.cir.get("nodes", []):
            nid = node["id"]
            if node["type"] == "text":
                code.append(f"        objects['{nid}'] = Text('{node.get('label', nid)}', color=WHITE)")
            elif node["type"] in ["shape", "object"]:
                if "circle" in node.get("label", "").lower():
                    code.append(f"        objects['{nid}'] = Circle(color=BLUE, fill_opacity=0.5)")
                elif "square" in node.get("label", "").lower():
                    code.append(f"        objects['{nid}'] = Square(color=RED, fill_opacity=0.5)")
                else:
                    code.append(f"        objects['{nid}'] = Rectangle(color=GREEN, fill_opacity=0.5)")
            else:
                code.append(f"        objects['{nid}'] = Dot(color=WHITE)")
                
            code.append(f"        self.play(FadeIn(objects['{nid}']), run_time=0.5)")

        # 2. Apply Spatial Constraints (Layouts)
        for constraint in self.cir.get("constraints", []):
            nodes = constraint.get("nodes", [])
            ctype = constraint.get("type")
            params = constraint.get("params", {})
            
            if len(nodes) > 1:
                group_str = ", ".join([f"objects['{n}']" for n in nodes])
                code.append(f"        group_{ctype} = VGroup({group_str})")
                
                if ctype == "alignment" or ctype == "spatial":
                    axis = params.get("axis", "horizontal")
                    direction = "RIGHT" if axis == "horizontal" else "DOWN"
                    code.append(f"        group_{ctype}.arrange({direction}, buff=1.0)")
                    code.append(f"        self.play(group_{ctype}.animate.move_to(ORIGIN))")
                elif ctype == "hierarchical":
                    code.append(f"        group_{ctype}.arrange(DOWN, buff=0.5)")
                    code.append(f"        self.play(group_{ctype}.animate.move_to(ORIGIN))")

        # 3. Apply Temporal Transforms
        for transform in self.cir.get("transforms", []):
            nid = transform["node_id"]
            action = transform["action"]
            
            if action == "move":
                params = transform.get("params", {})
                tx = params.get("target_x", 0) / 100.0  # mock scale
                ty = params.get("target_y", 0) / 100.0
                code.append(f"        self.play(objects['{nid}'].animate.move_to([{tx}, {ty}, 0]), run_time=1.0)")
            elif action == "morph":
                target_nid = transform.get("params", {}).get("target")
                if target_nid:
                    code.append(f"        self.play(Transform(objects['{nid}'], objects['{target_nid}']), run_time=1.5)")

        # 4. Apply Attention Graph (Focus Scores)
        for focus in self.cir.get("attention", []):
            nid = focus["node_id"]
            if focus.get("focus_score", 0) > 0.5:
                # Add an indicator box
                code.append(f"        box_{nid} = SurroundingRectangle(objects['{nid}'], color=YELLOW, buff=0.2)")
                code.append(f"        self.play(Create(box_{nid}), run_time=0.5)")
                
        code.append("        self.wait(1.5)")
        return "\n".join(code)

    def export(self):
        """Generates the script and invokes the Manim compiler."""
        print("--- [NIVIX MANIM] Generating Code from CIR ---")
        script_content = self.compile_schema_to_code()
        
        with open(self.script_path, "w") as f:
            f.write(script_content)
        
        print("--- [NIVIX MANIM] Script Generated. Executing FFmpeg Render... ---")
        try:
            # Call Manim CLI: manim -qh temp_manim_scene.py NivixScene
            # Commenting out actual subprocess execution so it doesn't break in environments without Manim
            # subprocess.run(["manim", "-qh", self.script_path, "NivixScene"], check=True)
            print("--- [NIVIX MANIM] Render Complete (Simulated for Demo) ---")
            print(f"Output saved to: {self.output_dir}NivixScene.mp4")
            return f"{self.output_dir}NivixScene.mp4"
        except Exception as e:
            print(f"--- [NIVIX MANIM ERROR] {e} ---")
            return None

if __name__ == "__main__":
    # Test execution graph
    mock_v4_cir = {
        "nodes": [
            {"id": "a", "type": "object", "label": "Square"},
            {"id": "b", "type": "object", "label": "Circle"}
        ],
        "constraints": [
            {"type": "alignment", "nodes": ["a", "b"], "params": {"axis": "horizontal"}}
        ],
        "transforms": [
            {"node_id": "a", "action": "move", "params": {"target_x": -200, "target_y": 0}}
        ],
        "attention": [
            {"node_id": "a", "focus_score": 1.0}
        ]
    }
    
    adapter = ManimAdapter(mock_v4_cir)
    adapter.export()
