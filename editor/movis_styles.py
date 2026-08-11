
import movis as mv
from typing import Dict, Any
from sizing.container_sizing import calculate_container_size, fit_text_to_container
from editor.movis_animations import apply_fade_in, apply_scale_pop, apply_slide_in


def _validate_content(content: Dict[str, Any], required_keys: list) -> None:
    missing = [k for k in required_keys if k not in content or not str(content[k]).strip()]
    if missing:
        raise ValueError("Missing required content keys: " + str(missing))


def render_text_box(content: Dict[str, Any], duration: float, palette: Dict[str, Any],
                     video_width: int, video_height: int, font_path: str, font_family: str) -> mv.layer.Composition:
    """Lower-third style panel: navy background, heading + body, slides in from left."""
    _validate_content(content, ["heading"])
    heading = str(content["heading"]).upper()
    body = str(content.get("body", ""))

    panel_w, panel_h = calculate_container_size("text_box", video_width, video_height, char_count=len(body))
    scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)

    panel = scene.add_layer(
        mv.layer.Rectangle(size=(panel_w, panel_h), color=palette["navy_hex"], radius=16),
        name="panel", position=(panel_w // 2, video_height - panel_h // 2 - 40),
    )
    apply_slide_in(panel, 0.0, 0.4, (-panel_w, video_height - panel_h // 2 - 40), (panel_w // 2, video_height - panel_h // 2 - 40))

    h_size, h_lines, h_line_h = fit_text_to_container(heading, font_path, panel_w - 60, panel_h // 2, start_size=48)
    heading_layer = scene.add_layer(
        mv.layer.Text("\n".join(h_lines), font_size=h_size, font_family=font_family, color=palette["white_hex"]),
        name="heading", position=(panel_w // 2, video_height - panel_h + 50),
    )
    apply_fade_in(heading_layer, 0.15, 0.3)

    if body:
        b_size, b_lines, b_line_h = fit_text_to_container(body, font_path, panel_w - 60, panel_h // 2, start_size=26)
        body_layer = scene.add_layer(
            mv.layer.Text("\n".join(b_lines), font_size=b_size, font_family=font_family, color=palette["offwhite_hex"]),
            name="body", position=(panel_w // 2, video_height - panel_h // 2 + 20),
        )
        apply_fade_in(body_layer, 0.25, 0.3)

    return scene


def render_stat_callout(content: Dict[str, Any], duration: float, palette: Dict[str, Any],
                         video_width: int, video_height: int, font_path: str, font_family: str) -> mv.layer.Composition:
    """Large centered number in a circular glass panel, scale-pop entrance."""
    _validate_content(content, ["stat"])
    stat = str(content["stat"])
    label = str(content.get("label", ""))

    box_w, box_h = calculate_container_size("stat_callout", video_width, video_height, char_count=len(label))
    scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)

    circle = scene.add_layer(
        mv.layer.Ellipse(radius=(box_w // 2, box_h // 2), color=palette["navy_hex"]),
        name="circle", position=(video_width // 2, video_height // 2),
    )
    apply_scale_pop(circle, 0.0, 0.45, from_scale=0.0, to_scale=1.0)

    stat_size, stat_lines, _ = fit_text_to_container(stat, font_path, box_w - 80, box_h // 2, start_size=160)
    stat_layer = scene.add_layer(
        mv.layer.Text(stat, font_size=stat_size, font_family=font_family, color=palette["white_hex"]),
        name="stat_text", position=(video_width // 2, video_height // 2 - box_h // 6),
    )
    apply_fade_in(stat_layer, 0.3, 0.25)

    if label:
        label_size, label_lines, _ = fit_text_to_container(label, font_path, box_w - 100, box_h // 3, start_size=28)
        label_layer = scene.add_layer(
            mv.layer.Text("\n".join(label_lines), font_size=label_size, font_family=font_family, color=palette["orange_hex"]),
            name="label_text", position=(video_width // 2, video_height // 2 + box_h // 4),
        )
        apply_fade_in(label_layer, 0.45, 0.25)

    return scene


def render_bar_chart(content: Dict[str, Any], duration: float, palette: Dict[str, Any],
                      video_width: int, video_height: int, font_path: str, font_family: str) -> mv.layer.Composition:
    """Growing bars, each animated in with a staggered scale-up on the y-axis via position slide."""
    _validate_content(content, ["categories", "values"])
    categories = content["categories"]
    values = [float(v) for v in content["values"]]
    if not categories or not values or len(categories) != len(values):
        raise ValueError("bar_chart requires matching categories and values lists.")

    panel_w, panel_h = calculate_container_size("bar_chart", video_width, video_height, item_count=len(values))
    scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)

    panel = scene.add_layer(
        mv.layer.Rectangle(size=(panel_w, panel_h), color=palette["navy_hex"], radius=20),
        name="panel", position=(video_width // 2, video_height // 2),
    )
    apply_fade_in(panel, 0.0, 0.3)

    max_v = max(values)
    chart_w = panel_w - 120
    chart_h = panel_h - 200
    bar_w = chart_w // (len(values) * 2)
    base_x = video_width // 2 - chart_w // 2
    base_y = video_height // 2 + chart_h // 2

    for idx, (cat, val) in enumerate(zip(categories, values)):
        bar_h = int((val / max_v) * chart_h)
        x = base_x + idx * 2 * bar_w + bar_w
        color = palette["orange_hex"] if idx == len(values) - 1 else palette["muted_blue_hex"]

        bar = scene.add_layer(
            mv.layer.Rectangle(size=(bar_w, bar_h), color=color),
            name="bar_" + str(idx), position=(x, base_y - bar_h // 2), anchor_point=(0.5, 0.5),
        )
        start_t = 0.1 + idx * 0.08
        bar.scale.enable_motion().extend(
            keyframes=[start_t, start_t + 0.3], values=[(1.0, 0.0), (1.0, 1.0)], easings=["ease_out"]
        )

        label_size, _, _ = fit_text_to_container(str(cat), font_path, bar_w * 2, 40, start_size=22)
        scene.add_layer(
            mv.layer.Text(str(cat), font_size=label_size, font_family=font_family, color=palette["offwhite_hex"]),
            name="label_" + str(idx), position=(x, base_y + 30),
        )

    return scene


def render_list_reveal(content: Dict[str, Any], duration: float, palette: Dict[str, Any],
                        video_width: int, video_height: int, font_path: str, font_family: str) -> mv.layer.Composition:
    """Staggered fade+slide list items, one per line, in a glass panel."""
    _validate_content(content, ["heading", "items"])
    heading = str(content["heading"]).upper()
    items = content.get("items", [])
    if not items:
        raise ValueError("list_reveal requires at least one item.")

    panel_w, panel_h = calculate_container_size("list_reveal", video_width, video_height, item_count=len(items))
    scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)

    panel = scene.add_layer(
        mv.layer.Rectangle(size=(panel_w, panel_h), color=palette["navy_hex"], radius=20),
        name="panel", position=(video_width // 2, video_height // 2),
    )
    apply_fade_in(panel, 0.0, 0.3)

    top_y = video_height // 2 - panel_h // 2 + 60
    h_size, h_lines, _ = fit_text_to_container(heading, font_path, panel_w - 80, 80, start_size=36)
    heading_layer = scene.add_layer(
        mv.layer.Text("\n".join(h_lines), font_size=h_size, font_family=font_family, color=palette["orange_hex"]),
        name="heading", position=(video_width // 2, top_y),
    )
    apply_fade_in(heading_layer, 0.1, 0.25)

    row_h = min(80, (panel_h - 150) // max(1, len(items)))
    for idx, item in enumerate(items[:6]):
        item_size, item_lines, _ = fit_text_to_container(str(item), font_path, panel_w - 120, row_h - 10, start_size=28)
        y = top_y + 70 + idx * row_h
        from_pos = (video_width // 2 - 80, y)
        to_pos = (video_width // 2, y)

        item_layer = scene.add_layer(
            mv.layer.Text("\n".join(item_lines), font_size=item_size, font_family=font_family, color=palette["white_hex"]),
            name="item_" + str(idx), position=from_pos,
        )
        start_t = 0.2 + idx * 0.15
        apply_slide_in(item_layer, start_t, 0.25, from_pos, to_pos)
        apply_fade_in(item_layer, start_t, 0.25)

    return scene


def render_comparison(content: Dict[str, Any], duration: float, palette: Dict[str, Any],
                       video_width: int, video_height: int, font_path: str, font_family: str) -> mv.layer.Composition:
    """Two-sided split panel, values slide in from opposite edges."""
    _validate_content(content, ["left_label", "left_value", "right_label", "right_value"])

    panel_w, panel_h = calculate_container_size("comparison", video_width, video_height)
    scene = mv.layer.Composition(size=(video_width, video_height), duration=duration)

    panel = scene.add_layer(
        mv.layer.Rectangle(size=(panel_w, panel_h), color=palette["navy_hex"], radius=20),
        name="panel", position=(video_width // 2, video_height // 2),
    )
    apply_fade_in(panel, 0.0, 0.3)

    left_cx = video_width // 2 - panel_w // 4
    right_cx = video_width // 2 + panel_w // 4

    lv_size, lv_lines, _ = fit_text_to_container(str(content["left_value"]), font_path, panel_w // 2 - 60, panel_h // 3, start_size=54)
    left_val = scene.add_layer(
        mv.layer.Text("\n".join(lv_lines), font_size=lv_size, font_family=font_family, color=palette["white_hex"]),
        name="left_val", position=(left_cx - panel_w // 3, video_height // 2 - 40),
    )
    apply_slide_in(left_val, 0.1, 0.35, (left_cx - panel_w // 3 - 100, video_height // 2 - 40), (left_cx, video_height // 2 - 40))

    rv_size, rv_lines, _ = fit_text_to_container(str(content["right_value"]), font_path, panel_w // 2 - 60, panel_h // 3, start_size=54)
    right_val = scene.add_layer(
        mv.layer.Text("\n".join(rv_lines), font_size=rv_size, font_family=font_family, color=palette["orange_hex"]),
        name="right_val", position=(right_cx + panel_w // 3 + 100, video_height // 2 - 40),
    )
    apply_slide_in(right_val, 0.15, 0.35, (right_cx + panel_w // 3 + 100, video_height // 2 - 40), (right_cx, video_height // 2 - 40))

    ll_size, ll_lines, _ = fit_text_to_container(str(content["left_label"]), font_path, panel_w // 2 - 60, 60, start_size=22)
    scene.add_layer(
        mv.layer.Text("\n".join(ll_lines), font_size=ll_size, font_family=font_family, color=palette["offwhite_hex"]),
        name="left_label", position=(left_cx, video_height // 2 + 60),
    )

    rl_size, rl_lines, _ = fit_text_to_container(str(content["right_label"]), font_path, panel_w // 2 - 60, 60, start_size=22)
    scene.add_layer(
        mv.layer.Text("\n".join(rl_lines), font_size=rl_size, font_family=font_family, color=palette["offwhite_hex"]),
        name="right_label", position=(right_cx, video_height // 2 + 60),
    )

    return scene
