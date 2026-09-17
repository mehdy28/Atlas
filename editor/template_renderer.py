import sys
import subprocess
import os
import threading
from playwright.sync_api import sync_playwright

TEMPLATES_ROOT = "/content/Atlas/motion_templates"
if TEMPLATES_ROOT + "/engine" not in sys.path:
    sys.path.append(TEMPLATES_ROOT + "/engine")
from motion_engine import wrap_frame

class MotionTemplateRenderer:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height

    def start(self):
        pass  # Kept for interface compatibility

    def render_sequence_to_mov(self, sequence, output_mov_path, fps=30, transparent=True):
        """
        Renders Sequence HTML frames via Playwright in an isolated thread
        (completely immune to Jupyter/asyncio loop conflicts) and direct-pipes to FFmpeg (qtrle).
        """
        err_box = []

        def _worker():
            try:
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(headless=True)
                    page = browser.new_page(viewport={"width": self.width, "height": self.height})
                    total_frames = max(2, int(round(sequence.duration * fps)))

                    ffmpeg_cmd = [
                        "ffmpeg", "-y", "-loglevel", "error",
                        "-f", "image2pipe",
                        "-vcodec", "png",
                        "-r", str(fps),
                        "-i", "-",
                        "-c:v", "qtrle",
                        output_mov_path
                    ]
                    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

                    try:
                        for f in range(total_frames):
                            t = (f / float(fps))
                            html = wrap_frame(sequence.html_at(t), transparent=transparent)
                            page.set_content(html, wait_until="load")
                            png_bytes = page.screenshot(type="png", omit_background=transparent)
                            proc.stdin.write(png_bytes)
                    finally:
                        proc.stdin.close()
                        proc.wait()

                    browser.close()
            except Exception as e:
                err_box.append(e)

        # Run worker thread so it has its own clean thread context
        thread = threading.Thread(target=_worker)
        thread.start()
        thread.join()

        if err_box:
            raise err_box[0]

        return os.path.exists(output_mov_path) and os.path.getsize(output_mov_path) > 1000

    def close(self):
        pass
