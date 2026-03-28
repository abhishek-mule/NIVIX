# Test solver layer
from nivix.core.solver import SolverRegistry, create_solver, SolverMode
from nivix.core.solver.timeline_solver import TimelineSolver
from nivix.core.solver.layout_solver import LayoutSolver
from nivix.core.solver.intent_resolver import IntentResolver

# Explicit registration
SolverRegistry.register("timeline", TimelineSolver)
SolverRegistry.register("layout", LayoutSolver)
SolverRegistry.register("intent", IntentResolver)

print("--- [TEST] Solver Registry ---")
for s in SolverRegistry.list_solvers():
    print(f"  {s}")
print()

# Create test CIR
test_cir = {
    "nodes": [
        {"id": "a", "type": "shape", "label": "Square"},
        {"id": "b", "type": "shape", "label": "Circle"}
    ],
    "transforms": [
        {"node_id": "a", "action": "move", "start_frame": 0, "end_frame": 30},
        {"node_id": "b", "action": "fade_in", "start_frame": 30, "end_frame": 60}
    ],
    "constraints": [
        {"type": "alignment", "nodes": ["a", "b"]}
    ],
    "attention": [
        {"node_id": "a", "focus_score": 1.0, "start_frame": 0, "end_frame": 60}
    ],
    "meta": {
        "prompt": "compare square and circle",
        "version": "4.0"
    }
}

print("--- [TEST] Timeline Solver ---")
ts = create_solver("timeline")
if ts:
    result = ts.solve(test_cir)
    print(f"Solver: {result.get('_solver')}")
    print(f"Schedule: {result.get('_frame_schedule')}")
print()

print("--- [TEST] Layout Solver ---")
ls = create_solver("layout")
if ls:
    result = ls.solve(test_cir)
    print(f"Solver: {result.get('_solver')}")
    print(f"Positions: {result.get('_position_map')}")
print()

print("--- [TEST] Intent Resolver ---")
ir = create_solver("intent")
if ir:
    result = ir.solve(test_cir)
    print(f"Solver: {result.get('_solver')}")
    intents = result.get("_intent_graph", {})
    print(f"Relationships: {intents.get('relationships')}")
    print(f"Roles: {intents.get('roles')}")
print()

print("--- [SUCCESS] Solver layer operational ---")