
import subprocess


def build_panel_overlay(idx, variant, start, duration, slide_dur, fade_dur,
                         video_width, panel_width, enter_from_left):
    """
    Builds one branch of the filter graph for a side panel. Slides in from
    off-screen, holds, slides back out. Uses time-based x expressions.
    """
    tag_in = str(idx) + ":v"
    gfx_tag = "gfx" + str(idx)

    slide_end = start + slide_dur
    hold_end = start + duration - slide_dur
    exit_end = start + duration

    if enter_from_left:
        off_x = "-" + str(panel_width)
        rest_x = "0"
        x_expr = (
            "if(lt(t," + str(start) + ")," + off_x + ","
            "if(lt(t," + str(slide_end) + ")," + off_x + "+(t-" + str(start) + ")/" + str(slide_dur) + "*(" + rest_x + "-(" + off_x + ")),"
            "if(lt(t," + str(hold_end) + ")," + rest_x + ","
            "if(lt(t," + str(exit_end) + ")," + rest_x + "-(t-" + str(hold_end) + ")/" + str(slide_dur) + "*(" + rest_x + "-(" + off_x + "))," + off_x + "))))"
        )
    else:
        off_x = str(video_width)
        rest_x = str(video_width - panel_width)
        x_expr = (
            "if(lt(t," + str(start) + ")," + off_x + ","
            "if(lt(t," + str(slide_end) + ")," + off_x + "-(t-" + str(start) + ")/" + str(slide_dur) + "*(" + off_x + "-(" + rest_x + ")),"
            "if(lt(t," + str(hold_end) + ")," + rest_x + ","
            "if(lt(t," + str(exit_end) + ")," + rest_x + "+(t-" + str(hold_end) + ")/" + str(slide_dur) + "*(" + off_x + "-(" + rest_x + "))," + off_x + "))))"
        )

    prep = "[" + tag_in + "]setpts=PTS-STARTPTS+" + str(start) + "/TB[" + gfx_tag + "]"
    overlay = (
        "overlay=x='" + x_expr + "':y=0:enable='between(t," + str(start) + "," + str(exit_end) + ")'"
    )
    return prep, overlay, gfx_tag


def build_scrim_overlay(idx, start, duration, fade_dur):
    """Full-screen scrim: fades in/out in place, no slide needed."""
    tag_in = str(idx) + ":v"
    gfx_tag = "gfx" + str(idx)

    fade_out_start = duration - fade_dur

    prep = (
        "[" + tag_in + "]format=rgba,"
        "fade=t=in:st=0:d=" + str(fade_dur) + ":alpha=1,"
        "fade=t=out:st=" + str(fade_out_start) + ":d=" + str(fade_dur) + ":alpha=1,"
        "setpts=PTS-STARTPTS+" + str(start) + "/TB[" + gfx_tag + "]"
    )
    overlay = "overlay=x=0:y=0:enable='between(t," + str(start) + "," + str(start + duration) + ")'"
    return prep, overlay, gfx_tag


def render_all_graphics_single_pass(base_video_path, graphics, output_path,
                                     video_width, video_height, fps,
                                     display_duration, fade_duration, slide_duration):
    """
    graphics: list of dicts, each with keys:
      png_path, variant ('panel' or 'scrim'), start_seconds,
      panel_width (only for panel), enter_from_left (only for panel)
    Builds ONE ffmpeg command with all overlays chained, encoding once.
    """
    inputs = ["-i", base_video_path]
    filter_parts = []
    prev_tag = "0:v"

    for idx, g in enumerate(graphics, start=1):
        display_dur = display_duration

        if g["variant"] == "panel":
            inputs += ["-loop", "1", "-t", str(display_dur), "-i", g["png_path"]]
            prep, overlay, gfx_tag = build_panel_overlay(
                idx, g["variant"], g["start_seconds"], display_dur, slide_duration, fade_duration,
                video_width, g["panel_width"], g["enter_from_left"]
            )
        else:
            inputs += ["-loop", "1", "-t", str(display_dur), "-i", g["png_path"]]
            prep, overlay, gfx_tag = build_scrim_overlay(idx, g["start_seconds"], display_dur, fade_duration)

        out_tag = "v" + str(idx)
        filter_parts.append(prep)
        filter_parts.append("[" + prev_tag + "][" + gfx_tag + "]" + overlay + "[" + out_tag + "]")
        prev_tag = out_tag

    filter_complex = ";".join(filter_parts)

    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[" + prev_tag + "]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr
