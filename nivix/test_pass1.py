"""Quick Pass 1 validation - shows full output clearly."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nivix.core.planner.llm_pass1 import run_pass1_nodes

test_prompts = [
    "explain why imaginary numbers exist",
    "show how RSA encryption works",
    "demonstrate the concept of a derivative",
    "show Fourier transform intuitively",
    "explain the pythagorean theorem",
]

results = []
for p in test_prompts:
    r = run_pass1_nodes(p)
    results.append({
        "prompt": p,
        "source": r.get("source"),
        "node_count": len(r["nodes"]),
        "nodes": [(n["type"], n["id"], n["label"]) for n in r["nodes"]],
        "reasoning": r.get("reasoning", "")
    })

# Print as clean table
print("\n" + "="*70)
print("NIVIX PASS 1 — SEMANTIC NODE GAUNTLET RESULTS")
print("="*70)
for res in results:
    print(f"\nPROMPT : {res['prompt']}")
    print(f"SOURCE : {res['source']}  |  NODES: {res['node_count']}")
    for t, id_, label in res["nodes"]:
        print(f"  [{t:10}] {id_:30} → \"{label}\"")
    print(f"REASON : {res['reasoning']}")
    print("-"*70)
