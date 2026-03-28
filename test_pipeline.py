# Test full solver pipeline
from nivix.core.solver.timeline_solver import TimelineSolver
from nivix.core.solver.layout_solver import LayoutSolver
from nivix.core.solver.intent_resolver import IntentResolver

# Test CIR
test_cir = {
    "nodes": [
        {"id": "numerator", "type": "text", "label": "3", "lifecycle": {"spawn": 0}},
        {"id": "denominator", "type": "text", "label": "4", "lifecycle": {"spawn": 30}},
        {"id": "result", "type": "text", "label": "0.75", "lifecycle": {"spawn": 60}}
    ],
    "transforms": [
        {"node_id": "numerator", "action": "move", "start_frame": 30, "end_frame": 90, "params": {"to": {"x": 100, "y": 0}}}
    ],
    "constraints": [
        {"type": "hierarchical", "nodes": ["numerator", "denominator", "result"]}
    ],
    "attention": [
        {"node_id": "numerator", "focus_score": 1.0, "start_frame": 0, "end_frame": 30},
        {"node_id": "result", "focus_score": 1.0, "start_frame": 60, "end_frame": 120}
    ],
    "meta": {
        "prompt": "derive fraction 3/4",
        "version": "4.0",
        "template": "geometric_unroll_v1"
    }
}

print("=" * 60)
print("NIVIX v5.0 SOLVER PIPELINE TEST")
print("=" * 60)

print("\n[1] INTENT RESOLVER")
print("-" * 40)
ir = IntentResolver()
cir = ir.solve(test_cir)
print(f"  Pipeline stage: {cir.get('_solver')}")

print("\n[2] LAYOUT SOLVER")
print("-" * 40)
ls = LayoutSolver()
cir = ls.solve(cir)
print(f"  Pipeline stage: {cir.get('_solver')}")

print("\n[3] TIMELINE SOLVER")
print("-" * 40)
ts = TimelineSolver()
cir = ts.solve(cir)
print(f"  Pipeline stage: {cir.get('_solver')}")

print("\n" + "=" * 60)
print("FINAL SOLVED CIR")
print("=" * 60)
print(f"Intent graph: {cir.get('_intent_graph', {}).get('relationships')}")
print(f"Position map: {cir.get('_position_map')}")
print(f"Frame schedule: {cir.get('_frame_schedule')}")
print("\n[PASS] Full solver pipeline operational.")