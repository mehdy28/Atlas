
import subprocess


def render_all_graphics_single_pass(base_video_path, graphics, output_path, fps, use_nvenc=True):
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

    codec_args = ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "19"] if use_nvenc else ["-c:v", "libx264", "-preset", "medium", "-crf", "19"]

    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[" + prev_tag + "]",
    ] + codec_args + [output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0 and use_nvenc:
        print("NVENC compositing failed, falling back to software encode.")
        cmd_fallback = ["ffmpeg", "-y", "-loglevel", "error"] + inputs + [
            "-filter_complex", filter_complex,
            "-map", "[" + prev_tag + "]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            output_path,
        ]
        result = subprocess.run(cmd_fallback, capture_output=True, text=True)

    return result.returncode == 0, result.stderr
