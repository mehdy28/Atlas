import os
import sys
import getpass
import io

def get_or_prompt_api_key(key_path, service_label="API key", info_url=""):
    # 1. If key exists, use it silently (avoids silent hangs in captured pipelines)
    if os.path.exists(key_path):
        with open(key_path) as f:
            saved_key = f.read().strip()
        if saved_key:
            return saved_key

    # 2. Refined capture check: only trigger if stdout is explicitly redirected to a StringIO buffer
    is_captured = (
        isinstance(sys.stdout, io.StringIO)
        or "StringIO" in type(sys.stdout).__name__
    )

    if is_captured:
        raise RuntimeError(
            f"\n[Error] Missing {service_label}!\n"
            f"The pipeline is currently running with captured output, so it cannot prompt you for input.\n"
            f"Please write the key manually to {key_path} or run the discovery script once to set it up."
        )

    # 3. Prompt the user normally in interactive mode
    prompt = "Enter your " + service_label
    if info_url:
        prompt += " (from " + info_url + ")"
    prompt += ": "
    api_key = getpass.getpass(prompt).strip()

    if not api_key or len(api_key) < 6:
        raise ValueError(service_label + " looks empty or too short.")

    # Automatically save it
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    with open(key_path, "w") as f:
        f.write(api_key)
    print("Saved key locally to: " + key_path)

    return api_key
