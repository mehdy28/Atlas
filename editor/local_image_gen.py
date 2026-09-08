
import os
import gc
import torch


_pipe = None


def load_sd_pipeline(model_name):
    global _pipe
    if _pipe is not None:
        return _pipe

    from diffusers import AutoPipelineForText2Image

    print("Loading Stable Diffusion (" + model_name + ")...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    _pipe = AutoPipelineForText2Image.from_pretrained(model_name, torch_dtype=dtype)
    _pipe = _pipe.to(device)
    print("Stable Diffusion loaded on " + device + ".")
    return _pipe


def generate_images_batch(prompts_with_indices, output_dir, model_name,
                           steps=4, width=768, height=512):
    """
    prompts_with_indices: list of {"paragraph_index": int, "prompt": str}
    Returns list of {"paragraph_index": int, "image_path": str}
    """
    os.makedirs(output_dir, exist_ok=True)
    pipe = load_sd_pipeline(model_name)

    results = []
    for item in prompts_with_indices:
        p_idx = item["paragraph_index"]
        prompt = item["prompt"]

        try:
            image = pipe(
                prompt=prompt,
                num_inference_steps=steps,
                guidance_scale=0.0,  # sd-turbo is distilled for guidance_scale=0
                width=width, height=height,
            ).images[0]

            out_path = os.path.join(output_dir, "generated_p" + str(p_idx) + ".png")
            image.save(out_path)
            results.append({"paragraph_index": p_idx, "image_path": out_path, "prompt": prompt})
            print("Generated image for paragraph " + str(p_idx) + ": " + prompt[:60])
        except Exception as e:
            print("Image generation FAILED for paragraph " + str(p_idx) + ": " + str(e))

    return results


def unload_sd_pipeline():
    """
    Explicitly frees the Stable Diffusion pipeline from GPU memory.
    Must be called before Whisper/BLIP/TTS need the GPU later in the
    same pipeline run, or they will compete for VRAM.
    """
    global _pipe
    if _pipe is not None:
        del _pipe
        _pipe = None
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    print("Stable Diffusion unloaded, GPU memory freed.")
