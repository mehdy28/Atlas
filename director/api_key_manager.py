
import os
import getpass


def get_or_prompt_api_key(key_path, service_label="API key", info_url=""):
    if os.path.exists(key_path):
        with open(key_path) as f:
            saved_key = f.read().strip()
        if saved_key:
            masked = saved_key[:4] + "..." + saved_key[-4:] if len(saved_key) > 8 else "****"
            use_saved = input("Found a saved " + service_label + " (" + masked + "). Use it? [Y/n]: ").strip().lower()
            if use_saved in ("", "y", "yes"):
                return saved_key

    prompt = "Enter your " + service_label
    if info_url:
        prompt += " (from " + info_url + ")"
    prompt += ": "
    api_key = getpass.getpass(prompt).strip()

    if not api_key or len(api_key) < 6:
        raise ValueError(service_label + " looks empty or too short.")

    consent = input("Save this key to Drive at " + key_path + " for reuse next time? [y/N]: ").strip().lower()
    if consent in ("y", "yes"):
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        with open(key_path, "w") as f:
            f.write(api_key)
        print("Key saved.")
    else:
        print("Key not saved - you will be asked again next run.")

    return api_key
