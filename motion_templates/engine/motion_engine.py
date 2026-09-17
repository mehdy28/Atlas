# motion_engine.py - Transition engine and HTML wrapper
import os

FPS, W, H = 30, 1280, 720
FONT = "font-family:'Inter','Helvetica Neue',Arial,sans-serif;-webkit-font-smoothing:antialiased;"
ORANGE, PINK = "#ff6a00", "#ee0979"

# Default signature ambient background (used when no underlying video/asset is provided)
DEFAULT_BG = (
    "radial-gradient(ellipse at 30% 65%, rgba(255,106,0,.06) 0%, transparent 50%), "
    "radial-gradient(ellipse at 75% 30%, rgba(238,9,121,.05) 0%, transparent 50%), "
    "linear-gradient(180deg, #100d0a 0%, #0a0806 100%)"
)

def c01(x):
    return max(0.0, min(1.0, float(x)))

def eoc(t):
    return 1.0 - (1.0 - c01(t)) ** 3

def eio(t):
    t = c01(t)
    return 4.0 * t ** 3 if t < 0.5 else 1.0 - (-2.0 * t + 2.0) ** 3 / 2.0

def ph(t, a, b):
    if b <= a:
        return 1.0 if t >= b else 0.0
    return c01((t - a) / (b - a))

def lerp(a, b, m):
    return a + (b - a) * m

def in_out(t, fade_in=0.1, fade_out=0.1, duration=1.0):
    """Smooth ease-in and ease-out opacity curve for overlay elements."""
    if duration <= 0: return 1.0
    local_p = t / float(duration)
    if local_p < fade_in:
        return eoc(local_p / max(1e-4, fade_in))
    if local_p > (1.0 - fade_out):
        return eoc((1.0 - local_p) / max(1e-4, fade_out))
    return 1.0

def elem(kind, x, y, w=0, h=0, opacity=1.0, scale=1.0, rotation=0.0, **content):
    return {"kind": kind, "x": x, "y": y, "w": w, "h": h,
            "opacity": opacity, "scale": scale, "rotation": rotation, "content": content}

GEOM_KEYS = ("x", "y", "w", "h", "scale", "rotation")

def render_element(name, e):
    x, y, w, h = e["x"], e["y"], e["w"], e["h"]
    op, sc, rot = e["opacity"], e["scale"], e["rotation"]
    c = e["content"]
    if op <= 0.002: return ""
    origin = c.get("origin", "top left")
    tag = f'data-el="{name}" data-kind="{e["kind"]}"'
    base = (f"position:absolute;left:{x:.1f}px;top:{y:.1f}px;"
            f"opacity:{op:.3f};transform:scale({sc:.4f}) rotate({rot:.2f}deg);"
            f"transform-origin:{origin};")

    if e["kind"] == "bar":
        c1, c2 = c.get("color1", ORANGE), c.get("color2", PINK)
        return f'<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;background:linear-gradient(180deg,{c1},{c2});box-shadow:0 0 40px rgba(255,106,0,.35);"></div>'

    if e["kind"] == "headline":
        return f'''<div {tag} style="{base}width:{w:.1f}px;">
            <div style="color:{ORANGE};font-size:{c.get('kicker_size',24)}px;font-weight:800;letter-spacing:9px;margin-bottom:20px;{FONT}">{c.get('kicker','')}</div>
            <div style="color:#fff;font-size:{c.get('size',100)}px;font-weight:900;line-height:1.03;letter-spacing:-2px;{FONT}">{c.get('text','')}</div>
        </div>'''

    if e["kind"] == "subtext":
        return f'<div {tag} style="{base}width:{w:.1f}px;color:{c.get("color","#ddd")};text-align:{c.get("align","left")};font-size:{c.get("size",28)}px;font-weight:700;line-height:1.4;letter-spacing:.5px;{FONT}">{c.get("text","")}</div>'

    if e["kind"] == "big_stat":
        align = c.get("align", "left")
        return f'''<div {tag} style="{base}width:{w:.1f}px;">
            <div style="text-align:{align};width:100%;color:{ORANGE};font-size:{c.get('kicker_size',20)}px;font-weight:800;letter-spacing:7px;margin-bottom:18px;{FONT}">{c.get('kicker','')}</div>
            <div style="text-align:{align};width:100%;color:#fff;font-size:{c.get('size',220)}px;font-weight:900;line-height:.82;letter-spacing:-7px;margin-bottom:24px;{FONT}">{c.get('number','')}</div>
            <div style="text-align:{align};width:100%;color:#ddd;font-size:{c.get('desc_size',28)}px;font-weight:700;letter-spacing:1.5px;line-height:1.4;{FONT}">{c.get('desc','')}</div>
        </div>'''

    if e["kind"] == "caption_panel":
        pad = c.get("padding", "28px 34px")
        k_sz, t_sz = c.get("kicker_size", 16), c.get("text_size", 32)
        k_html = f'<div style="color:{ORANGE};font-size:{k_sz}px;font-weight:800;letter-spacing:5px;margin-bottom:12px;{FONT}">{c.get("kicker","")}</div>' if c.get("kicker") else ""
        t_html = f'<div style="color:#fff;font-size:{t_sz}px;font-weight:800;line-height:1.28;{FONT}">{c.get("text","")}</div>' if c.get("text") else ""
        return f'''<div {tag} style="{base}width:{w:.1f}px;background:rgba(12,10,8,.94);padding:{pad};border-radius:10px;box-shadow:0 24px 80px rgba(0,0,0,.8);border:1px solid rgba(255,255,255,.08);">{k_html}{t_html}</div>'''

    return ""

def render_elements(elements: dict) -> str:
    return "\n".join(render_element(name, e) for name, e in elements.items())


def blend_geom(a, b, mix):
    return {k: lerp(a[k], b[k], mix) for k in GEOM_KEYS}

def morph(elements_a: dict, elements_b: dict, mix: float) -> dict:
    mix = c01(mix)
    out = {}
    for k in set(elements_a) | set(elements_b):
        a, b = elements_a.get(k), elements_b.get(k)
        if a and b:
            geom = blend_geom(a, b, mix)
            if a["content"] == b["content"] and a["kind"] == b["kind"]:
                out[k] = {**b, **geom, "opacity": lerp(a["opacity"], b["opacity"], mix)}
            else:
                out[k + "__out"] = {**a, **geom, "opacity": a["opacity"] * (1 - mix)}
                out[k + "__in"] = {**b, **geom, "opacity": b["opacity"] * mix}
        elif a and not b:
            out[k] = {**a, "opacity": a["opacity"] * (1 - mix)}
        elif b and not a:
            out[k] = {**b, "opacity": b["opacity"] * mix}
    return out

def slide_handoff_html(elements_a: dict, elements_b: dict, mix: float) -> str:
    m = eio(c01(mix))
    out_x, out_y = -W * 0.55 * m, H * 0.55 * m
    in_x, in_y = W * 0.55 * (1 - m), -H * 0.55 * (1 - m)
    a_html, b_html = render_elements(elements_a), render_elements(elements_b)
    return f'''
    <div style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;
        transform:translate({out_x:.1f}px,{out_y:.1f}px);opacity:{1-m:.3f};">{a_html}</div>
    <div style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;
        transform:translate({in_x:.1f}px,{in_y:.1f}px);opacity:{m:.3f};">{b_html}</div>
    '''

def cut_html(elements_a: dict, elements_b: dict, mix: float) -> str:
    return render_elements(elements_b if mix >= 0.5 else elements_a)

def wrap_frame(inner_html, bg=None, transparent=False):
    """
    Renders element HTML into a full 1280x720 canvas container.
    - transparent=True: for compositing directly over footage/video in video software.
    - transparent=False & bg=None: uses default signature warm brown ambient gradient.
    """
    if transparent:
        effective_bg = "transparent"
    elif bg is not None:
        effective_bg = bg
    else:
        effective_bg = DEFAULT_BG

    return f'''<!DOCTYPE html><html><head><style>
    html,body{{margin:0;padding:0;width:{W}px;height:{H}px;overflow:hidden;background:{effective_bg};}}
    *{{box-sizing:border-box;}}
    </style></head><body style="margin:0;background:{effective_bg};overflow:hidden;">
    <div style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;background:{effective_bg};">
        {inner_html}
    </div>
    </body></html>'''

class Sequence:
    def __init__(self, segments):
        self.segments = segments
        self.duration = segments[-1][-1]
        self._first_hold = segments[0]

    def resolve(self, t):
        t = min(t, self.duration - 1e-6)
        for seg in self.segments:
            kind = seg[0]
            t0, t1 = seg[-2], seg[-1]
            if t0 <= t < t1 or (t1 == self.duration and t >= t0):
                local = ph(t, t0, t1)
                if kind == "hold":
                    tpl = seg[1]
                    p = local if seg is self._first_hold else 1.0
                    return "hold", {"template": tpl.__name__, "p": p, "elements": tpl(p)}
        return "hold", {"template": "none", "p": 0.0, "elements": {}}

    def html_at(self, t):
        kind, info = self.resolve(t)
        return render_elements(info.get("elements", {}))

    @property
    def start_elements(self):
        return self.segments[0][1](0.0)

    @property
    def end_elements(self):
        return self.segments[-1][1](1.0)
