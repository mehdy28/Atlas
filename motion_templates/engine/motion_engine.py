# motion_engine.py - Complete Motion Graphics Transition Engine
import os

FPS, W, H = 30, 1280, 720
FONT = "font-family:'Inter','Helvetica Neue',Arial,sans-serif;-webkit-font-smoothing:antialiased;"
ORANGE, PINK = "#ff6a00", "#ee0979"

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

    k = e["kind"]

    if k == "bar":
        c1, c2 = c.get("color1", ORANGE), c.get("color2", PINK)
        return f'<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;background:linear-gradient(180deg,{c1},{c2});box-shadow:0 0 40px rgba(255,106,0,.35);"></div>'

    if k == "headline":
        k_html = f'<div style="color:{ORANGE};font-size:{c.get("kicker_size",24)}px;font-weight:800;letter-spacing:9px;margin-bottom:20px;{FONT}">{c.get("kicker","")}</div>' if c.get("kicker") else ""
        return f'<div {tag} style="{base}width:{w:.1f}px;">{k_html}<div style="color:#fff;font-size:{c.get("size",84)}px;font-weight:900;line-height:1.03;letter-spacing:-2px;{FONT}">{c.get("text","")}</div></div>'

    if k == "subtext":
        return f'<div {tag} style="{base}width:{w:.1f}px;color:{c.get("color","#ddd")};text-align:{c.get("align","left")};font-size:{c.get("size",28)}px;font-weight:700;line-height:1.4;letter-spacing:.5px;{FONT}">{c.get("text","")}</div>'

    if k == "big_stat":
        align = c.get("align", "left")
        k_html = f'<div style="text-align:{align};width:100%;color:{ORANGE};font-size:{c.get("kicker_size",20)}px;font-weight:800;letter-spacing:7px;margin-bottom:18px;{FONT}">{c.get("kicker","")}</div>' if c.get("kicker") else ""
        desc_html = f'<div style="text-align:{align};width:100%;color:#ddd;font-size:{c.get("desc_size",28)}px;font-weight:700;letter-spacing:1.5px;line-height:1.4;{FONT}">{c.get("desc","")}</div>' if c.get("desc") else ""
        return f'<div {tag} style="{base}width:{w:.1f}px;">{k_html}<div style="text-align:{align};width:100%;color:#fff;font-size:{c.get("size",220)}px;font-weight:900;line-height:.82;letter-spacing:-7px;margin-bottom:24px;{FONT}">{c.get("number","")}</div>{desc_html}</div>'

    if k == "caption_panel":
        pad = c.get("padding", "28px 34px")
        k_sz, t_sz = c.get("kicker_size", 16), c.get("text_size", 32)
        k_html = f'<div style="color:{ORANGE};font-size:{k_sz}px;font-weight:800;letter-spacing:5px;margin-bottom:12px;{FONT}">{c.get("kicker","")}</div>' if c.get("kicker") else ""
        t_html = f'<div style="color:#fff;font-size:{t_sz}px;font-weight:800;line-height:1.28;{FONT}">{c.get("text","")}</div>' if c.get("text") else ""
        return f'<div {tag} style="{base}width:{w:.1f}px;background:rgba(12,10,8,.94);padding:{pad};border-radius:10px;box-shadow:0 24px 80px rgba(0,0,0,.8);border:1px solid rgba(255,255,255,.08);">{k_html}{t_html}</div>'

    if k == "quote":
        return f'<div {tag} style="{base}width:{w:.1f}px;color:#fff;font-size:{c.get("size",48)}px;font-weight:700;line-height:1.35;letter-spacing:-0.5px;font-style:italic;{FONT}">“{c.get("text","")}”</div>'

    if k == "credit_line":
        return f'<div {tag} style="{base}width:{w:.1f}px;"><div style="color:#fff;font-size:{c.get("name_size",40)}px;font-weight:900;letter-spacing:-1px;{FONT}">{c.get("name","")}</div><div style="color:{ORANGE};font-size:{c.get("role_size",18)}px;font-weight:800;letter-spacing:4px;margin-top:6px;{FONT}">{c.get("role","")}</div></div>'

    if k == "timeline_track":
        return f'<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;background:rgba(255,255,255,0.15);border-radius:2px;"></div>'

    if k == "timeline_marker":
        return f'<div {tag} style="{base}width:{w:.1f}px;"><div style="width:12px;height:12px;border-radius:50%;background:{ORANGE};box-shadow:0 0 16px {ORANGE};margin-bottom:12px;"></div><div style="color:{ORANGE};font-size:16px;font-weight:800;letter-spacing:3px;margin-bottom:6px;{FONT}">{c.get("date","")}</div><div style="color:#eee;font-size:20px;font-weight:700;line-height:1.3;{FONT}">{c.get("label","")}</div></div>'

    if k == "list_container":
        return f'<div {tag} style="{base}width:{w:.1f}px;color:{ORANGE};font-size:22px;font-weight:800;letter-spacing:6px;border-bottom:1px solid rgba(255,106,0,0.3);padding-bottom:14px;{FONT}">{c.get("title","")}</div>'

    if k == "list_item":
        return f'<div {tag} style="{base}width:{w:.1f}px;display:flex;align-items:center;"><span style="color:{ORANGE};font-size:24px;font-weight:900;margin-right:20px;{FONT}">{c.get("rank","")}</span><span style="color:#fff;font-size:32px;font-weight:800;letter-spacing:-0.5px;{FONT}">{c.get("text","")}</span></div>'

    if k == "title_chip":
        l2_html = f'<div style="color:#aaa;font-size:16px;font-weight:700;letter-spacing:1px;margin-top:4px;{FONT}">{c.get("label2","")}</div>' if c.get("label2") else ""
        return f'<div {tag} style="{base}display:inline-block;padding:{c.get("padding","18px 28px")};background:rgba(18,14,10,.95);border-left:{c.get("border_w",8)}px solid {ORANGE};border-radius:4px;box-shadow:0 20px 50px rgba(0,0,0,.8);"><div style="color:#fff;font-size:{c.get("label1_size",26)}px;font-weight:900;letter-spacing:2px;{FONT}">{c.get("label1","")}</div>{l2_html}</div>'

    if k == "radial_progress":
        pct = float(c.get("pct", 0.0))
        deg = int(pct * 360)
        return f'<div {tag} style="{base}width:{w:.1f}px;height:{w:.1f}px;border-radius:50%;background:conic-gradient({ORANGE} {deg}deg, rgba(255,255,255,0.08) {deg}deg);display:flex;align-items:center;justify-content:center;box-shadow:0 0 50px rgba(255,106,0,.25);"><div style="width:{w*0.75:.1f}px;height:{w*0.75:.1f}px;border-radius:50%;background:#0e0b09;display:flex;flex-direction:column;align-items:center;justify-content:center;"><div style="color:#fff;font-size:{c.get("number_size",72)}px;font-weight:900;letter-spacing:-2px;{FONT}">{c.get("number","")}</div><div style="color:{ORANGE};font-size:{c.get("label_size",16)}px;font-weight:800;letter-spacing:3px;margin-top:4px;{FONT}">{c.get("label","")}</div></div></div>'

    if k == "chart_bars":
        bars = c.get("bars", [])
        bar_html = "".join([f'<div style="flex:1;height:{float(b)*100:.1f}%;background:linear-gradient(180deg,{ORANGE},{PINK});border-radius:4px 4px 0 0;box-shadow:0 0 20px rgba(255,106,0,.25);"></div>' for b in bars])
        return f'<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;display:flex;align-items:flex-end;gap:18px;border-bottom:2px solid rgba(255,255,255,0.2);padding-bottom:4px;">{bar_html}</div>'

    if k == "chart_label":
        return f'<div {tag} style="{base}color:#fff;font-size:{c.get("size",26)}px;font-weight:800;letter-spacing:1px;{FONT}">{c.get("text","")}</div>'

    if k == "tile_grid":
        items = c.get("items", [])
        tiles = "".join([f'<div style="flex:1;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:24px;color:#fff;font-size:24px;font-weight:800;text-align:center;{FONT}">{item}</div>' for item in items])
        return f'<div {tag} style="{base}width:{w:.1f}px;display:flex;gap:16px;">{tiles}</div>'

    if k == "alert_badge":
        return f'<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;background:rgba(255,50,50,0.15);border:2px solid #ff3333;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#ff3333;font-size:36px;font-weight:900;{FONT}">!</div>'

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

def wrap_frame(inner_html, bg=None, transparent=False):
    effective_bg = "transparent" if transparent else (bg or DEFAULT_BG)
    return f"""<!DOCTYPE html><html><head><style>
    html,body{{margin:0;padding:0;width:{W}px;height:{H}px;overflow:hidden;background:{effective_bg};}}
    *{{box-sizing:border-box;}}
    </style></head><body style="margin:0;background:{effective_bg};overflow:hidden;">
    <div style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;background:{effective_bg};">
        {inner_html}
    </div>
    </body></html>"""

class Sequence:
    def __init__(self, segments, content=None):
        self.segments = segments
        self.duration = segments[-1][-1]
        self.content = content or {}
        self._first_hold = segments[0]

    def _call(self, fn, p):
        try:
            return fn(p, content=self.content)
        except TypeError:
            return fn(p)

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
                    return "hold", {"elements": self._call(tpl, p)}
                elif kind == "morph":
                    tpl_a, tpl_b = seg[1], seg[2]
                    return "morph", {"elements": morph(self._call(tpl_a, 1.0), self._call(tpl_b, 1.0), local)}
        return "hold", {"elements": {}}

    def html_at(self, t):
        _, info = self.resolve(t)
        return render_elements(info.get("elements", {}))

# Backward-compatibility alias for template imports
if 'ease_in_out' in globals():
    in_out = ease_in_out
elif 'ease_inout' in globals():
    in_out = ease_inout
else:
    def in_out(t, b=0, c=1, d=1):
    t = t / (d / 2.0)
    if t < 1:
        return c / 2.0 * t * t + b
    t -= 1
    return -c / 2.0 * (t * (t - 2) - 1) + b
