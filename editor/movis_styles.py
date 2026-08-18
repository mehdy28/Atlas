
import re
import math
import hashlib
from typing import Dict, Any, List, Tuple
import movis as mv
from sizing.container_sizing import calculate_container_size, fit_text_to_container, inscribed_square_side
from editor.movis_animations import apply_fade_in, apply_fade_out, apply_scale_pop, apply_slide_in


# ============== SHARED LAYOUT ENGINE ==============
# Every text-heavy style uses this: measure all blocks first, size the
# container to fit exactly what was measured, then position top-down.
# This is the single source of truth for vertical layout, replacing the
# per-style ad-hoc math that kept producing inconsistent overflow bugs.

def measure_block(text, font_path, max_width, max_height, start_size, min_size=16):
    size, lines, line_h = fit_text_to_container(text, font_path, max_width, max_height, start_size=start_size, min_size=min_size, padding=0)
    return {"lines": lines, "font_size": size, "line_h": line_h, "block_h": line_h * len(lines)}


def stack_blocks(blocks: List[dict], pad_top_bottom: int, gap: int, max_total_height: int):
    """
    Given pre-measured blocks (each with 'block_h'), returns:
    (total_content_height, list of top_y_offsets relative to content top)
    Caps total height at max_total_height - if exceeded, this indicates
    the content genuinely does not fit even at minimum font size, which
    should be rare given fit_text_to_container already shrinks text.
    """
    offsets = []
    cursor = 0
    for b in blocks:
        offsets.append(cursor)
        cursor += b["block_h"] + gap
    total = cursor - gap if blocks else 0
    total_with_padding = total + pad_top_bottom * 2
    return min(total_with_padding, max(max_total_height, total_with_padding)), offsets


def add_text_layer(scene, block, x_center, y_top, color, font_family, fade_start=0.15, fade_dur=0.3, add_shadow=True):
    layer = scene.add_layer(
        mv.layer.Text("\n".join(block["lines"]), font_size=block["font_size"], font_family=font_family, color=color),
        position=(x_center, y_top + block["block_h"] // 2),
    )
    if add_shadow:
        layer.add_effect(mv.effect.DropShadow(offset=3.0, color="#000000", opacity=0.5, radius=4.0))
    apply_fade_in(layer, fade_start, fade_dur)
    return layer


def rounded_panel(scene, w, h, x, y, fill_hex, border_hex=None, radius=22):
    panel = scene.add_layer(
        mv.layer.Rectangle(size=(w, h), color=fill_hex, radius=radius, contents=(
            [mv.attribute.StrokeProperty(color=border_hex, width=2)] if border_hex else []
        )),
        position=(x, y),
    )
    return panel


def _validate_content(content: Dict[str, Any], required_keys: list) -> None:
    missing = [k for k in required_keys if k not in content or not str(content[k]).strip()]
    if missing:
        raise ValueError("Missing required content keys: " + str(missing))


def extract_percent(text):
    m = re.search(r"(\d+(\.\d+)?)\s*%", str(text))
    return float(m.group(1)) if m else None


def pick_variant(candidates, seed_key):
    h = int(hashlib.md5(str(seed_key).encode()).hexdigest(), 16)
    return candidates[h % len(candidates)]


# ============== STYLE RENDERERS ==============

def render_text_box(content, duration, palette, video_width, video_height, font_path, font_family):
    _validate_content(content, ["heading"])
    heading = str(content["heading"]).upper()
    body = str(content.get("body", ""))

    panel_w, _ = calculate_container_size("text_box", video_width, video_height, char_count=len(body))
    PAD, GAP = 44, 22
    max_h = int(video_height * 0.85)

    blocks = [measure_block(heading, font_path, panel_w - PAD * 2, max_h * 0.5, start_size=46)]
    if body:
        blocks.append(measure_block(body, font_path, panel_w - PAD * 2, max_h * 0.5, start_size=27))

    panel_h, offsets = stack_blocks(blocks, PAD, GAP, max_h)

    scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)
    py = video_height - panel_h // 2 - 40
    panel = rounded_panel(scene, panel_w, panel_h, panel_w // 2, py, palette["navy_hex"], border_hex=palette["orange_hex"])
    apply_slide_in(panel, 0.0, 0.4, (-panel_w, py), (panel_w // 2, py))

    content_top = py - panel_h // 2 + PAD
    colors = [palette["white_hex"], palette["offwhite_hex"]]
    for i, block in enumerate(blocks):
        add_text_layer(scene, block, panel_w // 2, content_top + offsets[i], colors[i], font_family, fade_start=0.15 + i * 0.1)

    return scene


def render_stat_callout(content, duration, palette, video_width, video_height, font_path, font_family):
    _validate_content(content, ["stat"])
    stat = str(content["stat"])
    label = str(content.get("label", ""))

    # Design decision: circles only work for short, predictable content.
    # Longer stats/labels automatically use a rounded badge instead.
    use_circle = len(stat) <= 6 and len(label) <= 30

    if use_circle:
        box_w_raw, box_h_raw = calculate_container_size("stat_callout", video_width, video_height, char_count=len(label))
        box_size = max(box_w_raw, box_h_raw)
        safe_side = int(inscribed_square_side(box_size))
        PAD = 20
        usable_w = safe_side - PAD * 2
        max_h = int(usable_w * 0.9)

        stat_block = measure_block(stat, font_path, usable_w, max_h * 0.6, start_size=130)
        blocks = [stat_block]
        if label:
            blocks.append(measure_block(label, font_path, usable_w, max_h * 0.4, start_size=26))

        _, offsets = stack_blocks(blocks, 0, 14, max_h)
        total_h = sum(b["block_h"] for b in blocks) + 14 * (len(blocks) - 1)

        scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)
        cx, cy = video_width // 2, video_height // 2
        circle = scene.add_layer(
            mv.layer.Rectangle(size=(box_size, box_size), color=palette["navy_hex"], radius=box_size // 2,
                                contents=[mv.attribute.StrokeProperty(color=palette["orange_hex"], width=3)]),
            position=(cx, cy),
        )
        apply_scale_pop(circle, 0.0, 0.45, from_scale=0.0, to_scale=1.0)

        content_top = cy - total_h // 2
        colors = [palette["white_hex"], palette["orange_hex"]]
        for i, block in enumerate(blocks):
            add_text_layer(scene, block, cx, content_top + offsets[i], colors[i], font_family, fade_start=0.3 + i * 0.15)

        return scene

    # Rounded badge fallback for longer content
    panel_w, panel_h_raw = calculate_container_size("stat_callout", video_width, video_height, char_count=len(label))
    panel_w = max(panel_w, 560)
    PAD, GAP = 40, 16
    max_h = int(video_height * 0.5)

    stat_block = measure_block(stat, font_path, panel_w - PAD * 2, max_h * 0.55, start_size=90)
    blocks = [stat_block]
    if label:
        blocks.append(measure_block(label, font_path, panel_w - PAD * 2, max_h * 0.45, start_size=26))

    panel_h, offsets = stack_blocks(blocks, PAD, GAP, max_h)

    scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)
    cx, cy = video_width // 2, video_height // 2
    panel = rounded_panel(scene, panel_w, panel_h, cx, cy, palette["navy_hex"], border_hex=palette["orange_hex"], radius=28)
    apply_scale_pop(panel, 0.0, 0.4, from_scale=0.9, to_scale=1.0)

    content_top = cy - panel_h // 2 + PAD
    colors = [palette["white_hex"], palette["orange_hex"]]
    for i, block in enumerate(blocks):
        add_text_layer(scene, block, cx, content_top + offsets[i], colors[i], font_family, fade_start=0.3 + i * 0.15)

    return scene


def render_comparison(content, duration, palette, video_width, video_height, font_path, font_family):
    _validate_content(content, ["left_label", "left_value", "right_label", "right_value"])

    panel_w, _ = calculate_container_size("comparison", video_width, video_height)
    PAD, DIVIDER_GAP, GAP = 50, 40, 18
    half_w = (panel_w - PAD * 2 - DIVIDER_GAP) // 2
    max_h = int(video_height * 0.6)

    left_val = measure_block(str(content["left_value"]), font_path, half_w, max_h * 0.5, start_size=50)
    right_val = measure_block(str(content["right_value"]), font_path, half_w, max_h * 0.5, start_size=50)
    left_lbl = measure_block(str(content["left_label"]), font_path, half_w, max_h * 0.4, start_size=23)
    right_lbl = measure_block(str(content["right_label"]), font_path, half_w, max_h * 0.4, start_size=23)

    value_h = max(left_val["block_h"], right_val["block_h"])
    label_h = max(left_lbl["block_h"], right_lbl["block_h"])
    total_h = value_h + GAP + label_h
    panel_h = min(total_h + PAD * 2, max_h)

    scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)
    cx, cy = video_width // 2, video_height // 2
    panel = rounded_panel(scene, panel_w, panel_h, cx, cy, palette["navy_hex"], border_hex=None, radius=22)
    apply_fade_in(panel, 0.0, 0.3)

    left_cx = cx - DIVIDER_GAP // 2 - half_w // 2
    right_cx = cx + DIVIDER_GAP // 2 + half_w // 2
    top_y = cy - total_h // 2

    left_val_layer = scene.add_layer(
        mv.layer.Text("\n".join(left_val["lines"]), font_size=left_val["font_size"], font_family=font_family, color=palette["white_hex"]),
        position=(left_cx, top_y + value_h // 2),
    )
    left_val_layer.add_effect(mv.effect.DropShadow(offset=3.0, color="#000000", opacity=0.5, radius=4.0))
    apply_slide_in(left_val_layer, 0.1, 0.35, (left_cx - 100, top_y + value_h // 2), (left_cx, top_y + value_h // 2))

    right_val_layer = scene.add_layer(
        mv.layer.Text("\n".join(right_val["lines"]), font_size=right_val["font_size"], font_family=font_family, color=palette["orange_hex"]),
        position=(right_cx, top_y + value_h // 2),
    )
    right_val_layer.add_effect(mv.effect.DropShadow(offset=3.0, color="#000000", opacity=0.5, radius=4.0))
    apply_slide_in(right_val_layer, 0.15, 0.35, (right_cx + 100, top_y + value_h // 2), (right_cx, top_y + value_h // 2))

    add_text_layer(scene, left_lbl, left_cx, top_y + value_h + GAP, palette["offwhite_hex"], font_family, fade_start=0.3, add_shadow=False)
    add_text_layer(scene, right_lbl, right_cx, top_y + value_h + GAP, palette["offwhite_hex"], font_family, fade_start=0.3, add_shadow=False)

    scene.add_layer(
        mv.layer.Rectangle(size=(2, int(total_h)), color=palette["muted_blue_hex"]),
        position=(cx, cy),
    )

    return scene


def render_quote_card(content, duration, palette, video_width, video_height, font_path, font_family):
    _validate_content(content, ["quote"])
    quote = "\u201c" + str(content["quote"]) + "\u201d"
    attribution = str(content.get("attribution", ""))

    panel_w, _ = calculate_container_size("quote_card", video_width, video_height, char_count=len(quote))
    PAD, GAP = 64, 26
    max_h = int(video_height * 0.85)

    blocks = [measure_block(quote, font_path, panel_w - PAD * 2, max_h * 0.75, start_size=42)]
    if attribution:
        blocks.append(measure_block("\u2014 " + attribution, font_path, panel_w - PAD * 2, max_h * 0.15, start_size=23))

    panel_h, offsets = stack_blocks(blocks, PAD, GAP, max_h)

    scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)
    cx, cy = video_width // 2, video_height // 2
    panel = rounded_panel(scene, panel_w, panel_h, cx, cy, palette["navy_hex"], border_hex=palette["orange_hex"], radius=26)
    apply_fade_in(panel, 0.0, 0.35)
    apply_scale_pop(panel, 0.0, 0.4, from_scale=0.94, to_scale=1.0)

    content_top = cy - panel_h // 2 + PAD
    colors = [palette["white_hex"], palette["orange_hex"]]
    for i, block in enumerate(blocks):
        add_text_layer(scene, block, cx, content_top + offsets[i], colors[i], font_family, fade_start=0.2 + i * 0.2)

    return scene


def render_list_reveal(content, duration, palette, video_width, video_height, font_path, font_family):
    _validate_content(content, ["heading", "items"])
    heading = str(content["heading"]).upper()
    items = content.get("items", [])[:6]
    if not items:
        raise ValueError("list_reveal requires at least one item.")

    panel_w, _ = calculate_container_size("list_reveal", video_width, video_height, item_count=len(items))
    PAD, GAP, ITEM_GAP = 50, 26, 16
    max_h = int(video_height * 0.85)

    heading_block = measure_block(heading, font_path, panel_w - PAD * 2, 100, start_size=38)
    item_blocks = [measure_block(str(item), font_path, panel_w - PAD * 2 - 30, 80, start_size=27) for item in items]

    items_total_h = sum(b["block_h"] for b in item_blocks) + ITEM_GAP * (len(item_blocks) - 1)
    total_h = heading_block["block_h"] + GAP + items_total_h
    panel_h = min(total_h + PAD * 2, max_h)

    scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)
    cx, cy = video_width // 2, video_height // 2
    panel = rounded_panel(scene, panel_w, panel_h, cx, cy, palette["navy_hex"], border_hex=None, radius=22)
    apply_fade_in(panel, 0.0, 0.3)

    content_top = cy - panel_h // 2 + PAD
    add_text_layer(scene, heading_block, cx, content_top, palette["orange_hex"], font_family, fade_start=0.1)

    cursor = content_top + heading_block["block_h"] + GAP
    dot_x = cx - (panel_w - PAD * 2) // 2 + 10

    for idx, (item, block) in enumerate(zip(items, item_blocks)):
        start_t = 0.25 + idx * 0.13
        dot = scene.add_layer(
            mv.layer.Rectangle(size=(14, 14), color=palette["orange_hex"], radius=7),
            position=(dot_x, cursor + block["block_h"] // 2),
        )
        apply_fade_in(dot, start_t, 0.2)

        item_layer = scene.add_layer(
            mv.layer.Text("\n".join(block["lines"]), font_size=block["font_size"], font_family=font_family, color=palette["white_hex"]),
            position=(cx + 15, cursor + block["block_h"] // 2),
        )
        apply_fade_in(item_layer, start_t, 0.2)
        cursor += block["block_h"] + ITEM_GAP

    return scene


def render_bar_chart(content, duration, palette, video_width, video_height, font_path, font_family):
    _validate_content(content, ["categories", "values"])
    categories = content["categories"]
    values = [float(v) for v in content["values"]]
    max_v = max(values) if values else 1

    panel_w, panel_h = calculate_container_size("bar_chart", video_width, video_height, item_count=len(values))
    scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)
    cx, cy = video_width // 2, video_height // 2
    panel = rounded_panel(scene, panel_w, panel_h, cx, cy, palette["navy_hex"], border_hex=None, radius=22)
    apply_fade_in(panel, 0.0, 0.3)

    PAD_TOP = 90
    title_block = measure_block(str(content.get("title", "")).upper(), font_path, panel_w - 100, 60, start_size=34)
    top_y = cy - panel_h // 2
    add_text_layer(scene, title_block, cx - (panel_w // 2) + 60 + title_block["block_h"], top_y + 45, palette["white_hex"], font_family, fade_start=0.1, add_shadow=False)

    chart_w = panel_w - 140
    chart_h = panel_h - PAD_TOP - 90
    ox = cx - chart_w // 2
    oy = cy + chart_h // 2
    bar_w = chart_w // (len(values) * 2)

    for idx, (cat, val) in enumerate(zip(categories, values)):
        bar_h = int((val / max_v) * chart_h)
        x = ox + idx * 2 * bar_w + bar_w
        color = palette["orange_hex"] if idx == len(values) - 1 else palette["muted_blue_hex"]
        bar = scene.add_layer(
            mv.layer.Rectangle(size=(bar_w, bar_h), color=color, radius=4),
            position=(x, oy - bar_h // 2),
        )
        start_t = 0.15 + idx * 0.06
        bar.scale.enable_motion().extend(keyframes=[start_t, start_t + 0.3], values=[(1.0, 0.0), (1.0, 1.0)], easings=["ease_out"])

        lbl = measure_block(str(cat)[:10], font_path, bar_w * 2, 40, start_size=22)
        add_text_layer(scene, lbl, x, oy + 16, palette["offwhite_hex"], font_family, fade_start=start_t, add_shadow=False)

    return scene


def render_line_chart(content, duration, palette, video_width, video_height, font_path, font_family):
    _validate_content(content, ["x_labels", "values"])
    x_labels = content["x_labels"]
    values = [float(v) for v in content["values"]]
    max_v, min_v = max(values), min(values)

    panel_w, panel_h = calculate_container_size("line_chart", video_width, video_height, item_count=len(values))
    scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)
    cx, cy = video_width // 2, video_height // 2
    panel = rounded_panel(scene, panel_w, panel_h, cx, cy, palette["navy_hex"], border_hex=None, radius=22)
    apply_fade_in(panel, 0.0, 0.3)

    title_block = measure_block(str(content.get("title", "")).upper(), font_path, panel_w - 100, 60, start_size=34)
    top_y = cy - panel_h // 2
    add_text_layer(scene, title_block, cx - (panel_w // 2) + 60 + title_block["block_h"], top_y + 45, palette["white_hex"], font_family, fade_start=0.1, add_shadow=False)

    chart_w, chart_h = panel_w - 140, panel_h - 200
    ox, oy = cx - chart_w // 2, cy + chart_h // 2
    n = max(2, len(values))

    points = []
    for idx, val in enumerate(values):
        x = ox + int(idx / (n - 1) * chart_w)
        norm = (val - min_v) / (max_v - min_v) if max_v != min_v else 0.5
        y = oy - int(norm * chart_h)
        points.append((x, y))

    for idx in range(len(points) - 1):
        x1, y1 = points[idx]
        x2, y2 = points[idx + 1]
        seg_len = int(math.hypot(x2 - x1, y2 - y1))
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2
        seg = scene.add_layer(
            mv.layer.Rectangle(size=(max(seg_len, 2), 5), color=palette["orange_hex"]),
            position=(mx, my), rotation=angle,
        )
        apply_fade_in(seg, 0.25 + idx * (0.5 / max(1, len(points) - 1)), 0.15)

    for idx, (x, y) in enumerate(points):
        node = scene.add_layer(
            mv.layer.Rectangle(size=(16, 16), color=palette["white_hex"], radius=8),
            position=(x, y),
        )
        start_t = 0.2 + idx * (0.5 / max(1, len(points) - 1))
        apply_scale_pop(node, start_t, 0.2)

        lbl = measure_block(str(x_labels[idx]), font_path, chart_w // n, 40, start_size=20)
        add_text_layer(scene, lbl, x, oy + 20, palette["offwhite_hex"], font_family, fade_start=start_t, add_shadow=False)

    return scene


# ============== TYPE -> STYLE REGISTRY ==============

TEXT_BOX_STYLES = [render_text_box]
COMPARISON_STYLES = [render_comparison]
BAR_CHART_STYLES = [render_bar_chart]
LINE_CHART_STYLES = [render_line_chart]
LIST_REVEAL_STYLES = [render_list_reveal]
QUOTE_CARD_STYLES = [render_quote_card]
STAT_STYLES = [render_stat_callout]


def select_style_fn(graphic):
    g_type = graphic["type"]
    seed = graphic.get("trigger_phrase", "") + str(graphic.get("paragraph_index", 0))

    if g_type == "text_box":
        return pick_variant(TEXT_BOX_STYLES, seed)
    if g_type == "comparison":
        return pick_variant(COMPARISON_STYLES, seed)
    if g_type == "bar_chart":
        return pick_variant(BAR_CHART_STYLES, seed)
    if g_type == "line_chart":
        return pick_variant(LINE_CHART_STYLES, seed)
    if g_type == "list_reveal":
        return pick_variant(LIST_REVEAL_STYLES, seed)
    if g_type == "quote_card":
        return pick_variant(QUOTE_CARD_STYLES, seed)
    if g_type == "stat_callout":
        return pick_variant(STAT_STYLES, seed)
    return pick_variant(TEXT_BOX_STYLES, seed)
