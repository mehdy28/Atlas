
import subprocess
import textwrap
from PIL import Image, ImageDraw, ImageFont


def generate_title_card_image(title_text, output_image_path, width, height, font_path, font_size):
    img = Image.new("RGB", (width, height), color=(12, 12, 14))
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(font_path, font_size)

    wrapped = textwrap.fill(title_text.upper(), width=22)
    lines = wrapped.split("\n")

    line_heights = []
    max_line_width = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        line_heights.append(line_h)
        max_line_width = max(max_line_width, line_w)

    total_text_height = sum(line_heights) + (len(lines) - 1) * 20
    y = (height - total_text_height) // 2

    # Thin horizontal accent line above the title (documentary-style flourish)
    accent_y = y - 50
    accent_width = 160
    draw.line(
        [(width // 2 - accent_width // 2, accent_y), (width // 2 + accent_width // 2, accent_y)],
        fill=(200, 40, 40), width=4
    )

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        x = (width - line_w) // 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += line_heights[i] + 20

    img.save(output_image_path)


def render_title_card_clip(title_text, output_path, width, height, fps, duration_seconds,
                            font_path, font_size):
    still_path = output_path.replace(".mp4", "_still.png")
    generate_title_card_image(title_text, still_path, width, height, font_path, font_size)

    fade_dur = 0.6
    vf = (
        "fade=t=in:st=0:d=" + str(fade_dur) +
        ",fade=t=out:st=" + str(duration_seconds - fade_dur) + ":d=" + str(fade_dur)
    )

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-loop", "1", "-i", still_path,
        "-t", str(duration_seconds),
        "-vf", vf,
        "-r", str(fps),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr
