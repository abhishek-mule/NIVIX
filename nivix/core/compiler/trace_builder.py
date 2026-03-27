# Nivix Execution Trace Engine v2.9
# Deterministic Debugging & Replay Layer.

import json
from dataclasses import asdict

class ExecutionTraceBuilder:
    """
    Captures the final 'State Trace' of every object in the narrative.
    Used for debugging, replay, and backend parity validation.
    """
    
    def build_trace(self, cir_plan):
        """
        Input: Optimized CIR Plan.
        Output: A flattened list of lifecycle events per object.
        """
        print("--- [NIVIX TRACE] Capturing Execution Blueprint (v2.9) ---")
        
        trace = {
            "version": "2.9",
            "metadata": cir_plan.get("metadata", {}),
            "object_timelines": {}
        }
        
        for event in cir_plan.get("timeline", []):
             obj_id = event["target"]
             if obj_id not in trace["object_timelines"]:
                  trace["object_timelines"][obj_id] = []
                  
             # Capture a normalized snapshot of this lifecycle event
             trace["object_timelines"][obj_id].append({
                 "type": event["type"],
                 "start": event["t"],
                 "end": event["t"] + event["d"],
                 "params": event.get("params", {})
             })
             
        return trace

def capture_trace(cir_plan):
    return ExecutionTraceBuilder().build_trace(cir_plan)
