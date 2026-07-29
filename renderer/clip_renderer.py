
import subprocess
import os


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


def render_clip(video_path, source_start, use_duration, motion, output_path, width, height, fps):
    zoompan = build_zoompan_filter(
        motion["zoom_start"], motion["zoom_end"],
        tuple(motion["pan_start_fraction"]), tuple(motion["pan_end_fraction"]),
        use_duration, fps
    ).format(w=width, h=height)

    vf = "scale=3840:2160," + zoompan + ",format=yuv420p"

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", str(source_start),
        "-t", str(use_duration),
        "-i", video_path,
        "-vf", vf,
        "-an",
        "-r", str(fps),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def freeze_extend_clip(input_path, output_path, extra_seconds, fps):
    """
    Extends a rendered clip by freezing its final frame for extra_seconds.
    Used to close small paragraph-level timing gaps.
    """
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", input_path,
        "-vf", "tpad=stop_mode=clone:stop_duration=" + str(extra_seconds),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-r", str(fps),
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr
