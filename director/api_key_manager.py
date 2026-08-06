
import os
import getpass


def get_or_prompt_api_key(key_path):
    """
    Loads a saved API key from Drive if present. Otherwise prompts for
    it (hidden input), asks explicit consent before saving, and stores
    it plaintext at key_path if the person agrees.

    Note: this is a convenience store, not a secrets vault - anyone with
    access to this Drive folder could read the file. Fine for a personal
    project; revoke/regenerate the key at aistudio.google.com if needed.
    """
    if os.path.exists(key_path):
        with open(key_path) as f:
            saved_key = f.read().strip()
        if saved_key:
            masked = saved_key[:4] + "..." + saved_key[-4:] if len(saved_key) > 8 else "****"
            use_saved = input("Found a saved Gemini API key (" + masked + "). Use it? [Y/n]: ").strip().lower()
            if use_saved in ("", "y", "yes"):
                return saved_key

    api_key = getpass.getpass("Enter your Gemini API key (hidden input, from aistudio.google.com/apikey): ").strip()

    if not api_key or len(api_key) < 10:
        raise ValueError("API key looks empty or too short - paste failed, try again.")

    consent = input(
        "Save this key to Drive (plaintext, at " + key_path + ") so you don't "
        "have to re-enter it next time? This is convenience storage, not encrypted. [y/N]: "
    ).strip().lower()

    if consent in ("y", "yes"):
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        with open(key_path, "w") as f:
            f.write(api_key)
        print("Key saved to " + key_path)
    else:
        print("Key not saved - you will be asked again next run.")

    return api_key
