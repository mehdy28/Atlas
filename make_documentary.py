
import os

ATLAS_DIR = "/content/Atlas"

STEPS = [
    ("generate_script.py",          "Gemini script + graphics plan"),
    ("generate_narration.py",       "Voice selection/creation + TTS narration"),
    ("align_script.py",             "Whisper alignment (word timestamps)"),
    ("resolve_graphics_timing.py",  "Resolve graphics trigger phrases to exact timestamps"),
    ("build_timeline.py",           "Match footage clips to narration via semantic search"),
    ("apply_editing.py",            "Apply Ken Burns motion effects"),
    ("render_video.py",             "Render base video (clips + grading + audio)"),
    ("add_graphics.py",             "Composite motion graphics onto final video"),
]

print("="*70)
print("ATLAS - FULL DOCUMENTARY PIPELINE")
print("="*70)
for i, (fname, desc) in enumerate(STEPS, start=1):
    print("  " + str(i) + ". " + desc)

resume_input = input("\nStart from step (1-" + str(len(STEPS)) + ", default 1): ").strip()
start_index = int(resume_input) - 1 if resume_input else 0

if start_index < 0 or start_index >= len(STEPS):
    raise SystemExit("Invalid step number.")

for i in range(start_index, len(STEPS)):
    fname, desc = STEPS[i]
    path = os.path.join(ATLAS_DIR, fname)

    print("\n" + "="*70)
    print("STEP " + str(i+1) + "/" + str(len(STEPS)) + ": " + desc)
    print("(" + fname + ")")
    print("="*70 + "\n")

    with open(path) as f:
        code = f.read()

    try:
        exec(compile(code, path, "exec"), {"__name__": "__main__"})
    except SystemExit as e:
        print("\nStep " + fname + " exited early: " + str(e))
        raise
    except Exception as e:
        print("\n" + "!"*70)
        print("STEP " + str(i+1) + " (" + fname + ") FAILED: " + str(e))
        print("To resume after fixing, re-run make_documentary.py and start from step " + str(i+1) + ".")
        print("!"*70)
        raise

print("\n" + "="*70)
print("ALL STEPS COMPLETE")
print("Final video: /content/drive/MyDrive/AtlasData/production/video.mp4")
print("="*70)
