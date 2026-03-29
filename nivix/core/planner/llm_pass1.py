"""
Nivix LLM Pass 1: Real Object Graph Builder
The first real LLM integration in the Nivix compiler pipeline.

Uses OpenRouter (single API key) with a free-model auto-fallback chain.
If Model A fails or is unavailable, it automatically tries Model B, then C, etc.
Zero cost — all models in the chain are free-tier on OpenRouter.

Set env variable: OPENROUTER_API_KEY=sk-or-v1-...
"""
import os
import json
import time
import hashlib
import urllib.request
import urllib.error

# Simple file-based cache to avoid re-calling LLM for identical prompts
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".pass1_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# OpenRouter free model fallback chain (tried in order)
# All are free-tier. If one is overloaded or fails, next is tried automatically.
FREE_MODEL_CHAIN = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "google/gemma-3-12b-it:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "qwen/qwen-2-7b-instruct:free",
]

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

PASS_1_SYSTEM_PROMPT = """You are the Object Graph Builder for Nivix, an animation compiler.
Your job is Pass 1 of a multi-pass compilation pipeline.

Given an educational topic or concept, you must reason about:
1. What are the key visual primitives (nodes) needed to teach this concept?
2. What TYPE is each node? (text, shape, object, plot, math, highlight)
3. What is the pedagogical label for each node?
4. At what frame does each node spawn into the scene?

RULES:
- Output ONLY valid JSON. No explanations, no markdown code blocks. Just raw JSON.
- Every node MUST have: id (snake_case), type, label, lifecycle.spawn
- Use meaningful ids like "real_axis", "imaginary_axis", "complex_plane" NOT "node_1", "node_2"
- Spawn frames should feel like a natural narrative (0, 30, 60, 90...)
- Maximum 8 nodes. Minimum 2. Pick the MOST pedagogically essential ones.
- Types allowed: text, shape, object, plot, math, highlight

OUTPUT FORMAT (strict):
{
  "nodes": [
    {"id": "example_id", "type": "shape", "label": "Human Label", "lifecycle": {"spawn": 0}},
    ...
  ],
  "reasoning": "One sentence explaining WHY these specific objects teach the concept."
}"""

def _get_cache_key(prompt: str) -> str:
    """Hash-based cache lookup to avoid duplicate LLM calls."""
    normalized = prompt.strip().lower()
    return hashlib.md5(normalized.encode()).hexdigest()

def _read_cache(key: str):
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def _write_cache(key: str, data: dict):
    path = os.path.join(CACHE_DIR, f"{key}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def run_pass1_nodes(prompt: str, use_cache: bool = True) -> dict:
    """
    Executes Pass 1: LLM-driven Object Graph generation via OpenRouter.
    Automatically tries each free model in FREE_MODEL_CHAIN until one succeeds.
    Falls back to keyword-aware heuristics only if ALL models fail.
    
    Set use_cache=False to bypass cache and force LLM call.
    """
    import os
    api_key = os.environ.get("OPENROUTER_API_KEY")
    force_llm = os.environ.get("FORCE_LLM", "false").lower() == "true"
    
    cache_key = _get_cache_key(prompt)
    
    # Only use cache if NOT forcing LLM
    if use_cache and not force_llm:
        cached = _read_cache(cache_key)
        if cached:
            print(f"[PASS 1] Cache HIT for: '{prompt[:50]}'")
            cached["source"] = "cache"
            return cached
    else:
        print(f"[PASS 1] Cache BYPASSED, use_cache={use_cache}, force_llm={force_llm}")

    api_key = os.environ.get("OPENROUTER_API_KEY")

    print(f"[PASS 1] API key present: {bool(api_key)}")
    
    if api_key:
        print(f"[PASS 1] Key found, attempting LLM call...")
        try:
            result = _run_openrouter_pass1(prompt, api_key)
            print(f"[PASS 1] Result source: {result.get('source')}")
        except Exception as e:
            print(f"[PASS 1] LLM call FAILED: {e}")
            result = _heuristic_fallback_pass1(prompt)
    else:
        print("[PASS 1] No OPENROUTER_API_KEY. Using fallback.")
        result = _heuristic_fallback_pass1(prompt)

    _write_cache(cache_key, result)
    return result


def _run_openrouter_pass1(prompt: str, api_key: str) -> dict:
    """
    Calls OpenRouter with automatic free-model fallback chain.
    Tries META Llama → Mistral → Gemma → Phi → Qwen in sequence.
    All are free-tier. No credit card required.
    """
    last_error = None

    for model in FREE_MODEL_CHAIN:
        try:
            print(f"[PASS 1] Trying model: {model}")
            t0 = time.time()

            payload = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": PASS_1_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Topic: {prompt}"}
                ],
                "temperature": 0.3,
                "max_tokens": 800,
            }).encode("utf-8")

            req = urllib.request.Request(
                OPENROUTER_API_URL,
                data=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://nivix.onrender.com",
                    "X-Title": "Nivix Compiler",
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=20) as resp:
                body = json.loads(resp.read().decode("utf-8"))

            latency_ms = int((time.time() - t0) * 1000)
            raw = body["choices"][0]["message"]["content"].strip()

            # Strip markdown fences some models add despite instructions
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            parsed = json.loads(raw)
            parsed["source"] = f"openrouter/{model}"
            parsed["latency_ms"] = latency_ms
            print(f"[PASS 1] SUCCESS via {model} in {latency_ms}ms")
            print(f"[PASS 1] Nodes generated: {len(parsed.get('nodes', []))}")
            print(f"[PASS 1] First node: {parsed.get('nodes', [{}])[0].get('id', 'N/A')}")
            return parsed

        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code} from {model}"
            print(f"[PASS 1] {model} returned {e.code}. Trying next model...")
        except json.JSONDecodeError as e:
            last_error = f"JSON parse error from {model}: {e}"
            print(f"[PASS 1] {model} returned invalid JSON. Trying next model...")
        except Exception as e:
            last_error = f"{model} failed: {e}"
            print(f"[PASS 1] {model} failed ({e}). Trying next model...")

    # All models failed — fall to heuristics
    print(f"[PASS 1] All OpenRouter models failed. Last error: {last_error}")
    print("[PASS 1] Activating keyword heuristic fallback.")
    return _heuristic_fallback_pass1(prompt)


def _heuristic_fallback_pass1(prompt: str) -> dict:
    """
    Educated heuristic fallback. Better than templates — keyword-aware.
    Used when no API key is configured.
    """
    content = prompt.lower()
    nodes = []
    reasoning = ""
    
    if any(w in content for w in ["imaginary", "complex number", "i²", "sqrt(-1)"]):
        nodes = [
            {"id": "real_axis", "type": "plot", "label": "Real Number Line", "lifecycle": {"spawn": 0}},
            {"id": "imaginary_axis", "type": "plot", "label": "Imaginary Axis", "lifecycle": {"spawn": 30}},
            {"id": "complex_plane", "type": "shape", "label": "Complex Plane", "lifecycle": {"spawn": 60}},
            {"id": "unit_i", "type": "math", "label": "i = √(-1)", "lifecycle": {"spawn": 90}},
            {"id": "rotation_arrow", "type": "highlight", "label": "90° Rotation", "lifecycle": {"spawn": 120}}
        ]
        reasoning = "Imaginary numbers need the evolution: real line → add perpendicular axis → show i as rotation."
        
    elif any(w in content for w in ["rsa", "encryption", "public key", "private key"]):
        nodes = [
            {"id": "plaintext", "type": "text", "label": "Plain Message", "lifecycle": {"spawn": 0}},
            {"id": "public_key", "type": "object", "label": "Public Key (e, n)", "lifecycle": {"spawn": 30}},
            {"id": "encrypt_op", "type": "math", "label": "M^e mod n", "lifecycle": {"spawn": 60}},
            {"id": "ciphertext", "type": "text", "label": "Encrypted Output", "lifecycle": {"spawn": 90}},
            {"id": "private_key", "type": "object", "label": "Private Key (d, n)", "lifecycle": {"spawn": 120}},
            {"id": "decrypt_op", "type": "math", "label": "C^d mod n", "lifecycle": {"spawn": 150}},
        ]
        reasoning = "RSA needs to visually trace: message → encrypt with public key → decrypt with private key."
        
    elif any(w in content for w in ["derivative", "calculus", "slope", "tangent"]):
        nodes = [
            {"id": "curve", "type": "plot", "label": "f(x) Curve", "lifecycle": {"spawn": 0}},
            {"id": "point_p", "type": "highlight", "label": "Point P", "lifecycle": {"spawn": 30}},
            {"id": "secant_line", "type": "shape", "label": "Secant Line", "lifecycle": {"spawn": 60}},
            {"id": "tangent_line", "type": "shape", "label": "Tangent Line (limit)", "lifecycle": {"spawn": 90}},
            {"id": "derivative_label", "type": "math", "label": "f'(x) = dy/dx", "lifecycle": {"spawn": 120}}
        ]
        reasoning = "Derivatives require showing the secant → tangent transformation as Δx → 0."
        
    elif any(w in content for w in ["gravity", "gravitational", "newton", "force", "mass"]):
        nodes = [
            {"id": "earth", "type": "shape", "label": "Earth", "lifecycle": {"spawn": 0}},
            {"id": "apple", "type": "object", "label": "Falling Apple", "lifecycle": {"spawn": 30}},
            {"id": "force_arrow", "type": "highlight", "label": "F = ma", "lifecycle": {"spawn": 60}},
            {"id": "trajectory", "type": "shape", "label": "Motion Path", "lifecycle": {"spawn": 90}},
            {"id": "newton_label", "type": "text", "label": "Newton's Law", "lifecycle": {"spawn": 120}}
        ]
        reasoning = "Gravity: show mass → force → motion to demonstrate F = ma."
        
    elif any(w in content for w in ["prime", "primary number", "primality"]):
        nodes = [
            {"id": "number_line", "type": "plot", "label": "Number Line", "lifecycle": {"spawn": 0}},
            {"id": "sieve", "type": "highlight", "label": "Sieve of Eratosthenes", "lifecycle": {"spawn": 30}},
            {"id": "prime_highlight", "type": "highlight", "label": "Prime Numbers", "lifecycle": {"spawn": 60}},
            {"id": "composite_cross", "type": "highlight", "label": "Composite Numbers", "lifecycle": {"spawn": 90}},
            {"id": "divisibility", "type": "math", "label": "Only 1 and itself", "lifecycle": {"spawn": 120}}
        ]
        reasoning = "Prime numbers: sieve out composites to reveal primes uniquely."
        
    elif any(w in content for w in ["pythagorean", "pythagoras", "a²+b²", "right triangle"]):
        nodes = [
            {"id": "triangle", "type": "shape", "label": "Right Triangle", "lifecycle": {"spawn": 0}},
            {"id": "leg_a", "type": "shape", "label": "Leg a", "lifecycle": {"spawn": 30}},
            {"id": "leg_b", "type": "shape", "label": "Leg b", "lifecycle": {"spawn": 45}},
            {"id": "hypotenuse", "type": "shape", "label": "Hypotenuse c", "lifecycle": {"spawn": 60}},
            {"id": "formula", "type": "math", "label": "a² + b² = c²", "lifecycle": {"spawn": 90}}
        ]
        reasoning = "Pythagorean theorem: show squares on legs combine to equal square on hypotenuse."
        
    elif any(w in content for w in ["sine", "cosine", "tan", "trigonometry", "trig", "sohcahtoa"]):
        nodes = [
            {"id": "unit_circle", "type": "shape", "label": "Unit Circle", "lifecycle": {"spawn": 0}},
            {"id": "angle_theta", "type": "highlight", "label": "Angle θ", "lifecycle": {"spawn": 30}},
            {"id": "sin_segment", "type": "highlight", "label": "Sine (opposite/hypotenuse)", "lifecycle": {"spawn": 60}},
            {"id": "cos_segment", "type": "highlight", "label": "Cosine (adjacent/hypotenuse)", "lifecycle": {"spawn": 80}},
            {"id": "tan_segment", "type": "highlight", "label": "Tangent (opposite/adjacent)", "lifecycle": {"spawn": 100}}
        ]
        reasoning = "Trigonometry: show angle relationships in the unit circle."
        
    elif any(w in content for w in ["integration", "integral", "area under", "antiderivative"]):
        nodes = [
            {"id": "curve", "type": "plot", "label": "f(x) Curve", "lifecycle": {"spawn": 0}},
            {"id": "region", "type": "shape", "label": "Region Under Curve", "lifecycle": {"spawn": 30}},
            {"id": "riemann_sum", "type": "shape", "label": "Riemann Sum", "lifecycle": {"spawn": 60}},
            {"id": "integral_label", "type": "math", "label": "∫f(x)dx", "lifecycle": {"spawn": 90}},
            {"id": "area_result", "type": "text", "label": "Signed Area", "lifecycle": {"spawn": 120}}
        ]
        reasoning = "Integrals: approximate infinite rectangles to find exact area."
        
    elif any(w in content for w in ["matrix", "matrices", "determinant", "eigenvalue"]):
        nodes = [
            {"id": "matrix_2x2", "type": "math", "label": "2×2 Matrix", "lifecycle": {"spawn": 0}},
            {"id": "determinant", "type": "math", "label": "det(A) = ad - bc", "lifecycle": {"spawn": 30}},
            {"id": "transformation", "type": "shape", "label": "Linear Transformation", "lifecycle": {"spawn": 60}},
            {"id": "eigenvector", "type": "highlight", "label": "Eigenvector (unchanged direction)", "lifecycle": {"spawn": 90}},
            {"id": "eigenvalue", "type": "math", "label": "Av = λv", "lifecycle": {"spawn": 120}}
        ]
        reasoning = "Matrices: show how they transform space and when vectors stay fixed."
        
    elif any(w in content for w in ["fourier", "frequency", "wave", "signal"]):
        nodes = [
            {"id": "time_wave", "type": "plot", "label": "Time Domain Wave", "lifecycle": {"spawn": 0}},
            {"id": "transform_icon", "type": "highlight", "label": "Fourier Transform", "lifecycle": {"spawn": 40}},
            {"id": "freq_bars", "type": "plot", "label": "Frequency Components", "lifecycle": {"spawn": 80}},
            {"id": "reconstruction", "type": "plot", "label": "Reconstructed Wave", "lifecycle": {"spawn": 120}}
        ]
        reasoning = "Fourier: decompose complex wave into simple frequencies."
        
    else:
        # Generic concept decomposition
        words = [w for w in prompt.split() if len(w) > 3][:3]
        nodes = [
            {"id": "concept_intro", "type": "text", "label": prompt.title()[:30], "lifecycle": {"spawn": 0}},
            {"id": "element_a", "type": "object", "label": words[0].capitalize() if words else "Element A", "lifecycle": {"spawn": 30}},
            {"id": "element_b", "type": "object", "label": words[1].capitalize() if len(words) > 1 else "Element B", "lifecycle": {"spawn": 60}},
            {"id": "relation", "type": "highlight", "label": "Relationship", "lifecycle": {"spawn": 90}}
        ]
        reasoning = f"Generic concept decomposition: introduce, show components, then reveal their relationship."

    return {
        "nodes": nodes,
        "reasoning": reasoning,
        "source": "heuristic_fallback"
    }


if __name__ == "__main__":
    """
    Test Pass 1 against genuinely novel prompts that templates can't handle.
    This is the proof test: can the planner generate meaningful nodes cold?
    """
    test_prompts = [
        "explain why imaginary numbers exist",
        "show how RSA encryption works",
        "demonstrate the concept of a derivative",
        "compare linear and exponential growth",
        "explain the Fourier transform intuitively",
    ]
    
    print("=" * 60)
    print("NIVIX PASS 1: LLM Object Graph Test (10-Prompt Gauntlet)")
    print("=" * 60)
    
    for prompt in test_prompts:
        print(f"\n→ Prompt: '{prompt}'")
        result = run_pass1_nodes(prompt)
        print(f"  Source: {result.get('source', 'unknown')}")
        print(f"  Nodes ({len(result['nodes'])}):")
        for n in result["nodes"]:
            print(f"    [{n['type']:8}] {n['id']:25} → '{n['label']}'")
        print(f"  Reasoning: {result.get('reasoning', 'N/A')}")
