# Nivix API Specification v1.0
## Cinematic Reasoning Infrastructure Interface

This document specifies the communication contract for the Nivix compiler. External tools interact with Nivix through these endpoints to generate explained animations.

### 1. POST /compile
Translates a symbolic pedagogical prompt into a stabilized, optimized execution plan (CIR).

**Input:**
- `prompt`: (string) The educational concept or lesson goal.
- `intent_override`: (optional) Direct hint (e.g., "compare", "prove").
- `backend`: (string, default "manim") The target renderer.
- `attention_priors`: (optional) Weightings for specific objects/scenes.

**Output:**
- `cir`: The Canonical Intermediate Representation (Execution Blueprint).
- `trace`: Frame-accurate object lifecycle history.
- `audit`: Intent satisfaction score and pedagogical gap analysis.
- `diagnostics`: Any compiler alerts (layout overlaps, etc.).

---

### 2. POST /preview
Slices a segment of the execution timeline for high-speed replay.

**Input:**
- `cir`: (json) The input execution blueprint.
- `start_time`: (float) The beginning of the window.
- `end_time`: (float) The end of the window.

**Output:**
- `sliced_cir`: A pre-filtered plan for the target window only.

---

### 3. POST /edit (Incremental)
Update an existing plan with minimal re-computation.

**Input:**
- `original_plan`: (json) The current fully-compiled execution plan.
- `change_set`: (list) Objects/nodes that have been modified (e.g., color, text).

**Output:**
- `patched_plan`: A re-optimized plan with updated CIR primitives.

---

### 4. GET /trace/explain
Provides reasoning for cinematic decisions made during compilation.

**Input:**
- `trace_id`: (string) Reference to a compiled trace.
- `object_id`: (string) Target entity.

**Output:**
- `reasoning`: (string) Explanation for specific highlight, morph, or position.
- `pedagogical_weight`: (float) Importance of this event in the narrative.
