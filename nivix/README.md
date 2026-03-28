# Nivix: The LLVM of Cinematic Reasoning 🎬

**Deterministic, auditable, and renderer-agnostic AI animation.**

*See every semantic decision. Inspect every timeline. Trust every frame.*

---

Nivix is not a "prompt-to-video" tool. It is a foundational infrastructure compiler that translates natural language educational intent into a **verifiably correct execution graph** before any rendering takes place. 

If you are an academic proving reasoning models, or an engineer building the next generational educational platform, Nivix is the deterministic backend you build on top of.

## 🚀 Quick Demo Tour

Don't read the theory. **See the compiler reason in real time.**

### Step 1: Discover Semantic Reasoning (CLI)
You can ask the compiler how it plans to execute a prompt without rendering heavy video files:
```bash
python cli.py explain examples/explain_fraction.txt --visual
```
*Outcome: Generates an interactive HTML trace in your browser showing the parsed Constraints, Attention Maps, and Semantic Confidence scores.*

### Step 2: The Live API & Web-Native Player
Start the schema-aware reasoning engine:
```bash
python api_server.py
# (Runs on http://localhost:8000/api/compile)
```
Then, double click `player/index.html` in your browser.
Click **Fetch Live API**, type `"derive the area of a circle"`, and watch the Canonical Intermediate Representation (CIR) construct itself and animate sequentially *via pure Canvas*—zero video dependencies.

---

## 🏗️ Architecture Overview

The platform guarantees correctness by separating reasoning from rendering across **three pillars**:

1. **The Spec (`schema/cir_schema.json`)**
   The formal architectural moat. A strict JSON schema defining `nodes`, `transforms`, `constraints`, and `attention`. Every output is validated against this exact contract.
2. **The Engine (`api_server.py`)**
   The compiler core. Computes the multi-graph semantic dependencies and issues a strict HTTP 400 if the reasoning model hallucinates an invalid instruction constraint. 
3. **The Player (`player/index.html` or Adapters)**
   The deterministic consumer. Frontends merely scrub across the pre-calculated timeline.

### CIR Lifecycle Map
```mermaid
graph LR
A[Prompt] --> B(Semantic Planner)
B --> C{Schema Validator}
C -- Fail --> D[Reject / Repair]
C -- Pass --> E[Canonical IR (v4.0)]
E --> F[Web-Native Player]
E --> G[Manim/Remotion Adapters]
```
*(For a deeper dive into constraint solving, read `nivix_architecture.md`)*

---

## 🎨 Example Gallery

### `explain_fraction.txt`
* **Prompt:** "Explain numerator and denominator"
* **CIR Outcome:** Generates a `hierarchical_layout_v2` constraint ensuring elements stack vertically regardless of screen size. 
* **Attention Constraint:** Forces `top_down_sequential` focus mapping, preventing viewers from looking at the denominator before the vinculum is drawn.

### `compare_shapes.txt`
* **Prompt:** "Compare triangle and square"
* **CIR Outcome:** Calculates `horizontal_alignment` bounding boxes. Evaluates semantic confidence at `0.93`.

*(Full traces available in the `examples/` directory).*

---

## 💻 Developer & Integration Guide

If you are building your own educational platform, you consume Nivix like this:

### 1. Compile Request
```bash
curl -X POST http://localhost:8000/api/compile \
-H "Content-Type: application/json" \
-d '{"prompt": "highlight the difference between linear and exponential growth"}'
```

### 2. Guaranteed Payload
The API provides a fully audited `cir` object and execution `trace`:
```json
{
  "status": "success",
  "cir": {
    "nodes": [ ... ],
    "transforms": [ ... ],
    "constraints": [ ... ],
    "attention": [ ... ],
    "meta": {
      "version": "4.0",
      "semantic_confidence": 0.88,
      "template": "contrast_reveal_v1"
    }
  }
}
```

### 3. Build Your Adapter
Pass the guaranteed `cir` block into your React app, your Unity engine, or your Manim script. Because the schema validates the spatial layouts and chronological timelines, **your renderer only needs to focus on making it look beautiful.**

---

*Inspect the infrastructure, integrate the API, or build your own renderer—every CIR is fully deterministic and auditable.*
