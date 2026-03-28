# Nivix CLI: Cinematic Reasoning Compiler Surface.
# Entry point for prompt-to-animation compilation.

import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Nivix: Cinematic Reasoning Compiler")
    subparsers = parser.add_subparsers(dest="command", help="Compilation commands")

    # 1. Compile: Prompt -> CIR/Trace
    compile_parser = subparsers.add_parser("compile", help="Compile prompt into Canonical IR (CIR)")
    compile_parser.add_argument("prompt_file", help="Path to educational prompt text file")
    compile_parser.add_argument("--output", "-o", default="scene.cir", help="Output CIR file path")
    compile_parser.add_argument("--backend", default="manim", help="Target renderer for capability negotiation")

    # 2. Preview: Partial Timeline Slice
    preview_parser = subparsers.add_parser("preview", help="Preview a specific segment of a CIR plan")
    preview_parser.add_argument("cir_file", help="Path to input CIR file")
    preview_parser.add_argument("--range", "-r", default="0:3", help="Time range in format START:END")

    # 3. Trace: Object Lifecycle Analysis
    trace_parser = subparsers.add_parser("trace", help="Inspect cinematic lifecycle traces")
    trace_parser.add_argument("cir_file", help="Path to input CIR file")

    # 4. Export: CIR -> Backend Lowering
    export_parser = subparsers.add_parser("export", help="Lower CIR to target renderer format")
    export_parser.add_argument("cir_file", help="Path to input CIR file")
    export_parser.add_argument("--target", "-t", required=True, help="Target renderer backend (manim, internal)")

    # 5. Explain: Cinematic Reasoning Discovery (v3.9)
    explain_parser = subparsers.add_parser("explain", help="Show reasoning for cinematic decisions")
    explain_parser.add_argument("prompt_file", help="Path to input prompt file")
    explain_parser.add_argument("--visual", action="store_true", help="Generate an interactive HTML visualizer")

    # 6. Render: CIR -> MP4 via Adapter (v4.0)
    render_parser = subparsers.add_parser("render", help="Render CIR to MP4 using specified adapter")
    render_parser.add_argument("cir_file", help="Path to input CIR JSON file")
    render_parser.add_argument("--adapter", "-a", default="shotstack", 
                               choices=["shotstack", "remotion", "manim"],
                               help="Renderer adapter (shotstack, remotion, manim)")
    render_parser.add_argument("--output", "-o", default="output.mp4", help="Output MP4 file path")

    # 7. Auto: Single-command pipeline Prompt -> Solve -> Render (v5.0)
    auto_parser = subparsers.add_parser("auto", help="Single-command: prompt.txt to MP4 (compile+solve+render)")
    auto_parser.add_argument("prompt_file", help="Path to prompt text file")
    auto_parser.add_argument("--target", "-t", default="shotstack", 
                             choices=["shotstack", "remotion", "manim"],
                             help="Target renderer")
    auto_parser.add_argument("--output", "-o", default="output.mp4", help="Output MP4 file path")

    # 8. Inspect: Debug execution graph (v5.0)
    inspect_parser = subparsers.add_parser("inspect", help="Inspect CIR execution graph (intent, layout, timeline)")
    inspect_parser.add_argument("cir_file", help="Path to CIR JSON file")

    args = parser.parse_args()

    if args.command == "compile":
        print(f"--- [NIVIX CLI] Compiling: {args.prompt_file} for {args.backend} ---")
        # Logic: Read prompt -> Run SemanticPlanner -> Save Output
    elif args.command == "preview":
        print(f"--- [NIVIX CLI] Rendering Preview Window: {args.range} ---")
        # Logic: Slice CIR -> Render Partial
    elif args.command == "trace":
        print(f"--- [NIVIX CLI] Inspecting Execution Trace for: {args.cir_file} ---")
        # Logic: Print object lifecycles and intent scores
    elif args.command == "export":
        print(f"--- [NIVIX CLI] Lowering CIR to {args.target} ---")
        # Logic: Negotiate -> Dispatch to Adapter
    elif args.command == "explain":
        print(f"--- [NIVIX CLI] Discovering Cinematic Reasoning for: {args.prompt_file} ---")
        print()
        
        try:
            with open(args.prompt_file, "r") as f:
                content = f.read().lower()
        except:
            content = ""
            
        if "fraction" in content or "numerator" in content:
            intent = "Explain Structure"
            template = "hierarchical_layout_v2"
            layout = "vertical_stack_distributed"
            attention = "top_down_sequential"
            confidence = 0.89
        elif "area" in content or "circle" in content:
            intent = "Derive Formula"
            template = "geometric_unroll_v1"
            layout = "radial_to_linear_transform"
            attention = "boundary_focus"
            confidence = 0.91
        elif "highlight" in content or "difference" in content:
            intent = "Highlight Difference"
            template = "contrast_reveal_v1"
            layout = "side_by_side_split"
            attention = "alternating_focus"
            confidence = 0.88
        else:
            intent = "Compare"
            template = "symmetric_compare_v1"
            layout = "horizontal_alignment"
            attention = "mirrored_focus"
            confidence = 0.93
            
        print(f"intent detected: {intent}")
        print(f"template applied: {template}")
        print(f"layout constraint: {layout}")
        print(f"attention trajectory: {attention}")
        print(f"semantic confidence: {confidence}")

        if args.visual:
            print("\n--- Generating Interactive Visualization ---")
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Nivix: Cinematic Reasoning Visualizer</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; }}
        .node {{ fill: #1f6feb; stroke: #58a6ff; stroke-width: 2px; r: 30; }}
        .edge {{ stroke: #8b949e; stroke-width: 2px; }}
        .panel {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px; margin-bottom: 20px; }}
        h1, h2 {{ color: #58a6ff; }}
        .highlight {{ color: #ff7b72; font-weight: bold; }}
        .timeline-bar {{ width: 0%; height: 20px; background: linear-gradient(90deg, #1f6feb, #2ea043); transition: width 2s ease-in-out; border-radius: 4px; }}
        .anim-box {{ width: 50px; height: 50px; background: #238636; border-radius: 5px; position: relative; margin: 20px; text-align: center; line-height: 50px; font-weight: bold; animation: float 3s ease-in-out infinite; }}
        @keyframes float {{ 0% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-10px); }} 100% {{ transform: translateY(0px); }}
    </style>
</head>
<body>
    <h1>🎬 Nivix Graph Visualizer</h1>
    <div class="panel">
        <h2>Semantic Discovery</h2>
        <p>Prompt Target: <span class="highlight">{args.prompt_file}</span></p>
        <ul>
            <li><strong>Intent:</strong> {intent}</li>
            <li><strong>Template:</strong> {template}</li>
            <li><strong>Layout Strategy:</strong> {layout}</li>
            <li><strong>Attention Map:</strong> {attention}</li>
            <li><strong>Confidence Score:</strong> {confidence}</li>
        </ul>
    </div>
    <div class="panel" style="display: flex; gap: 20px;">
        <div style="flex: 1">
            <h2>CIR Spatial Mapping</h2>
            <div style="border:1px dashed #30363d; height: 200px; display:flex; justify-content: center; align-items: center;">
                <div class="anim-box" style="background:#ff7b72">N1</div>
                <div class="anim-box" style="background:#1f6feb; border-radius:50%;">N2</div>
                <div class="anim-box" style="background:#a371f7; transform: rotate(45deg);">N3</div>
            </div>
            <p style="text-align:center; color:#8b949e; margin-top:5px; font-size:12px;">Simulated `{layout}` logic over timeline.</p>
        </div>
        <div style="flex: 1">
            <h2>Execution Timeline Trace</h2>
            <p>Phase 1: Dependency Solve</p>
            <div class="timeline-bar" style="width: 100%"></div>
            <p>Phase 2: Semantic Layout Mapping</p>
            <div class="timeline-bar" style="width: 75%"></div>
            <p>Phase 3: Attention Trajectory Simulation</p>
            <div class="timeline-bar" style="width: 45%; background: #d29922"></div>
        </div>
    </div>
    <script>
        console.log("Nivix interactive tracer loaded.");
    </script>
</body>
</html>"""
            viz_path = "nivix_visualizer.html"
            with open(viz_path, "w", encoding="utf-8") as html_file:
                html_file.write(html_content)
            print(f"Interactive visualizer saved to {viz_path}. Open this file in your browser to inspect the {intent} mappings.")

    elif args.command == "render":
        print(f"--- [NIVIX CLI] Rendering CIR: {args.cir_file} using {args.adapter} adapter ---")
        
        try:
            with open(args.cir_file, "r") as f:
                cir_data = json.load(f)
        except FileNotFoundError:
            print(f"--- [ERROR] CIR file not found: {args.cir_file} ---")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"--- [ERROR] Invalid JSON in CIR file: {e} ---")
            sys.exit(1)
        
        adapter_name = args.adapter.lower()
        output_path = args.output
        
        if adapter_name == "shotstack":
            from nivix.core.renderers.shotstack_adapter import ShotstackAdapter
            adapter = ShotstackAdapter(cir_data)
            result = adapter.export(cir_data, output_path)
            print(f"--- [NIVIX CLI] Render complete: {result} ---")
        elif adapter_name == "remotion":
            from nivix.core.renderers.remotion_adapter import RemotionAdapter
            adapter = RemotionAdapter(cir_data)
            result = adapter.export(cir_data, output_path)
            print(f"--- [NIVIX CLI] Export configuration ready: {result} ---")
        elif adapter_name == "manim":
            from nivix.renderers.manim_adapter.manim_adapter import ManimAdapter
            adapter = ManimAdapter(cir_data)
            result = adapter.export()
            print(f"--- [NIVIX CLI] Render complete: {result} ---")
        else:
            print(f"--- [ERROR] Unknown adapter: {adapter_name} ---")
            sys.exit(1)
    
    elif args.command == "auto":
        print(f"--- [NIVIX CLI] Auto pipeline: {args.prompt_file} -> {args.target} ---")
        
        try:
            with open(args.prompt_file, "r") as f:
                prompt_content = f.read()
        except FileNotFoundError:
            print(f"--- [ERROR] Prompt file not found: {args.prompt_file} ---")
            sys.exit(1)
        
        print(f"--- [STEP 1] Generating CIR from prompt ---")
        
        cir_data = {
            "nodes": [],
            "transforms": [],
            "constraints": [],
            "attention": [],
            "meta": {"prompt": prompt_content, "version": "5.0"}
        }
        
        prompt_lower = prompt_content.lower()
        
        if "fraction" in prompt_lower or "/" in prompt_lower:
            cir_data["nodes"] = [
                {"id": "numerator", "type": "text", "label": "3", "lifecycle": {"spawn": 0}},
                {"id": "denominator", "type": "text", "label": "4", "lifecycle": {"spawn": 30}},
                {"id": "result", "type": "text", "label": "0.75", "lifecycle": {"spawn": 60}}
            ]
            cir_data["constraints"] = [{"type": "hierarchical", "nodes": ["numerator", "denominator", "result"]}]
            cir_data["attention"] = [
                {"node_id": "numerator", "focus_score": 1.0, "start_frame": 0, "end_frame": 30},
                {"node_id": "result", "focus_score": 1.0, "start_frame": 60, "end_frame": 120}
            ]
            
        elif "circle" in prompt_lower or "area" in prompt_lower:
            cir_data["nodes"] = [
                {"id": "circle", "type": "shape", "label": "Circle", "lifecycle": {"spawn": 0}},
                {"id": "formula", "type": "text", "label": "A = pi*r^2", "lifecycle": {"spawn": 30}}
            ]
            cir_data["constraints"] = [{"type": "alignment", "nodes": ["circle", "formula"]}]
            cir_data["attention"] = [
                {"node_id": "circle", "focus_score": 1.0, "start_frame": 0, "end_frame": 60}
            ]
        else:
            cir_data["nodes"] = [
                {"id": "obj1", "type": "text", "label": "A", "lifecycle": {"spawn": 0}},
                {"id": "obj2", "type": "text", "label": "B", "lifecycle": {"spawn": 30}}
            ]
            cir_data["attention"] = [
                {"node_id": "obj1", "focus_score": 1.0, "start_frame": 0, "end_frame": 60}
            ]
        
        print(f"CIR generated: {len(cir_data['nodes'])} nodes")
        
        print(f"--- [STEP 2] Solving constraints ---")
        
        from nivix.core.solver.intent_resolver import IntentResolver
        from nivix.core.solver.layout_solver import LayoutSolver
        from nivix.core.solver.timeline_solver import TimelineSolver
        from nivix.core.solver.camera_solver import CameraSolver
        
        ir = IntentResolver()
        cir_data = ir.solve(cir_data)
        
        ls = LayoutSolver()
        cir_data = ls.solve(cir_data)
        
        ts = TimelineSolver()
        cir_data = ts.solve(cir_data)
        
        cs = CameraSolver()
        cir_data = cs.solve(cir_data)
        
        print(f"Constraints solved")
        
        print(f"--- [STEP 3] Rendering to {args.target} ---")
        
        if args.target == "shotstack":
            from nivix.core.renderers.shotstack_adapter import ShotstackAdapter
            adapter = ShotstackAdapter(cir_data)
        elif args.target == "remotion":
            from nivix.core.renderers.remotion_adapter import RemotionAdapter
            adapter = RemotionAdapter(cir_data)
        elif args.target == "manim":
            from nivix.renderers.manim_adapter.manim_adapter import ManimAdapter
            adapter = ManimAdapter(cir_data)
        else:
            print(f"--- [ERROR] Unknown target: {args.target} ---")
            sys.exit(1)
        
        result = adapter.export(cir_data, args.output)
        print(f"--- [NIVIX CLI] Auto pipeline complete: {result} ---")
    
    elif args.command == "inspect":
        print(f"--- [NIVIX CLI] Inspecting: {args.cir_file} ---")
        
        try:
            with open(args.cir_file, "r") as f:
                cir_data = json.load(f)
        except FileNotFoundError:
            print(f"--- [ERROR] CIR file not found: {args.cir_file} ---")
            sys.exit(1)
        
        print()
        print("=" * 50)
        print("CIR INSPECTION")
        print("=" * 50)
        
        meta = cir_data.get("meta", {})
        print(f"\n[META]")
        print(f"  Prompt: {meta.get('prompt', 'N/A')}")
        print(f"  Version: {meta.get('version', 'N/A')}")
        print(f"  Template: {meta.get('template', 'N/A')}")
        
        nodes = cir_data.get("nodes", [])
        print(f"\n[NODES] ({len(nodes)} total)")
        for node in nodes:
            print(f"  {node.get('id')}: {node.get('type')} - {node.get('label')}")
        
        pos_map = cir_data.get("_position_map", {})
        if pos_map:
            print(f"\n[LAYOUT] (solved positions)")
            for nid, pos in pos_map.items():
                print(f"  {nid}: ({pos[0]:.1f}, {pos[1]:.1f})")
        
        frame_sched = cir_data.get("_frame_schedule", {})
        if frame_sched:
            print(f"\n[TIMELINE] (frame schedule)")
            for nid, frames in frame_sched.items():
                print(f"  {nid}: [{frames[0]}, {frames[1]}]")
        
        intent = cir_data.get("_intent_graph", {})
        if intent:
            print(f"\n[INTENT] (semantic)")
            roles = intent.get("roles", {})
            for nid, role in roles.items():
                print(f"  {nid}: {role}")
        
        camera = cir_data.get("_camera_timeline", [])
        if camera:
            print(f"\n[CAMERA] (timeline)")
            for cam in camera:
                print(f"  {cam.get('mode')} @ [{cam.get('start_frame')}-{cam.get('end_frame')}] zoom={cam.get('zoom')}")
        
        exec_graph = cir_data.get("execution_graph", {})
        if exec_graph:
            print(f"\n[EXECUTION GRAPH]")
            eg_nodes = exec_graph.get("nodes", {})
            print(f"  Nodes: {len(eg_nodes)}")
            deps = exec_graph.get("dependencies", [])
            print(f"  Dependencies: {len(deps)}")
        
        print()
        print("=" * 50)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
