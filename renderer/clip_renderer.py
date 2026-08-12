
import subprocess
import os


def _video_codec_args(use_nvenc):
    if use_nvenc:
        return ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "20"]
    return ["-c:v", "libx264", "-preset", "fast", "-crf", "20"]


def build_zoompan_filter(zoom_start, zoom_end, pan_start, pan_end, duration_seconds, fps):
    total_frames = max(2, int(round(duration_seconds * fps)))
    dz = zoom_end - zoom_start
    dx = pan_end[0] - pan_start[0]
    dy = pan_end[1] - pan_start[1]
    denom = total_frames - 1

    zoom_expr = str(zoom_start) + "+" + str(dz) + "*on/" + str(denom)
    pan_x_expr = "(iw-iw/zoom)/2+(" + str(pan_start[0]) + "+(" + str(dx) + ")*on/" + str(denom) + ")*iw"
    pan_y_expr = "(ih-ih/zoom)/2+(" + str(pan_start[1]) + "+(" + str(dy) + ")*on/" + str(denom) + ")*ih"

    return "zoompan=z=\'" + zoom_expr + "\':x=\'" + pan_x_expr + "\':y=\'" + pan_y_expr + "\':d=1:s={w}x{h}:fps=" + str(fps)


def build_grade_filter(contrast, saturation, brightness, vignette_strength):
    eq = "eq=contrast=" + str(contrast) + ":saturation=" + str(saturation) + ":brightness=" + str(brightness)
    vignette = "vignette=PI/" + str(round(4 / max(vignette_strength, 0.01), 3))
    return eq + "," + vignette


def render_clip(video_path, source_start, use_duration, motion, output_path, width, height, fps,
                 grade_contrast, grade_saturation, grade_brightness, grade_vignette, use_nvenc=True):
    zoompan = build_zoompan_filter(
        motion["zoom_start"], motion["zoom_end"],
        tuple(motion["pan_start_fraction"]), tuple(motion["pan_end_fraction"]),
        use_duration, fps
    ).format(w=width, h=height)

    grade = build_grade_filter(grade_contrast, grade_saturation, grade_brightness, grade_vignette)
    vf = "scale=3840:2160," + zoompan + "," + grade + ",format=yuv420p"

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-ss", str(source_start), "-t", str(use_duration), "-i", video_path,
           "-vf", vf, "-an", "-r", str(fps)] + _video_codec_args(use_nvenc) + [output_path]

    encoder_used = "nvenc" if use_nvenc else "libx264"
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and use_nvenc:
        print("NVENC failed for this clip, falling back to software encode. Error: " + result.stderr[-200:])
        cmd_fallback = ["ffmpeg", "-y", "-loglevel", "error",
                         "-ss", str(source_start), "-t", str(use_duration), "-i", video_path,
                         "-vf", vf, "-an", "-r", str(fps)] + _video_codec_args(False) + [output_path]
        result = subprocess.run(cmd_fallback, capture_output=True, text=True)
        encoder_used = "libx264 (fallback)"

    return result.returncode == 0, result.stderr, encoder_used


def freeze_extend_clip(input_path, output_path, extra_seconds, fps, use_nvenc=True):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", input_path,
           "-vf", "tpad=stop_mode=clone:stop_duration=" + str(extra_seconds),
           "-r", str(fps)] + _video_codec_args(use_nvenc) + [output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and use_nvenc:
        cmd_fallback = ["ffmpeg", "-y", "-loglevel", "error", "-i", input_path,
                         "-vf", "tpad=stop_mode=clone:stop_duration=" + str(extra_seconds),
                         "-r", str(fps)] + _video_codec_args(False) + [output_path]
        result = subprocess.run(cmd_fallback, capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def render_image_clip(image_path, use_duration, motion, output_path, width, height, fps,
                       grade_contrast, grade_saturation, grade_brightness, grade_vignette, use_nvenc=True):
    """
    Applies the same Ken Burns zoom/pan treatment as video clips, but to
    a single still image held for use_duration.
    """
    zoompan = build_zoompan_filter(
        motion["zoom_start"], motion["zoom_end"],
        tuple(motion["pan_start_fraction"]), tuple(motion["pan_end_fraction"]),
        use_duration, fps
    ).format(w=width, h=height)

    grade = build_grade_filter(grade_contrast, grade_saturation, grade_brightness, grade_vignette)
    vf = "scale=3840:2160," + zoompan + "," + grade + ",format=yuv420p"

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-loop", "1", "-t", str(use_duration), "-i", image_path,
           "-vf", vf, "-an", "-r", str(fps)] + _video_codec_args(use_nvenc) + [output_path]

    result = subprocess.run(cmd, capture_output=True, text=True)
    encoder_used = "nvenc" if use_nvenc else "libx264"
    if result.returncode != 0 and use_nvenc:
        cmd_fallback = ["ffmpeg", "-y", "-loglevel", "error",
                         "-loop", "1", "-t", str(use_duration), "-i", image_path,
                         "-vf", vf, "-an", "-r", str(fps)] + _video_codec_args(False) + [output_path]
        result = subprocess.run(cmd_fallback, capture_output=True, text=True)
        encoder_used = "libx264 (fallback)"

    return result.returncode == 0, result.stderr, encoder_used
