# Nivix Intent Expectation Checker v3.5
# Cinematic Reasoning Auditor: Strategic Intent Verification.

class IntentExpectationChecker:
    """
    Final Pedagogical Auditor: Did the engine actually execute what the user wanted?
    Checks the high-level intent against the final execution trace.
    """
    
    def verify_intent(self, prompt, execution_trace):
        """
        Input: User Prompt, Execution Trace.
        Output: Confidence Score & Gap Analysis.
        """
        print(f"--- [NIVIX AUDIT] Verifying Narrative against Intent: '{prompt[:30]}...' ---")
        
        score = 1.0
        gaps = []
        
        # 1. Intent Matching (e.g. Compare requested -> Compare exists)
        # 2. Attention Proportionality (Is the focus object truly dominant?)
        # 3. Highlight Consistency (Were the most important terms emphasized?)
        
        if "compare" in prompt.lower():
             # Check if 'compare' event exists in the trace
             found_compare = any(e["type"] == "compare" for e in execution_trace.get("object_timelines", {}).values())
             if not found_compare:
                  score -= 0.3
                  gaps.append("Missing comparison event for comparison intent.")
                  
        print(f"--- [AUDIT] Intent Satisfaction Score: {score:.2f} (v3.5) ---")
        return score, gaps

def audit_intent(prompt, trace):
    return IntentExpectationChecker().verify_intent(prompt, trace)
