
import os
import sys
import subprocess
from contextlib import contextmanager
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector


@contextmanager
def _suppress_native_stderr():
    """
    swscaler/ffmpeg write warnings directly to the C-level stderr file
    descriptor, bypassing Python\'s logging/warnings system entirely.
    This temporarily redirects fd 2 to /dev/null so those warnings do
    not flood the notebook output, then restores it afterward.
    """
    stderr_fd = sys.stderr.fileno()
    saved_fd = os.dup(stderr_fd)
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull, stderr_fd)
        yield
    finally:
        os.dup2(saved_fd, stderr_fd)
        os.close(devnull)
        os.close(saved_fd)


def detect_scenes(video_path, threshold=27.0, min_scene_len_seconds=1.0):
    """
    Returns a list of (start_seconds, end_seconds) tuples.
    Falls back to treating the whole video as one scene if no
    cuts are detected (common for static or single-shot clips).
    """
    with _suppress_native_stderr():
        video = open_video(video_path)
        fps = video.frame_rate
        duration_seconds = video.duration.get_seconds()

        min_scene_len_frames = max(1, int(min_scene_len_seconds * fps))

        scene_manager = SceneManager()
        scene_manager.add_detector(
            ContentDetector(threshold=threshold, min_scene_len=min_scene_len_frames)
        )
        scene_manager.detect_scenes(video=video)
        scene_list = scene_manager.get_scene_list()

    if not scene_list:
        return [(0.0, duration_seconds)]

    return [(s.get_seconds(), e.get_seconds()) for s, e in scene_list]


def extract_thumbnail(video_path, timestamp_seconds, output_path):
    """
    Grabs a single frame at the given timestamp using ffmpeg.
    Returns True on success.
    """
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", str(timestamp_seconds),
        "-i", video_path,
        "-frames:v", "1",
        "-q:v", "3",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0
