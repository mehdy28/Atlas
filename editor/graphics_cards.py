
import os
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CARD_SIZES = {
    "stat_callout": (480, 200),
    "text_box": (560, 220),
    "comparison": (620, 220),
    "list_reveal": (560, 320),
    "quote_card": (600, 220),
    "bar_chart": (640, 380),
    "line_chart": (640, 380),
}


def _base_card(width, height, bg_color, accent_color, accent_width, corner_radius):
    card = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle([0, 0, width - 1, height - 1], radius=corner_radius, fill=bg_color)
    draw.rectangle([0, 0, accent_width, height], fill=accent_color)
    return card, draw


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def render_stat_callout(content, width, height, title_font_path, body_font_path,
                         bg_color, accent_color, text_color, subtext_color, accent_width, corner_radius):
    card, draw = _base_card(width, height, bg_color, accent_color, accent_width, corner_radius)
    pad_x = accent_width + 30

    stat_font = ImageFont.truetype(title_font_path, 64)
    label_font = ImageFont.truetype(body_font_path, 26)

    stat_text = str(content.get("stat", ""))
    label_text = str(content.get("label", ""))

    draw.text((pad_x, 30), stat_text, font=stat_font, fill=text_color)

    label_lines = _wrap_text(draw, label_text, label_font, width - pad_x - 20)
    y = 110
    for line in label_lines[:3]:
        draw.text((pad_x, y), line, font=label_font, fill=subtext_color)
        y += 34

    return card


def render_text_box(content, width, height, title_font_path, body_font_path,
                     bg_color, accent_color, text_color, subtext_color, accent_width, corner_radius):
    card, draw = _base_card(width, height, bg_color, accent_color, accent_width, corner_radius)
    pad_x = accent_width + 30

    heading_font = ImageFont.truetype(title_font_path, 34)
    body_font = ImageFont.truetype(body_font_path, 24)

    heading = str(content.get("heading", ""))
    body = str(content.get("body", ""))

    draw.text((pad_x, 30), heading.upper(), font=heading_font, fill=text_color)

    body_lines = _wrap_text(draw, body, body_font, width - pad_x - 20)
    y = 95
    for line in body_lines[:4]:
        draw.text((pad_x, y), line, font=body_font, fill=subtext_color)
        y += 32

    return card


def render_comparison(content, width, height, title_font_path, body_font_path,
                       bg_color, accent_color, text_color, subtext_color, accent_width, corner_radius):
    card, draw = _base_card(width, height, bg_color, accent_color, accent_width, corner_radius)
    pad_x = accent_width + 30

    value_font = ImageFont.truetype(title_font_path, 46)
    label_font = ImageFont.truetype(body_font_path, 22)

    left_label = str(content.get("left_label", ""))
    left_value = str(content.get("left_value", ""))
    right_label = str(content.get("right_label", ""))
    right_value = str(content.get("right_value", ""))

    half_width = (width - pad_x - 20) // 2

    draw.text((pad_x, 30), left_value, font=value_font, fill=text_color)
    for i, line in enumerate(_wrap_text(draw, left_label, label_font, half_width)[:2]):
        draw.text((pad_x, 100 + i * 28), line, font=label_font, fill=subtext_color)

    right_x = pad_x + half_width + 20
    draw.text((right_x, 30), right_value, font=value_font, fill=text_color)
    for i, line in enumerate(_wrap_text(draw, right_label, label_font, half_width)[:2]):
        draw.text((right_x, 100 + i * 28), line, font=label_font, fill=subtext_color)

    draw.line([(pad_x + half_width + 10, 20), (pad_x + half_width + 10, height - 20)],
              fill=(80, 80, 80, 255), width=2)

    return card


def render_list_reveal(content, width, height, title_font_path, body_font_path,
                        bg_color, accent_color, text_color, subtext_color, accent_width, corner_radius):
    card, draw = _base_card(width, height, bg_color, accent_color, accent_width, corner_radius)
    pad_x = accent_width + 30

    heading_font = ImageFont.truetype(title_font_path, 30)
    item_font = ImageFont.truetype(body_font_path, 24)

    heading = str(content.get("heading", ""))
    items = content.get("items", [])

    draw.text((pad_x, 25), heading.upper(), font=heading_font, fill=text_color)

    y = 85
    for item in items[:5]:
        draw.ellipse([pad_x, y + 8, pad_x + 8, y + 16], fill=accent_color)
        draw.text((pad_x + 20, y), str(item), font=item_font, fill=subtext_color)
        y += 40

    return card


def render_quote_card(content, width, height, title_font_path, body_font_path,
                       bg_color, accent_color, text_color, subtext_color, accent_width, corner_radius):
    card, draw = _base_card(width, height, bg_color, accent_color, accent_width, corner_radius)
    pad_x = accent_width + 30

    quote_font = ImageFont.truetype(body_font_path, 28)
    attr_font = ImageFont.truetype(body_font_path, 20)

    quote = "\u201c" + str(content.get("quote", "")) + "\u201d"
    attribution = str(content.get("attribution", ""))

    quote_lines = _wrap_text(draw, quote, quote_font, width - pad_x - 20)
    y = 30
    for line in quote_lines[:4]:
        draw.text((pad_x, y), line, font=quote_font, fill=text_color)
        y += 34

    draw.text((pad_x, height - 40), "- " + attribution, font=attr_font, fill=subtext_color)

    return card


def _render_chart_overlay(content, chart_type, width, height):
    fig, ax = plt.subplots(figsize=(width / 100.0, (height - 60) / 100.0), dpi=100)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    title = content.get("title", "")
    unit = content.get("unit", "")

    if chart_type == "bar_chart":
        categories = content.get("categories", [])
        values = content.get("values", [])
        ax.bar(categories, values, color="#c82828")
    else:
        x_labels = content.get("x_labels", [])
        values = content.get("values", [])
        ax.plot(x_labels, values, color="#c82828", marker="o", linewidth=2)

    ax.set_title(title, color="white", fontsize=11, loc="left")
    ax.tick_params(colors="white", labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#555555")
    ax.set_facecolor("none")

    if unit:
        ax.set_ylabel(unit, color="white", fontsize=9)

    buf_path = "/tmp/_chart_tmp.png"
    fig.tight_layout()
    fig.savefig(buf_path, transparent=True)
    plt.close(fig)

    return Image.open(buf_path).convert("RGBA")


def render_bar_or_line_chart(content, chart_type, width, height, title_font_path, body_font_path,
                              bg_color, accent_color, text_color, subtext_color, accent_width, corner_radius):
    card, draw = _base_card(width, height, bg_color, accent_color, accent_width, corner_radius)
    chart_img = _render_chart_overlay(content, chart_type, width - accent_width - 20, height - 20)

    paste_x = accent_width + 15
    paste_y = 10
    card.alpha_composite(chart_img, (paste_x, paste_y))
    return card


def generate_card_image(graphic, output_path, title_font_path, body_font_path,
                         bg_color, accent_color, text_color, subtext_color,
                         accent_width, corner_radius):
    g_type = graphic["type"]
    content = graphic["content"]
    width, height = CARD_SIZES[g_type]

    if g_type == "stat_callout":
        card = render_stat_callout(content, width, height, title_font_path, body_font_path,
                                    bg_color, accent_color, text_color, subtext_color, accent_width, corner_radius)
    elif g_type == "text_box":
        card = render_text_box(content, width, height, title_font_path, body_font_path,
                                bg_color, accent_color, text_color, subtext_color, accent_width, corner_radius)
    elif g_type == "comparison":
        card = render_comparison(content, width, height, title_font_path, body_font_path,
                                  bg_color, accent_color, text_color, subtext_color, accent_width, corner_radius)
    elif g_type == "list_reveal":
        card = render_list_reveal(content, width, height, title_font_path, body_font_path,
                                   bg_color, accent_color, text_color, subtext_color, accent_width, corner_radius)
    elif g_type == "quote_card":
        card = render_quote_card(content, width, height, title_font_path, body_font_path,
                                  bg_color, accent_color, text_color, subtext_color, accent_width, corner_radius)
    elif g_type in ("bar_chart", "line_chart"):
        card = render_bar_or_line_chart(content, g_type, width, height, title_font_path, body_font_path,
                                         bg_color, accent_color, text_color, subtext_color, accent_width, corner_radius)
    else:
        raise ValueError("Unknown graphic type: " + g_type)

    card.save(output_path)
    return width, height
