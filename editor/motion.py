
import random


def _seeded_random(seed_value):
    return random.Random(seed_value)


def assign_motion_effect(scene_id, duration_seconds, min_zoom, max_zoom, max_pan_fraction, min_duration_for_pan):
    """
    Deterministically assigns a Ken Burns effect to a clip based on its
    scene_id (so re-running the editor produces the same result, not a
    new random effect every time).

    Returns a dict describing normalized start/end zoom and pan targets.
    Zoom values are scale factors (1.0 = no zoom). Pan values are
    fractional offsets of frame width/height, describing where the
    frame center drifts from -> to over the clip\'s duration.
    """
    rng = _seeded_random(scene_id)

    zoom_direction = rng.choice(["in", "out"])
    if zoom_direction == "in":
        zoom_start, zoom_end = min_zoom, rng.uniform(min_zoom + 0.03, max_zoom)
    else:
        zoom_start, zoom_end = rng.uniform(min_zoom + 0.03, max_zoom), min_zoom

    if duration_seconds >= min_duration_for_pan:
        pan_angle = rng.uniform(0, 360)
        import math
        pan_x = max_pan_fraction * math.cos(math.radians(pan_angle))
        pan_y = max_pan_fraction * math.sin(math.radians(pan_angle))
        pan_start = (0.0, 0.0)
        pan_end = (round(pan_x, 4), round(pan_y, 4))
    else:
        pan_start = (0.0, 0.0)
        pan_end = (0.0, 0.0)

    return {
        "zoom_start": round(zoom_start, 4),
        "zoom_end": round(zoom_end, 4),
        "pan_start_fraction": list(pan_start),
        "pan_end_fraction": list(pan_end),
    }
