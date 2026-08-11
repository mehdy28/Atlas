
import os
import subprocess
import numpy as np
import imageio.v3 as iio


def export_alpha_clip(composition, output_path: str, fps: float = 30.0) -> bool:
    """
    Tries Movis's native write_video with an alpha-preserving codec first.
    If that fails (unsupported pixelformat/codec combo on this build),
    falls back to manually sampling frames via composition(t) - which is
    confirmed to return RGBA arrays - and encoding them ourselves with
    the same qtrle approach already proven in the PIL pipeline.
    """
    try:
        composition.write_video(output_path, codec="qtrle", pixelformat="rgba", fps=fps)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            return True
    except Exception as e:
        print("Native alpha write_video failed (" + str(e) + "), falling back to frame sampling.")

    frame_dir = output_path + "_frames"
    os.makedirs(frame_dir, exist_ok=True)
    duration = composition.duration
    frame_count = max(2, int(round(duration * fps)))

    for i in range(frame_count):
        t = (i / frame_count) * duration
        frame = composition(t)
        if frame is None:
            frame = np.zeros((composition.size[1], composition.size[0], 4), dtype=np.uint8)
        iio.imwrite(os.path.join(frame_dir, "f_" + str(i).zfill(4) + ".png"), frame)

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(fps),
        "-i", os.path.join(frame_dir, "f_%04d.png"),
        "-c:v", "qtrle",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
