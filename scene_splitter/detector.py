
from scenedetect import detect, ContentDetector


class SceneSplitter:
    """
    Detects shot boundaries in a video without cutting or saving new files.
    Returns timestamps only -- the original video stays the single source
    of truth, and downstream modules cut on-demand using ffmpeg seek.
    """

    def __init__(self, threshold=27.0, min_scene_len=15):
        self.threshold = threshold
        self.min_scene_len = min_scene_len

    def detect_scenes(self, video_path):
        scene_list = detect(
            video_path,
            ContentDetector(threshold=self.threshold, min_scene_len=self.min_scene_len)
        )

        scenes = []
        for start, end in scene_list:
            scenes.append({
                "start_seconds": start.get_seconds(),
                "end_seconds": end.get_seconds(),
            })
        return scenes
