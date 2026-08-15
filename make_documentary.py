
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import sys
import subprocess
import json
import io
from contextlib import redirect_stdout

ATLAS_DIR = "/content/Atlas"

print("Installing/verifying dependencies from requirements.txt...")
subprocess.run(["pip", "install", "-q", "-r", os.path.join(ATLAS_DIR, "requirements.txt")], capture_output=True)
subprocess.run(["apt-get", "-y", "-qq", "install", "ffmpeg", "libxcb-cursor0"], capture_output=True)

_project_prefixes = (
    "config", "director", "voice", "alignment", "timeline",
    "editor", "renderer", "search", "collectors", "splitter", "captioner",
)
for mod_name in list(sys.modules.keys()):
    if mod_name in _project_prefixes or any(mod_name.startswith(p + ".") for p in _project_prefixes):
        del sys.modules[mod_name]

def run_step(fname, capture=False):
    path = os.path.join(ATLAS_DIR, fname)
    print("\\n" + "="*70 + "\\nRUNNING: " + fname + "\\n" + "="*70)
    with open(path) as f:
        code = f.read()
    if capture:
        buf = io.StringIO()
        with redirect_stdout(buf):
            exec(compile(code, path, "exec"), {"__name__": "__main__"})
        output = buf.getvalue()
        print(output)
        return output
    else:
        exec(compile(code, path, "exec"), {"__name__": "__main__"})
        return ""

CORE_STEPS = [
    "generate_script.py",
    "discover_footage.py",
    "split_scenes.py",
    "caption_scenes.py",
    "build_index.py",
    "generate_narration.py",
    "align_script.py",
    "resolve_graphics_timing.py",
    "build_timeline.py",
]

for fname in CORE_STEPS:
    run_step(fname)

from config import LOW_RELEVANCE_PARAGRAPHS_PATH
with open(LOW_RELEVANCE_PARAGRAPHS_PATH) as f:
    low_relevance = json.load(f)

if low_relevance:
    print("\\n" + "="*70)
    print(str(len(low_relevance)) + " paragraph(s) below relevance threshold. Trying to resolve smartly...")
    print("="*70)
    boost_output = run_step("boost_footage.py", capture=True)

    if "NEEDS_NEW_FOOTAGE=true" in boost_output:
        print("\\nNew footage was discovered - reprocessing (split/caption/index)...")
        run_step("split_scenes.py")
        run_step("caption_scenes.py")
        run_step("build_index.py")
    else:
        print("\\nAll paragraphs resolved from existing footage - no reprocessing needed.")

    run_step("build_timeline.py")
else:
    print("\\nNo boost needed - footage matched well across all paragraphs.")

FINAL_STEPS = [
    "apply_editing.py",
    "render_video.py",
    "add_graphics.py",
]

for fname in FINAL_STEPS:
    run_step(fname)

print("\\n" + "="*70)
print("DONE. Final video: /content/drive/MyDrive/AtlasData/production/video.mp4")
print("="*70)
