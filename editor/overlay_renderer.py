
import subprocess
import os


def render_alpha_clip(png_path, output_mov_path, display_duration, fade_duration, fps):
    """
    Turns a static RGBA PNG into a short alpha-channel video clip with
    fade in/out on both color and alpha, using the qtrle codec (reliable
    alpha support in .mov containers).
    """
    fade_out_start = max(0, display_duration - fade_duration)

    vf = (
        "format=rgba,"
        "fade=t=in:st=0:d=" + str(fade_duration) + ":alpha=1,"
        "fade=t=out:st=" + str(fade_out_start) + ":d=" + str(fade_duration) + ":alpha=1"
    )

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-loop", "1", "-i", png_path,
        "-t", str(display_duration),
        "-vf", vf,
        "-r", str(fps),
        "-c:v", "qtrle",
        output_mov_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def overlay_clip_onto_video(base_video_path, overlay_mov_path, start_seconds, display_duration,
                             pos_x, pos_y, output_path):
    """
    Overlays one alpha clip onto the base video at start_seconds, holding
    for display_duration, then re-encodes. Called once per graphic in a
    sequential chain (each call\'s output becomes the next call\'s input).
    """
    end_seconds = start_seconds + display_duration

    filter_complex = (
        "[1:v]setpts=PTS+" + str(start_seconds) + "/TB[gfx];"
        "[0:v][gfx]overlay=x=" + str(pos_x) + ":y=" + str(pos_y) +
        ":enable='between(t," + str(start_seconds) + "," + str(end_seconds) + ")'[outv]"
    )

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", base_video_path,
        "-i", overlay_mov_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr
