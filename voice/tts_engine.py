
import os
import re
import time
import torch
import soundfile as sf
from pydub import AudioSegment


def smart_chunk(text, max_chars=240):
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) > max_chars:
            if current:
                chunks.append(current.strip())
            current = s
        else:
            current += " " + s
    if current:
        chunks.append(current.strip())
    return chunks


def load_tts_model(model_name):
    from qwen_tts import Qwen3TTSModel
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    print("Loading TTS model " + model_name + " on " + device + "...")
    model = Qwen3TTSModel.from_pretrained(model_name, device_map=device, dtype=dtype)
    print("TTS model loaded.")
    return model


def generate_chunk_audio(model, text, voice_profile, language="English"):
    """
    Generates one chunk of audio. Uses the cached prompt object if
    available (fast path, no re-encoding of reference audio); otherwise
    falls back to raw ref_audio + ref_text (slower, always works).
    """
    if voice_profile["is_cached"] and voice_profile["prompt_obj"] is not None:
        try:
            wavs, sr = model.generate_voice_clone(
                text=text,
                language=language,
                voice_clone_prompt=voice_profile["prompt_obj"],
                temperature=0.6,
                do_sample=True,
                max_new_tokens=4096,
            )
            return wavs, sr
        except TypeError:
            print("Installed qwen-tts version does not accept voice_clone_prompt kwarg - falling back to raw audio mode for this call.")

    wavs, sr = model.generate_voice_clone(
        text=text,
        language=language,
        ref_audio=voice_profile["ref_audio_path"],
        ref_text=voice_profile["ref_text"],
        x_vector_only_mode=True,
        temperature=0.6,
        do_sample=True,
        max_new_tokens=4096,
    )
    return wavs, sr


def generate_narration(model, script_text, voice_profile, work_dir, output_path,
                        max_chars=240, language="English"):
    os.makedirs(work_dir, exist_ok=True)

    chunks = smart_chunk(script_text, max_chars=max_chars)
    print("Total chunks: " + str(len(chunks)))

    chunk_paths = []
    for i, chunk in enumerate(chunks):
        out_path = os.path.join(work_dir, "chunk_" + str(i).zfill(3) + ".wav")

        if os.path.exists(out_path):
            print("Skipping chunk " + str(i+1) + "/" + str(len(chunks)) + " (already exists)")
            chunk_paths.append(out_path)
            continue

        print("\nChunk " + str(i+1) + "/" + str(len(chunks)) + ": " + chunk[:70] + ("..." if len(chunk) > 70 else ""))
        t0 = time.time()

        wavs, sr = generate_chunk_audio(model, chunk, voice_profile, language=language)

        if wavs is None or len(wavs) == 0:
            print("WARNING: model returned no audio for this chunk, skipping.")
            continue

        elapsed = time.time() - t0
        duration = len(wavs[0]) / sr
        print("Generated in " + str(round(elapsed,1)) + "s -> " + str(round(duration,2)) + "s of audio")

        sf.write(out_path, wavs[0], sr)
        chunk_paths.append(out_path)

    print("\nMerging " + str(len(chunk_paths)) + " chunks...")
    final = AudioSegment.silent(duration=200)
    for p in chunk_paths:
        seg = AudioSegment.from_wav(p)
        final += seg.fade_in(10).fade_out(10)
        final += AudioSegment.silent(duration=120)

    final = final.normalize()
    final.export(output_path, format="mp3")

    print("Saved final narration to " + output_path)
    return output_path
