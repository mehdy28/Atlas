
import re
import difflib
from faster_whisper import WhisperModel

_whisper_model = None


def _load_whisper(model_size="medium"):
    global _whisper_model
    if _whisper_model is None:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        print(f"Loading Whisper ({model_size}) on {device}...")
        _whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)
    return _whisper_model


def _normalize_word(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def transcribe_with_word_timestamps(audio_path, model_size="medium"):
    """
    Returns a list of (normalized_word, start_seconds, end_seconds).
    """
    model = _load_whisper(model_size)
    segments, _ = model.transcribe(audio_path, word_timestamps=True)

    words = []
    for segment in segments:
        for word in segment.words:
            norm = _normalize_word(word.word)
            if norm:
                words.append((norm, word.start, word.end))
    return words


def load_script_paragraphs(script_path):
    """
    Splits script.txt into paragraphs on blank lines.
    Returns list of paragraph text strings, in order.
    """
    with open(script_path, "r", encoding="utf-8") as f:
        raw = f.read()

    chunks = re.split(r"\n\s*\n", raw.strip())
    paragraphs = [c.strip().replace("\n", " ") for c in chunks if c.strip()]
    return paragraphs


def align_paragraphs_to_audio(paragraphs, whisper_words):
    """
    Aligns script paragraphs against the whisper word-level transcript
    using sequence matching on normalized words. Returns a list of dicts:
    {paragraph_index, text, start_seconds, end_seconds}
    """
    script_word_norms = []
    script_word_paragraph_idx = []

    for p_idx, paragraph in enumerate(paragraphs):
        for raw_word in paragraph.split():
            norm = _normalize_word(raw_word)
            if norm:
                script_word_norms.append(norm)
                script_word_paragraph_idx.append(p_idx)

    whisper_word_norms = [w[0] for w in whisper_words]

    matcher = difflib.SequenceMatcher(None, script_word_norms, whisper_word_norms, autojunk=False)
    matching_blocks = matcher.get_matching_blocks()

    # script_index -> whisper_index, for words that matched directly
    script_to_whisper = {}
    for block in matching_blocks:
        for offset in range(block.size):
            script_to_whisper[block.a + offset] = block.b + offset

    matched_script_indices = sorted(script_to_whisper.keys())

    def nearest_whisper_time(script_idx, want_start):
        """Falls back to nearest matched neighbor if this exact word did not match."""
        if not matched_script_indices:
            return None
        import bisect
        pos = bisect.bisect_left(matched_script_indices, script_idx)
        candidates = []
        if pos < len(matched_script_indices):
            candidates.append(matched_script_indices[pos])
        if pos > 0:
            candidates.append(matched_script_indices[pos - 1])
        if not candidates:
            return None
        nearest = min(candidates, key=lambda i: abs(i - script_idx))
        w_idx = script_to_whisper[nearest]
        return whisper_words[w_idx][1] if want_start else whisper_words[w_idx][2]

    results = []
    for p_idx, paragraph_text in enumerate(paragraphs):
        word_indices = [i for i, pidx in enumerate(script_word_paragraph_idx) if pidx == p_idx]
        if not word_indices:
            continue

        first_idx, last_idx = word_indices[0], word_indices[-1]

        start_time = None
        for i in word_indices:
            if i in script_to_whisper:
                start_time = whisper_words[script_to_whisper[i]][1]
                break
        if start_time is None:
            start_time = nearest_whisper_time(first_idx, want_start=True)

        end_time = None
        for i in reversed(word_indices):
            if i in script_to_whisper:
                end_time = whisper_words[script_to_whisper[i]][2]
                break
        if end_time is None:
            end_time = nearest_whisper_time(last_idx, want_start=False)

        results.append({
            "paragraph_index": p_idx,
            "text": paragraph_text,
            "start_seconds": round(start_time, 2) if start_time is not None else None,
            "end_seconds": round(end_time, 2) if end_time is not None else None,
        })

    return results
