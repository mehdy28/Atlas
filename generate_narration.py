
import os
import sys

sys.path.append("/content/Atlas")

from config import VOICES_DIR, SCRIPT_PATH, TTS_MODEL_NAME, TTS_CHUNK_MAX_CHARS, TTS_WORK_DIR, NARRATION_OUTPUT_PATH, TTS_BATCH_SIZE
from voice.voice_manager import list_voices, create_voice_profile, load_voice_profile
from voice.tts_engine import load_tts_model, generate_narration

os.makedirs(VOICES_DIR, exist_ok=True)

if not os.path.exists(SCRIPT_PATH):
    raise SystemExit("No script found at " + SCRIPT_PATH + ". Run generate_script.py first.")

with open(SCRIPT_PATH, encoding="utf-8") as f:
    script_text = f.read()

print("Script loaded (" + str(len(script_text)) + " characters).\n")

existing = list_voices(VOICES_DIR)

if existing:
    print("Existing voice profiles:")
    for idx, v in enumerate(existing):
        meta = v["metadata"]
        cached = "cached embedding" if meta.get("cached_embedding") else "fallback mode"
        print("  [" + str(idx) + "] " + v["name"] + " (" + meta.get("language","?") + ", " + cached + ")")
    print("  [n] Create a new voice")
else:
    print("No existing voice profiles found.")

choice = input("\nPick a voice number, or type 'n' for a new voice: ").strip().lower()

model = load_tts_model(TTS_MODEL_NAME)

if choice == "n" or not existing:
    voice_name = input("Name for this new voice (e.g. narrator_v1): ").strip()

    print("\nUpload a ~10 second reference audio clip of the voice (clear speech, minimal background noise).")
    from google.colab import files
    uploaded = files.upload()
    ref_filename = list(uploaded.keys())[0]
    tmp_ref_path = "/content/" + ref_filename
    with open(tmp_ref_path, "wb") as f:
        f.write(uploaded[ref_filename])

    print("\nType the EXACT transcript of what is said in that audio clip.")
    print("(Precision matters here - this is used to align the voice cloning.)")
    ref_text = input("Transcript: ").strip()

    language = input("Language (default English): ").strip() or "English"

    voice_dir = create_voice_profile(model, VOICES_DIR, voice_name, tmp_ref_path, ref_text, language=language)
else:
    idx = int(choice)
    voice_dir = existing[idx]["path"]
    print("Using voice: " + existing[idx]["name"])

voice_profile = load_voice_profile(voice_dir)

print("\nGenerating narration...")
generate_narration(
    model, script_text, voice_profile, TTS_WORK_DIR, NARRATION_OUTPUT_PATH,
    max_chars=TTS_CHUNK_MAX_CHARS,
    batch_size=TTS_BATCH_SIZE,
)

print("\nDone. Narration saved to " + NARRATION_OUTPUT_PATH)
