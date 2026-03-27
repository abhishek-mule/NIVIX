# Nivix Scene Preview Runner v3.9
# CIR Slicer: Partial Render & Replay Engine.

class ScenePreviewRunner:
    """
    Slices the execution timeline to enable fast, partial previews.
    Accepts: Canonical IR (CIR)
    Outputs: Partial CIR segment for the requested frame/segment.
    """
    
    def slice_timeline(self, cir, start_time, end_time=None):
        """
        Creates a 'Pre-filtered' CIR for a specific window.
        """
        print(f"--- [NIVIX PREVIEW] Slicing Timeline: {start_time}s to {end_time if end_time else 'End'}s ---")
        
        sliced_timeline = []
        for event in cir.get("timeline", []):
             t = event["t"]
             # Check if event falls within (or overlaps) the requested preview window
             if end_time:
                  if t >= start_time and t <= end_time:
                       sliced_timeline.append(event)
             else:
                  if t >= start_time:
                       sliced_timeline.append(event)
                       
        sliced_cir = cir.copy()
        sliced_cir["timeline"] = sliced_timeline
        return sliced_cir

def create_preview_cir(cir, t_start=0.0, t_end=3.0):
    return ScenePreviewRunner().slice_timeline(cir, t_start, t_end)
