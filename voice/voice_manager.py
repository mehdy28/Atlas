
import os
import json
import shutil
import torch


def list_voices(voices_dir):
    """Returns a list of dicts: {name, path, metadata}."""
    if not os.path.exists(voices_dir):
        return []
    voices = []
    for name in sorted(os.listdir(voices_dir)):
        voice_dir = os.path.join(voices_dir, name)
        meta_path = os.path.join(voice_dir, "metadata.json")
        prompt_path = os.path.join(voice_dir, "voice_clone_prompt.pt")
        if not os.path.isdir(voice_dir) or not os.path.exists(prompt_path):
            continue
        metadata = {}
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                metadata = json.load(f)
        voices.append({"name": name, "path": voice_dir, "metadata": metadata})
    return voices


def create_voice_profile(model, voices_dir, voice_name, ref_audio_path, ref_text, language="English"):
    """
    Extracts a reusable speaker-embedding prompt from the reference audio
    ONCE, and persists it to Drive so future sessions never need to
    re-encode the reference audio again.
    """
    voice_dir = os.path.join(voices_dir, voice_name)
    if os.path.exists(voice_dir):
        raise ValueError("A voice named '" + voice_name + "' already exists. Choose a different name.")
    os.makedirs(voice_dir, exist_ok=True)

    print("Extracting reusable speaker embedding from reference audio (one-time cost)...")

    prompt_obj = None
    creation_method = None

    if hasattr(model, "create_voice_clone_prompt"):
        try:
            prompt_obj = model.create_voice_clone_prompt(
                ref_audio=ref_audio_path,
                ref_text=ref_text,
            )
            creation_method = "create_voice_clone_prompt"
        except Exception as e:
            print("create_voice_clone_prompt failed (" + str(e) + "), will fall back to raw ref_audio/ref_text at generation time.")

    ref_audio_ext = os.path.splitext(ref_audio_path)[1] or ".wav"
    saved_ref_audio_path = os.path.join(voice_dir, "reference" + ref_audio_ext)
    shutil.copy2(ref_audio_path, saved_ref_audio_path)

    with open(os.path.join(voice_dir, "reference_text.txt"), "w", encoding="utf-8") as f:
        f.write(ref_text)

    prompt_saved = False
    if prompt_obj is not None:
        try:
            torch.save(prompt_obj, os.path.join(voice_dir, "voice_clone_prompt.pt"))
            prompt_saved = True
        except Exception as e:
            print("Could not save extracted prompt object (" + str(e) + "). Will use raw audio/text fallback instead.")

    if not prompt_saved:
        # Fallback: save a placeholder marker so list_voices() still finds this
        # profile; generation will recompute the embedding from ref_audio/ref_text
        # every time, which is slower but always works.
        torch.save({"fallback_mode": True}, os.path.join(voice_dir, "voice_clone_prompt.pt"))

    metadata = {
        "name": voice_name,
        "language": language,
        "creation_method": creation_method or "fallback_raw_audio",
        "cached_embedding": prompt_saved,
    }
    with open(os.path.join(voice_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print("Voice profile '" + voice_name + "' saved to " + voice_dir)
    print("Cached embedding: " + str(prompt_saved) + (" (fast path)" if prompt_saved else " (fallback: will re-encode ref audio each generation)"))

    return voice_dir


def load_voice_profile(voice_dir):
    """
    Returns a dict: {prompt_obj or None, ref_audio_path, ref_text, is_cached}
    """
    prompt_path = os.path.join(voice_dir, "voice_clone_prompt.pt")
    prompt_obj = torch.load(prompt_path, weights_only=False)

    is_cached = not (isinstance(prompt_obj, dict) and prompt_obj.get("fallback_mode"))

    ref_audio_path = None
    for fname in os.listdir(voice_dir):
        if fname.startswith("reference.") and not fname.endswith(".txt"):
            ref_audio_path = os.path.join(voice_dir, fname)
            break

    ref_text_path = os.path.join(voice_dir, "reference_text.txt")
    ref_text = ""
    if os.path.exists(ref_text_path):
        with open(ref_text_path, encoding="utf-8") as f:
            ref_text = f.read()

    return {
        "prompt_obj": prompt_obj if is_cached else None,
        "ref_audio_path": ref_audio_path,
        "ref_text": ref_text,
        "is_cached": is_cached,
    }
