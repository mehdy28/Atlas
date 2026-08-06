
import os
import sys
import subprocess

ATLAS_DIR = "/content/Atlas"

print("Installing/verifying dependencies from requirements.txt...")
result = subprocess.run(
    ["pip", "install", "-q", "-r", os.path.join(ATLAS_DIR, "requirements.txt")],
    capture_output=True, text=True
)
if result.returncode != 0:
    print("WARNING: pip install had issues:")
    print(result.stderr[-2000:])
else:
    print("Dependencies installed.\n")

# Also handle system-level packages pip cannot install
subprocess.run(["apt-get", "-y", "-qq", "install", "ffmpeg"], capture_output=True)

_project_prefixes = (
    "config", "director", "voice", "alignment", "timeline",
    "editor", "renderer", "search", "collectors", "splitter", "captioner",
)
for mod_name in list(sys.modules.keys()):
    if mod_name in _project_prefixes or any(mod_name.startswith(p + ".") for p in _project_prefixes):
        del sys.modules[mod_name]

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
