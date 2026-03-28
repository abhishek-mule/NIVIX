import os
import subprocess

def generate_all():
    print("--- 🎬 Generating Nivix Proof-of-Concept Tour Visuazliations ---\n")
    examples_dir = "examples"
    visuals_dir = os.path.join(examples_dir, "visuals")
    
    if not os.path.exists(visuals_dir):
        os.makedirs(visuals_dir)

    for file in os.listdir(examples_dir):
        if file.endswith(".txt") and file != "README.md":
            prompt_path = os.path.join(examples_dir, file)
            # Run the CLI explain visual command natively
            print(f"Generating trace for: {file}")
            # we capture output just to silence it, the file writes its own html
            subprocess.run(["python", "cli.py", "explain", prompt_path, "--visual"], stdout=subprocess.DEVNULL)
            
            # The CLI writes to nivix_visualizer.html. We will move it to the visuals folder.
            out_name = file.replace(".txt", "_tour.html")
            out_path = os.path.join(visuals_dir, out_name)
            if os.path.exists("nivix_visualizer.html"):
                os.replace("nivix_visualizer.html", out_path)
                print(f"✅ Saved Visual Tour to: {out_path}")

    print("\nAll interactive Proof-of-Concept tours generated successfully.")
    print(f"Explore them in: {visuals_dir}")

if __name__ == "__main__":
    generate_all()
