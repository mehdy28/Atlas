
import os

ATLAS_DIR = "/content/Atlas"

STEPS = [
    "generate_script.py",
    "generate_narration.py",
    "align_script.py",
    "resolve_graphics_timing.py",
    "build_timeline.py",
    "apply_editing.py",
    "render_video.py",
    "add_graphics.py",
]

for fname in STEPS:
    path = os.path.join(ATLAS_DIR, fname)
    with open(path) as f:
        code = f.read()
    exec(compile(code, path, "exec"), {"__name__": "__main__"})

print("\n" + "="*70)
print("DONE. Final video: /content/drive/MyDrive/AtlasData/production/video.mp4")
print("="*70)
