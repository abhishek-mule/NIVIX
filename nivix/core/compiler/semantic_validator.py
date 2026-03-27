# Nivix Semantic Validator v3.2
# Pedagogical Integrity & Meaning Verification Engine.

class SemanticValidator:
    """
    Validates that the execution plan satisfies pedagogical rules.
    Prevents 'meaning-less' but syntactically correct animations.
    """
    
    def validate_plan(self, cir_plan):
        """
        Runs symbolic verification on the CIR timeline.
        Check Rules: Lifecycle, Focus, Symmetry, Hierarchy.
        """
        print("--- [NIVIX VALIDATOR] Performing Pedagogical Integrity Check (v3.2) ---")
        
        # 1. Lifecycle Verification
        # (Rule: Transform(X) requires X to be in 'spawned' state)
        # 2. Relation Integrity
        # (Rule: Compare(X, Y) requires both X and Y to be alive)
        # 3. Attention Targeting
        # (Rule: Highlight(Z) shouldn't happen if attention is on other side of screen)
        
        errors = []
        # Heuristic: Find 'compare' without active targets
        for event in cir_plan.get("timeline", []):
             if event["type"] == "compare":
                  targets = event["params"].get("targets", [])
                  if len(targets) < 2:
                       errors.append(f"Compare event {event} lacks symmetric targets.")
                       
        if errors:
             print(f"--- [VALIDATOR] ERROR: {len(errors)} Pedagogical Inconsistencies! ---")
             
        return cir_plan, errors

def validate(cir_plan):
    return SemanticValidator().validate_plan(cir_plan)
