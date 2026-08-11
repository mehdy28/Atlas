
from typing import Tuple


def to_pixels(rel_x: float, rel_y: float, width: int, height: int) -> Tuple[int, int]:
    return int(rel_x * width), int(rel_y * height)


def apply_fade_in(layer_item, start: float, duration: float) -> None:
    layer_item.opacity.enable_motion().extend(
        keyframes=[start, start + duration], values=[0.0, 1.0], easings=["ease_out"]
    )


def apply_fade_out(layer_item, end_time: float, duration: float) -> None:
    layer_item.opacity.enable_motion().extend(
        keyframes=[end_time - duration, end_time], values=[1.0, 0.0], easings=["ease_out"]
    )


def apply_scale_pop(layer_item, start: float, duration: float,
                     from_scale: float = 0.0, to_scale: float = 1.0) -> None:
    layer_item.scale.enable_motion().extend(
        keyframes=[start, start + duration], values=[from_scale, to_scale], easings=["ease_out"]
    )


def apply_slide_in(layer_item, start: float, duration: float,
                    from_pos: Tuple[float, float], to_pos: Tuple[float, float]) -> None:
    layer_item.position.enable_motion().extend(
        keyframes=[start, start + duration], values=[from_pos, to_pos], easings=["ease_out"]
    )


def apply_slide_out(layer_item, end_time: float, duration: float,
                     from_pos: Tuple[float, float], to_pos: Tuple[float, float]) -> None:
    layer_item.position.enable_motion().extend(
        keyframes=[end_time - duration, end_time], values=[from_pos, to_pos], easings=["ease_in"]
    )
