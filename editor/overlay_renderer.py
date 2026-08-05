
import os
import subprocess
from PIL import Image


def render_graphic_alpha_clip(style_fn, content, graphic_meta, out_mov_path, width, height, fps, duration, fonts, palette):
    """
    Renders the full animated sequence for one graphic (using its own
    internal easing/timing over `duration`) as a transparent-background
    alpha video clip. All 20 styles already draw self-contained,
    full-canvas-sized frames, so no separate positioning step is needed.
    """
    frame_count = max(2, int(round(duration * fps)))
    tmp_dir = out_mov_path + "_frames"
    os.makedirs(tmp_dir, exist_ok=True)

    for i in range(frame_count):
        t = i / frame_count
        frame = style_fn(t, content, width, height, fonts, palette)
        frame.save(os.path.join(tmp_dir, "f_" + str(i).zfill(4) + ".png"))

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(fps),
        "-i", os.path.join(tmp_dir, "f_%04d.png"),
        "-c:v", "qtrle",
        out_mov_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def render_all_graphics_single_pass(base_video_path, graphics, output_path, fps):
    """
    graphics: list of dicts with keys: mov_path, start_seconds, duration_seconds
    All clips are full video-frame size, positioned at (0,0), so the
    only thing ffmpeg needs to do per graphic is time-shift and overlay
    with enable=between - no per-style positioning logic needed here.
    """
    inputs = ["-i", base_video_path]
    filter_parts = []
    prev_tag = "0:v"

    for idx, g in enumerate(graphics, start=1):
        inputs += ["-i", g["mov_path"]]
        gfx_tag = "gfx" + str(idx)
        out_tag = "v" + str(idx)
        start = g["start_seconds"]
        end = start + g["duration_seconds"]

        prep = "[" + str(idx) + ":v]setpts=PTS-STARTPTS+" + str(start) + "/TB[" + gfx_tag + "]"
        overlay = (
            "[" + prev_tag + "][" + gfx_tag + "]overlay=x=0:y=0:"
            "enable='between(t," + str(start) + "," + str(end) + ")'[" + out_tag + "]"
        )
        filter_parts.append(prep)
        filter_parts.append(overlay)
        prev_tag = out_tag

    filter_complex = ";".join(filter_parts)

    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[" + prev_tag + "]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr
