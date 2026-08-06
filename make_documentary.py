
import os
import sys

ATLAS_DIR = "/content/Atlas"

# Clear any stale cached modules from this project before running, so
# edits made earlier in the session (e.g. to config.py) are always
# picked up fresh rather than silently reusing an outdated cached version.
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
