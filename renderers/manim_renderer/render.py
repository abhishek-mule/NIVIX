# Nivix Manim Renderer Adapter v1.8
# Narrative Orchestration with Semantic Layout Logic & Cinematic Transitions.

try:
    from manim import *
except ImportError:
    # Safe-guard for environments where manim is not yet installed
    print("Warning: Manim library not found. Rendering will be simulated.")
    Scene = object
    Circle = Square = Triangle = Text = MathTex = TransformMatchingTex = VGroup = Write = FadeIn = FadeOut = lambda *args, **kwargs: object()
    RIGHT = LEFT = UP = DOWN = ORIGIN = [0, 0, 0]

class NivixScene(Scene):
    """
    Main Manim Scene that converts Multi-Phase Execution IR into visual animation.
    Now respects Spatial Layout Coordinates from the Layout Engine (v1.11).
    """
    def __init__(self, execution_ir, **kwargs):
        self.execution_ir = execution_ir
        super().__init__(**kwargs)

    def construct(self):
        # 1. Multi-Phase Extraction
        scenes = self.execution_ir.get("scenes", [])
        
        print(f"--- Manim Rendering v1.8: Semantic Layout active ---")
        
        m_registry = {} # actor_id -> Active Manim Mobject instance
        
        for scene_idx, scene_data in enumerate(scenes):
            print(f"--- [SHOT {scene_idx}] Starting Rendering Sub-Timeline... ---")
            
            # --- 1. HANDLE TRANSITIONS ---
            transitions_in = scene_data.get("transitions_in", [])
            for trans in transitions_in:
                 if trans.get("style") == "fade":
                      if self.mobjects: self.play(*[FadeOut(m) for m in self.mobjects], run_time=trans.get("duration", 1.0))
                 elif trans.get("style") == "cut": self.remove(*self.mobjects)
                 self.wait(0.5)
            
            temporal_groups = {} # start_time -> [list of anims]
            def add_anim(t, anim, dur):
                if t not in temporal_groups: temporal_groups[t] = []
                temporal_groups[t].append((anim, dur))
            
            # --- 2. Per-Shot Actor Initialization ---
            def prepare_actor(node, type_prefix):
                m_id = node.get("id", f"{type_prefix}_{len(m_registry)}")
                if type_prefix == "geometry": mobj = Square(color=WHITE) 
                elif type_prefix == "text": mobj = Text(node.get("content", ""))
                elif type_prefix == "math": mobj = MathTex(node.get("content", ""))
                
                mobj.scale(node.get("scale", 1.0))
                
                # --- APPLY LAYOUT COORDINATES (v1.11 Integration) ---
                if "position" in node:
                     print(f"--- [LAYOUT] Placing {m_id} at {node['position']} ---")
                     mobj.move_to(node["position"])
                
                m_registry[m_id] = mobj
                
                # Entrance Animation
                mot = node.get("motion", "none")
                if mot == "none":
                    anim = Write(mobj) if type_prefix in ["math", "text"] else FadeIn(mobj)
                    add_anim(node.get("start_time", 0.0), anim, node.get("duration", 1.0))
                else:
                    anim = mobj.animate.shift(UP * 3) # simplified shift
                    add_anim(node.get("start_time", 0.0), anim, node.get("duration", 1.0))

            for alist, prefix in [(scene_data.get("objects", []), "geometry"), 
                                  (scene_data.get("text_objects", []), "text"), 
                                  (scene_data.get("math_objects", []), "math")]:
                for node in alist: prepare_actor(node, prefix)
                    
            # Iterative Group Resolution
            unresolved = list(scene_data.get("group_objects", []))
            max_d = 5
            while unresolved and max_d > 0:
                 max_d -= 1; next_unresolved = []
                 for g_node in unresolved:
                      g_id = g_node.get("id", f"group_{len(m_registry)}")
                      members = [m_registry[m] for m in g_node.get("members", []) if m in m_registry]
                      if len(members) == len(g_node.get("members", [])):
                           m_registry[g_id] = VGroup(*members)
                           # Group level layout (v1.11 concept)
                           if "position" in g_node: m_registry[g_id].move_to(g_node["position"])
                           if g_node.get("motion") != "none":
                                add_anim(g_node.get("start_time", 0.0), m_registry[g_id].animate.shift(RIGHT * 3), g_node.get("duration", 1.0))
                      else: next_unresolved.append(g_node)
                 unresolved = next_unresolved

            # Final Render (Orchestrated by Scheduler/Optimizer outputs)
            sorted_times = sorted(temporal_groups.keys()); last_at_time = 0.0
            for t in sorted_times:
                gap = t - last_at_time; if gap > 0: self.wait(gap)
                anims = [item[0] for item in temporal_groups[t]]
                if anims: self.play(*anims, run_time=max([i[1] for i in temporal_groups[t]]))
                last_at_time = t + max([i[1] for i in temporal_groups[t]])
            
def render_scene(execution_ir):
    """Entry point for the Nivix -> Manim bridge."""
    print("Nivix Renderer: Semantic Layout v1.8 successfully scheduled.")
    scene = NivixScene(execution_ir)
    return scene
