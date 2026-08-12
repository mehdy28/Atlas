
import subprocess
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def ensure_fonts_registered():
    """
    Movis looks up fonts by OS-level family name via fontconfig, not by
    file path. This copies our custom fonts into the system font
    directory and refreshes the font cache so Movis can find them by
    name. Idempotent - safe to call every run.
    """
    target_dir = "/usr/share/fonts/truetype/atlas_custom"
    os.makedirs(target_dir, exist_ok=True)

    source_fonts = [
        "/content/Atlas/assets/fonts/Anton-Regular.ttf",
    ]
    for src in source_fonts:
        if os.path.exists(src):
            dst = os.path.join(target_dir, os.path.basename(src))
            if not os.path.exists(dst):
                subprocess.run(["cp", src, dst], capture_output=True)

    subprocess.run(["fc-cache", "-f"], capture_output=True)


def hex_from_rgba(rgba_tuple):
    r, g, b = rgba_tuple[0], rgba_tuple[1], rgba_tuple[2]
    return "#{:02X}{:02X}{:02X}".format(r, g, b)
