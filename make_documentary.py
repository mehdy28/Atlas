
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import sys
import subprocess
import json
import io
from contextlib import redirect_stdout

ATLAS_DIR = "/content/Atlas"

_data_dir = "/content/AtlasData"
for _sub in ["production", "voices", "config", "storage/videos", "storage/thumbnails",
             "storage/images", "storage/generated_images", "cache/videos"]:
    os.makedirs(os.path.join(_data_dir, _sub), exist_ok=True)
print("AtlasData directory structure ready at " + _data_dir)

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


def do_boost_and_rebuild():
    """Runs the boost/relevance-repair block: boost footage (incl. AI image
    generation fallback), conditionally reprocess, rebuild the timeline."""
    from config import LOW_RELEVANCE_PARAGRAPHS_PATH
    with open(LOW_RELEVANCE_PARAGRAPHS_PATH) as f:
        low_relevance = json.load(f)

    if not low_relevance:
        print("\\nNo boost needed - footage matched well across all paragraphs.")
        return

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


# Ordered pipeline: (label shown in resume menu, callable)
PIPELINE = [
    ("generate_script.py",        lambda: run_step("generate_script.py")),
    ("discover_footage.py",       lambda: run_step("discover_footage.py")),
    ("split_scenes.py",           lambda: run_step("split_scenes.py")),
    ("caption_scenes.py",         lambda: run_step("caption_scenes.py")),
    ("build_index.py",            lambda: run_step("build_index.py")),
    ("generate_narration.py",     lambda: run_step("generate_narration.py")),
    ("align_script.py",           lambda: run_step("align_script.py")),
    ("resolve_graphics_timing.py",lambda: run_step("resolve_graphics_timing.py")),
    ("build_timeline.py",         lambda: run_step("build_timeline.py")),
    ("boost + rebuild (incl. AI image gen fallback)", do_boost_and_rebuild),
    ("apply_editing.py",          lambda: run_step("apply_editing.py")),
    ("render_video.py",           lambda: run_step("render_video.py")),
    ("add_graphics.py",           lambda: run_step("add_graphics.py")),
]

print("\\nPipeline steps:")
for i, (label, _) in enumerate(PIPELINE):
    print("  " + str(i) + ". " + label)

resume_input = input("\\nResume from step number (press Enter to start from the beginning): ").strip()
start_index = int(resume_input) if resume_input else 0

if start_index < 0 or start_index >= len(PIPELINE):
    raise SystemExit("Invalid step number: " + str(start_index))

for label, fn in PIPELINE[start_index:]:
    fn()

print("\\n" + "="*70)
print("DONE. Final video: /content/AtlasData/production/video.mp4")
print("="*70)
