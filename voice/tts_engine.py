
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




def generate_chunk_audio_batch(model, texts, voice_profile, language="English"):
    """
    Attempts to generate multiple chunks in one call. If the installed
    qwen-tts version does not support list input, raises so the caller
    can fall back to one-at-a-time generation.
    """
    if voice_profile["is_cached"] and voice_profile["prompt_obj"] is not None:
        wavs, sr = model.generate_voice_clone(
            text=texts,
            language=language,
            voice_clone_prompt=voice_profile["prompt_obj"],
            temperature=0.6,
            do_sample=True,
            max_new_tokens=4096,
        )
    else:
        wavs, sr = model.generate_voice_clone(
            text=texts,
            language=language,
            ref_audio=voice_profile["ref_audio_path"],
            ref_text=voice_profile["ref_text"],
            x_vector_only_mode=True,
            temperature=0.6,
            do_sample=True,
            max_new_tokens=4096,
        )
    if not isinstance(wavs, (list, tuple)) or len(wavs) != len(texts):
        raise ValueError("Batch call did not return one waveform per input text - unsupported.")
    return wavs, sr


def generate_narration(model, script_text, voice_profile, work_dir, output_path,
                        max_chars=240, language="English", batch_size=4):
    os.makedirs(work_dir, exist_ok=True)

    chunks = smart_chunk(script_text, max_chars=max_chars)
    print("Total chunks: " + str(len(chunks)))
    print("Attempting batch size: " + str(batch_size))

    chunk_paths = []
    pending_indices = [i for i, c in enumerate(chunks)
                        if not os.path.exists(os.path.join(work_dir, "chunk_" + str(i).zfill(3) + ".wav"))]
    for i in range(len(chunks)):
        if i not in pending_indices:
            chunk_paths.append(os.path.join(work_dir, "chunk_" + str(i).zfill(3) + ".wav"))

    batching_works = True
    i = 0
    remaining = list(pending_indices)
    while remaining:
        batch_indices = remaining[:batch_size]
        remaining = remaining[batch_size:]
        batch_texts = [chunks[j] for j in batch_indices]

        t0 = time.time()
        used_batch = False
        if batching_works and len(batch_texts) > 1:
            try:
                wavs, sr = generate_chunk_audio_batch(model, batch_texts, voice_profile, language=language)
                used_batch = True
            except Exception as e:
                print("Batch generation unsupported (" + str(e) + "), falling back to one-at-a-time for remaining chunks.")
                batching_works = False

        if not used_batch:
            wavs = []
            sr = None
            for text in batch_texts:
                w, s = generate_chunk_audio(model, text, voice_profile, language=language)
                sr = s
                wavs.append(w[0] if isinstance(w, (list, tuple)) else w)

        elapsed = time.time() - t0
        print("Batch of " + str(len(batch_indices)) + " chunks generated in " + str(round(elapsed,1)) + "s" + (" (batched call)" if used_batch else " (sequential)"))

        for local_idx, chunk_idx in enumerate(batch_indices):
            out_path = os.path.join(work_dir, "chunk_" + str(chunk_idx).zfill(3) + ".wav")
            wav = wavs[local_idx]
            sf.write(out_path, wav, sr)
            chunk_paths.append(out_path)

    chunk_paths = [os.path.join(work_dir, "chunk_" + str(i).zfill(3) + ".wav") for i in range(len(chunks))
                    if os.path.exists(os.path.join(work_dir, "chunk_" + str(i).zfill(3) + ".wav"))]

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
