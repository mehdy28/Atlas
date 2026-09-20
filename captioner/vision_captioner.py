import torch
import transformers.modeling_utils as mu
import transformers.pytorch_utils as pu

if hasattr(pu, "apply_chunking_to_forward"):
    mu.apply_chunking_to_forward = pu.apply_chunking_to_forward
if hasattr(pu, "prune_linear_layer"):
    mu.prune_linear_layer = pu.prune_linear_layer

def find_pruneable_heads_and_indices(heads, n_heads, head_size, already_pruned_heads):
    mask = torch.ones(n_heads, head_size)
    heads = set(heads) - already_pruned_heads
    for head in heads:
        head = head - sum(1 if h < head else 0 for h in already_pruned_heads)
        mask[head] = 0
    mask = mask.view(-1).contiguous().eq(1)
    index = torch.arange(len(mask))[mask].long()
    return heads, index

mu.find_pruneable_heads_and_indices = find_pruneable_heads_and_indices
pu.find_pruneable_heads_and_indices = find_pruneable_heads_and_indices

import transformers.pytorch_utils
import transformers.modeling_utils
if not hasattr(transformers.modeling_utils, "apply_chunking_to_forward"):
    transformers.modeling_utils.apply_chunking_to_forward = transformers.pytorch_utils.apply_chunking_to_forward


import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

_device = "cuda" if torch.cuda.is_available() else "cpu"
_processor = None
_model = None


def load_model():
    """Loads the BLIP captioning model once and keeps it warm in memory."""
    global _processor, _model
    if _model is None:
        print(f"Loading BLIP captioning model onto {_device}...")
        _processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        _model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        _model.to(_device)
        if _device == "cuda":
            _model = _model.half()
        _model.eval()
        print("Model loaded.")
    return _processor, _model


def caption_batch(image_paths, max_new_tokens=30):
    """
    Captions a batch of images in one forward pass.
    Returns a list of captions (or None for images that failed to load),
    same length and order as image_paths.
    """
    processor, model = load_model()

    images = []
    valid_indices = []
    for i, path in enumerate(image_paths):
        try:
            img = Image.open(path).convert("RGB")
            images.append(img)
            valid_indices.append(i)
        except Exception:
            pass

    results = [None] * len(image_paths)
    if not images:
        return results

    inputs = processor(images=images, return_tensors="pt").to(_device)
    if _device == "cuda":
        inputs = {k: (v.half() if v.dtype.is_floating_point else v) for k, v in inputs.items()}

    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens)

    captions = processor.batch_decode(out, skip_special_tokens=True)

    for idx, caption in zip(valid_indices, captions):
        results[idx] = caption.strip()

    return results
