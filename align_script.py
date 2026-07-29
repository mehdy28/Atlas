
import os
import sys
import glob
import json
import sqlite3

sys.path.append("/content/Atlas")

from config import DRIVE_DB_PATH, PRODUCTION_DIR, SCRIPT_PATH, WHISPER_MODEL_SIZE
from alignment.aligner import transcribe_with_word_timestamps, load_script_paragraphs, align_paragraphs_to_audio

audio_candidates = glob.glob(f"{PRODUCTION_DIR}/narration.*")
if not audio_candidates:
    raise SystemExit(f"No narration audio file found in {PRODUCTION_DIR}. Upload it first.")
audio_path = audio_candidates[0]
print(f"Using audio file: {audio_path}")

if not os.path.exists(SCRIPT_PATH):
    raise SystemExit(f"Script file not found at {SCRIPT_PATH}. Upload it first.")

paragraphs = load_script_paragraphs(SCRIPT_PATH)
print(f"Loaded {len(paragraphs)} paragraphs from script.")

print("Transcribing audio with Whisper (this can take a few minutes for longer audio)...")
whisper_words = transcribe_with_word_timestamps(audio_path, model_size=WHISPER_MODEL_SIZE)
print(f"Transcribed {len(whisper_words)} words from audio.")

aligned = align_paragraphs_to_audio(paragraphs, whisper_words)

print("\nAlignment results:")
for a in aligned:
    dur = (a["end_seconds"] - a["start_seconds"]) if (a["start_seconds"] is not None and a["end_seconds"] is not None) else None
    dur_str = f"{dur:.1f}s" if dur is not None else "UNRESOLVED"
    preview = a["text"][:60] + ("..." if len(a["text"]) > 60 else "")
    print(f"  [{a[\'paragraph_index\']}] {a[\'start_seconds\']} -> {a[\'end_seconds\']} ({dur_str}) | {preview}")

unresolved = [a for a in aligned if a["start_seconds"] is None or a["end_seconds"] is None]
if unresolved:
    print(f"\nWARNING: {len(unresolved)} paragraph(s) could not be aligned. Review before building the timeline.")

output_path = f"{PRODUCTION_DIR}/paragraph_timings.json"
with open(output_path, "w") as f:
    json.dump(aligned, f, indent=2)

print(f"\nSaved paragraph timings to {output_path}")
print("Done.")
