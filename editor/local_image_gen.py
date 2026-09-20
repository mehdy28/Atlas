import os
import gc
import torch

_pipe = None

def load_sd_pipeline(model_name):
    global _pipe
    if _pipe is not None:
        return _pipe

    from diffusers import AutoPipelineForText2Image, DPMSolverMultistepScheduler

    print("Loading Stable Diffusion (" + model_name + ") on cuda...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    _pipe = AutoPipelineForText2Image.from_pretrained(
        model_name, torch_dtype=dtype, safety_checker=None
    ).to(device)
    
    _pipe.scheduler = DPMSolverMultistepScheduler.from_config(
        _pipe.scheduler.config, use_karras_sigmas=True
    )
    print("Stable Diffusion loaded with DPM++ 2M Karras scheduler.")
    return _pipe

def unload_sd_pipeline():
    global _pipe
    if _pipe is not None:
        del _pipe
        _pipe = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("Stable Diffusion unloaded, GPU memory freed.")

def generate_images_batch(prompts_with_indices, output_dir, model_name,
                           steps=35, width=768, height=432):
    os.makedirs(output_dir, exist_ok=True)
    pipe = load_sd_pipeline(model_name)

    NEGATIVE_PROMPT = (
        "cartoon, 3D render, illustration, anime, drawing, painting, CGI, video game, "
        "blurry, distorted, plastic skin, 90s cgi, deformed, bad anatomy, artificial, disfigured, text, watermark"
    )

    results = []
    for item in prompts_with_indices:
        p_idx = item["paragraph_index"]
        prompt = item["prompt"]

        enhanced_prompt = (
            f"35mm documentary photography, {prompt}, "
            "candid photojournalism, natural lighting, sharp focus, 8k resolution, authentic tactile textures"
        )

        try:
            image = pipe(
                prompt=enhanced_prompt,
                negative_prompt=NEGATIVE_PROMPT,
                num_inference_steps=steps,
                guidance_scale=7.5,
                width=width, height=height,
            ).images[0]

            out_path = os.path.join(output_dir, f"generated_p{p_idx}_{abs(hash(prompt)) % 100000}.png")
            image.save(out_path)
            results.append({
                "paragraph_index": p_idx,
                "prompt": prompt,
                "image_path": out_path
            })
            print(f"  -> Generated 35-step image for paragraph {p_idx}")
        except Exception as e:
            print(f"  FAILED generating image for paragraph {p_idx}: {e}")

    return results
