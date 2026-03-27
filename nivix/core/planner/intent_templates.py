# Nivix Intent Template Registry v3.8
# Pedagogical Skeletons: Strategic Intent Priors.

class IntentTemplateRegistry:
    """
    Provides pre-optimized narrative skeletons for high-level prompts.
    Translates 'Compare' or 'Derive' into a set of CIR-compatible blocks.
    """
    
    INTENT_SKELETONS = {
        "compare": {
            "phases": [
                {"type": "spawn", "goals": ["symmetric_entry"]},
                {"type": "align", "params": {"axis": "horizontal"}},
                {"type": "emphasize", "goals": ["contrast_features"]},
                {"type": "conclusion", "goals": ["synthesis_summary"]}
            ]
        },
        "derive": {
            "phases": [
                {"type": "spawn", "goals": ["base_axiom"]},
                {"type": "sequence", "goals": ["step_by_step_morph"]},
                {"type": "highlight", "goals": ["final_result"]}
            ]
        },
        "prove": {
            "phases": [
                {"type": "visualization", "goals": ["establish_evidence"]},
                {"type": "reveal", "goals": ["link_to_equation"]},
                {"type": "summary", "goals": ["conclusion_stating"]}
            ]
        }
    }

    def get_skeleton(self, intent_type):
        return self.INTENT_SKELETONS.get(intent_type.lower())

def get_intent_prior(intent_type):
    return IntentTemplateRegistry().get_skeleton(intent_type)
