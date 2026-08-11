
from PIL import ImageFont, ImageDraw, Image
from typing import Tuple, List


CONTENT_TYPE_RATIOS = {
    "stat_callout": (0.35, 0.40),
    "text_box": (0.60, 0.30),
    "bar_chart": (0.55, 0.55),
    "line_chart": (0.60, 0.55),
    "comparison": (0.45, 0.45),
    "quote_card": (0.65, 0.35),
    "list_reveal": (0.50, 0.50),
}


def calculate_container_size(content_type: str, video_width: int, video_height: int,
                              char_count: int = 0, item_count: int = 0) -> Tuple[int, int]:
    if content_type not in CONTENT_TYPE_RATIOS:
        content_type = "text_box"

    w_ratio, h_ratio = CONTENT_TYPE_RATIOS[content_type]

    if content_type == "bar_chart" and item_count > 4:
        w_ratio = min(0.85, w_ratio + 0.05 * (item_count - 4))

    if content_type == "list_reveal" and item_count > 4:
        h_ratio = min(0.75, h_ratio + 0.05 * (item_count - 4))

    if char_count > 120:
        h_ratio = min(0.8, h_ratio + 0.1)

    width = int(video_width * w_ratio)
    height = int(video_height * h_ratio)
    return max(width, 200), max(height, 120)


def fit_text_to_container(text: str, font_path: str, max_width: int, max_height: int,
                           start_size: int = 90, min_size: int = 18,
                           padding: int = 20, line_spacing: float = 1.25) -> Tuple[int, List[str], int]:
    """
    Measures with Pillow (font_path = actual .ttf file, for measurement only)
    to guarantee fit. The resulting font_size is then used with Movis's
    Text layer via font_family (registered font name), not this file path.
    """
    if not text or not text.strip():
        raise ValueError("fit_text_to_container received empty text.")

    usable_w = max(10, max_width - padding * 2)
    usable_h = max(10, max_height - padding * 2)

    measure_img = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(measure_img)

    size = start_size
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        words = text.split()
        lines, current = [], ""
        for word in words:
            candidate = (current + " " + word).strip()
            bbox = draw.textbbox((0, 0), candidate, font=font)
            if bbox[2] - bbox[0] <= usable_w or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)

        line_height = int(size * line_spacing)
        total_height = line_height * len(lines)
        max_line_width = max(draw.textbbox((0, 0), l, font=font)[2] for l in lines)

        if total_height <= usable_h and max_line_width <= usable_w:
            return size, lines, line_height

        size -= 2

    font = ImageFont.truetype(font_path, min_size)
    return min_size, [text], int(min_size * line_spacing)
