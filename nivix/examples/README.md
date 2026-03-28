# Nivix: The Cinematic Reasoning Compiler

This directory contains executable proof-of-concept pipelines that demonstrate Nivix's transition from an animation engine to a verifiably symbolic reasoning platform.

The core value of Nivix is not "prompt to animation".  
It is **Symbolic Reasoning → Cinematic Compilation**.

## Proof-of-Concept Tour

In these examples, we prove that Nivix understands structure before it renders pixels. The pipeline ensures full **transparency, predictability, and pedagogical correctness**.

### 1. The Compilation Pipeline

Run `nivix explain <prompt.txt>` on any of these scenarios. You will see how Nivix plans the execution:

1. **Prompt:** The educational intent ("derive the area of a circle").
2. **CIR (Canonical IR) Output:** The structured plan. An abstract graph that defines what objects exist, how they depend on each other, and what layout constraints apply safely before any backend renderer is invoked.
3. **Trace Output:** The deterministic runtime log. You can inspect the execution timeline, verify semantic phase transitions, and audit the object lifecycle.
4. **Preview Slice:** Non-destructive timeline slicing (0-3s). Allows rapid iteration on camera timings without waiting for full artifact builds.
5. **Export:** Lowering the CIR graph to an executable Manim script, resulting in the final HD educational video.

### 2. Semantic Compliance & Traceability
Our architecture exposes internal states transparently:
- **Semantic Confidence Scores:** If the pedagogical planner isn't confident about a layout strategy (e.g. `horizontal_alignment` for a comparison), the compilation can fallback.
- **Attention Trajectories:** Rather than just drawing shapes, Nivix maps mathematical gaze logic (`mirrored_focus`, `sequential`). 

---

## Interactive Visualizations

We know text logs aren't enough to build trust with outsiders.
Run the self-explaining compiler with the `--visual` flag to launch an interactive visualization of the reasoning map:

```bash
python cli.py explain examples/compare_shapes.txt --visual
```
*This command generates `nivix_visualizer.html`, plotting the precise spatial mappings and CIR execution phases right in your browser.*

### Examples Available:
- `compare_shapes.txt` — Geometric alignment reasoning.
- `explain_fraction.txt` — Hierarchical component distribution (numerator/vinculum/denominator).
- `derive_area_circle.txt` — Morphology and unrolling geometry solver.
- `highlight_difference.txt` — Synced multi-axis layout and crossfading focus.
