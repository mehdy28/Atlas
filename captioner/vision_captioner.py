import torch
from PIL import Image
from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
    BlipTextModel,
)

_device = "cuda" if torch.cuda.is_available() else "cpu"
_processor = None
_model = None


# ============================================================
# Compatibility patch for BLIP + newer Transformers
# ============================================================
#
# Some newer Transformers versions no longer expose
# get_head_mask() on BlipTextModel, while the BLIP generation
# implementation still calls it.
#
# BLIP does not use a custom head mask in our captioning path,
# so returning [None] for each transformer layer is sufficient.
#
if not hasattr(BlipTextModel, "get_head_mask"):

    def _blip_get_head_mask(self, head_mask, num_hidden_layers):
        if head_mask is None:
            return [None] * num_hidden_layers

        # Basic compatibility for an explicitly supplied mask.
        if head_mask.dim() == 1:
            head_mask = head_mask[None, None, :, None, None]
        elif head_mask.dim() == 2:
            head_mask = head_mask[:, None, :, None, None]

        return head_mask.to(
            dtype=self.dtype,
            device=self.device,
        ).unbind(dim=0)

    BlipTextModel.get_head_mask = _blip_get_head_mask


# ============================================================
# Model loading
# ============================================================

def load_model():
    """Loads the BLIP captioning model once and keeps it warm in memory."""

    global _processor, _model

    if _model is None:

        print(f"Loading BLIP captioning model onto {_device}...")

        _processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )

        _model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )

        _model.to(_device)

        if _device == "cuda":
            _model = _model.half()

        _model.eval()

        print("Model loaded.")

    return _processor, _model


# ============================================================
# Caption generation
# ============================================================

def caption_batch(image_paths, max_new_tokens=30):

    processor, model = load_model()

    images = []
    valid_indices = []

    for i, path in enumerate(image_paths):

        try:
            img = Image.open(path).convert("RGB")
            images.append(img)
            valid_indices.append(i)

        except Exception as e:
            print(f"Skipping image {path}: {e}")

    results = [None] * len(image_paths)

    if not images:
        return results

    inputs = processor(
        images=images,
        return_tensors="pt"
    )

    inputs = {
        k: v.to(_device)
        for k, v in inputs.items()
    }

    # Keep image tensors in FP16 on CUDA.
    if _device == "cuda":
        inputs = {
            k: (
                v.half()
                if v.dtype.is_floating_point
                else v
            )
            for k, v in inputs.items()
        }

    with torch.no_grad():

        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
        )

    captions = processor.batch_decode(
        out,
        skip_special_tokens=True
    )

    for idx, caption in zip(valid_indices, captions):
        results[idx] = caption.strip()

    return results