
import os
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


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


def _render_chart(content, chart_type, width, height):
    fig, ax = plt.subplots(figsize=(width / 100.0, height / 100.0), dpi=100)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    title = content.get("title", "")
    unit = content.get("unit", "")

    if chart_type == "bar_chart":
        categories = content.get("categories", [])
        values = content.get("values", [])
        ax.bar(categories, values, color="#d43333")
    else:
        x_labels = content.get("x_labels", [])
        values = content.get("values", [])
        ax.plot(x_labels, values, color="#d43333", marker="o", linewidth=3, markersize=8)

    ax.set_title(title, color="white", fontsize=15, loc="left", pad=14)
    ax.tick_params(colors="white", labelsize=12)
    for spine in ax.spines.values():
        spine.set_color("#666666")
    ax.set_facecolor("none")
    if unit:
        ax.set_ylabel(unit, color="white", fontsize=12)

    buf_path = "/tmp/_chart_tmp.png"
    fig.tight_layout()
    fig.savefig(buf_path, transparent=True)
    plt.close(fig)
    return Image.open(buf_path).convert("RGBA")


def render_side_panel(graphic, width, panel_height, title_font_path, body_font_path,
                       bg_color, accent_color, text_color, subtext_color, accent_width):
    """
    Full video-height vertical panel. Used for text_box, list_reveal,
    comparison, bar_chart, line_chart. Big, bold, clearly a documentary
    graphic rather than a UI toast.
    """
    g_type = graphic["type"]
    content = graphic["content"]

    card = Image.new("RGBA", (width, panel_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    draw.rectangle([0, 0, width - 1, panel_height - 1], fill=bg_color)
    draw.rectangle([0, 0, accent_width, panel_height], fill=accent_color)

    pad_x = accent_width + 50
    content_width = width - pad_x - 50

    if g_type == "text_box":
        heading_font = ImageFont.truetype(title_font_path, 46)
        body_font = ImageFont.truetype(body_font_path, 32)
        heading = str(content.get("heading", "")).upper()
        body = str(content.get("body", ""))

        y = panel_height // 2 - 100
        for line in _wrap_text(draw, heading, heading_font, content_width):
            draw.text((pad_x, y), line, font=heading_font, fill=text_color)
            y += 58
        y += 20
        for line in _wrap_text(draw, body, body_font, content_width):
            draw.text((pad_x, y), line, font=body_font, fill=subtext_color)
            y += 42

    elif g_type == "list_reveal":
        heading_font = ImageFont.truetype(title_font_path, 40)
        item_font = ImageFont.truetype(body_font_path, 30)
        heading = str(content.get("heading", "")).upper()
        items = content.get("items", [])

        total_h = 70 + len(items[:6]) * 60
        y = (panel_height - total_h) // 2
        for line in _wrap_text(draw, heading, heading_font, content_width):
            draw.text((pad_x, y), line, font=heading_font, fill=text_color)
            y += 50
        y += 30
        for item in items[:6]:
            draw.ellipse([pad_x, y + 10, pad_x + 14, y + 24], fill=accent_color)
            for line in _wrap_text(draw, str(item), item_font, content_width - 30)[:1]:
                draw.text((pad_x + 30, y), line, font=item_font, fill=subtext_color)
            y += 58

    elif g_type == "comparison":
        value_font = ImageFont.truetype(title_font_path, 52)
        label_font = ImageFont.truetype(body_font_path, 26)
        left_label = str(content.get("left_label", ""))
        left_value = str(content.get("left_value", ""))
        right_label = str(content.get("right_label", ""))
        right_value = str(content.get("right_value", ""))

        y = panel_height // 2 - 140
        draw.text((pad_x, y), left_value, font=value_font, fill=text_color)
        y += 70
        for line in _wrap_text(draw, left_label, label_font, content_width):
            draw.text((pad_x, y), line, font=label_font, fill=subtext_color)
            y += 34

        y += 50
        draw.line([(pad_x, y), (pad_x + content_width, y)], fill=(90, 90, 90, 255), width=2)
        y += 40

        draw.text((pad_x, y), right_value, font=value_font, fill=text_color)
        y += 70
        for line in _wrap_text(draw, right_label, label_font, content_width):
            draw.text((pad_x, y), line, font=label_font, fill=subtext_color)
            y += 34

    elif g_type in ("bar_chart", "line_chart"):
        heading_font = ImageFont.truetype(title_font_path, 34)
        title_text = str(content.get("title", "")).upper()
        draw.text((pad_x, 40), title_text, font=heading_font, fill=text_color)

        chart_img = _render_chart(content, g_type, content_width, panel_height - 160)
        card.alpha_composite(chart_img, (pad_x, 130))

    return card


def render_full_screen_scrim(graphic, width, height, title_font_path, body_font_path,
                              bg_color, accent_color, text_color, subtext_color):
    """
    Full-frame dark wash with large centered text. Used for stat_callout
    and quote_card - the highest-impact, most dramatic moments.
    """
    g_type = graphic["type"]
    content = graphic["content"]

    card = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    draw.rectangle([0, 0, width, height], fill=bg_color)

    accent_h = 6
    draw.rectangle([0, height // 2 - 140, width, height // 2 - 140 + accent_h], fill=accent_color)

    if g_type == "stat_callout":
        stat_font = ImageFont.truetype(title_font_path, 180)
        label_font = ImageFont.truetype(body_font_path, 42)
        stat_text = str(content.get("stat", ""))
        label_text = str(content.get("label", "")).upper()

        bbox = draw.textbbox((0, 0), stat_text, font=stat_font)
        stat_w = bbox[2] - bbox[0]
        draw.text(((width - stat_w) // 2, height // 2 - 130), stat_text, font=stat_font, fill=text_color)

        label_lines = _wrap_text(draw, label_text, label_font, width - 300)
        y = height // 2 + 90
        for line in label_lines[:2]:
            bbox = draw.textbbox((0, 0), line, font=label_font)
            lw = bbox[2] - bbox[0]
            draw.text(((width - lw) // 2, y), line, font=label_font, fill=subtext_color)
            y += 54

    elif g_type == "quote_card":
        quote_font = ImageFont.truetype(title_font_path, 58)
        attr_font = ImageFont.truetype(body_font_path, 32)
        quote = "\u201c" + str(content.get("quote", "")) + "\u201d"
        attribution = str(content.get("attribution", ""))

        quote_lines = _wrap_text(draw, quote, quote_font, width - 400)
        total_h = len(quote_lines[:5]) * 74
        y = (height - total_h) // 2
        for line in quote_lines[:5]:
            bbox = draw.textbbox((0, 0), line, font=quote_font)
            lw = bbox[2] - bbox[0]
            draw.text(((width - lw) // 2, y), line, font=quote_font, fill=text_color)
            y += 74

        y += 30
        attr_text = "\u2014 " + attribution
        bbox = draw.textbbox((0, 0), attr_text, font=attr_font)
        aw = bbox[2] - bbox[0]
        draw.text(((width - aw) // 2, y), attr_text, font=attr_font, fill=subtext_color)

    return card


def determine_variant(graphic_type):
    if graphic_type in ("stat_callout", "quote_card"):
        return "scrim"
    return "panel"


def generate_card_image(graphic, output_path,
                         title_font_path, body_font_path,
                         panel_width, panel_bg, panel_accent, panel_text, panel_subtext, panel_accent_width,
                         scrim_bg, scrim_text, scrim_subtext, scrim_accent,
                         video_width, video_height, enter_from_left):
    variant = determine_variant(graphic["type"])

    if variant == "panel":
        card = render_side_panel(
            graphic, panel_width, video_height, title_font_path, body_font_path,
            panel_bg, panel_accent, panel_text, panel_subtext, panel_accent_width
        )
        if enter_from_left:
            card = card.transpose(Image.FLIP_LEFT_RIGHT)
        width, height = panel_width, video_height
    else:
        card = render_full_screen_scrim(
            graphic, video_width, video_height, title_font_path, body_font_path,
            scrim_bg, scrim_accent, scrim_text, scrim_subtext
        )
        width, height = video_width, video_height

    card.save(output_path)
    return variant, width, height
