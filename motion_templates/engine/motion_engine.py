"""
motion_engine.py - shared transition engine for the template library.

Element schema: every state function returns {name: elem(...)}.
  elem(kind, x, y, w=0, h=0, opacity=1.0, scale=1.0, rotation=0.0, **content)
"""
import os

FPS, W, H = 30, 1280, 720
FONT = "font-family:'Inter','Helvetica Neue',Arial,sans-serif;-webkit-font-smoothing:antialiased;"
ORANGE, PINK = "#ff6a00", "#ee0979"


def c01(x):
    return max(0.0, min(1.0, float(x)))

def eoc(t):
    t = c01(t)
    return 1.0 - (1.0 - t) ** 3

def eio(t):
    t = c01(t)
    return 4.0 * t ** 3 if t < 0.5 else 1.0 - (-2.0 * t + 2.0) ** 3 / 2.0

def ph(t, a, b):
    if b <= a:
        return 1.0 if t >= b else 0.0
    return c01((t - a) / (b - a))

def lerp(a, b, m):
    return a + (b - a) * m


# ---------- element schema ----------
def elem(kind, x, y, w=0, h=0, opacity=1.0, scale=1.0, rotation=0.0, **content):
    return {"kind": kind, "x": x, "y": y, "w": w, "h": h,
            "opacity": opacity, "scale": scale, "rotation": rotation, "content": content}

GEOM_KEYS = ("x", "y", "w", "h", "scale", "rotation")


# ---------- generic renderer ----------
def render_element(name, e):
    x, y, w, h = e["x"], e["y"], e["w"], e["h"]
    op, sc, rot = e["opacity"], e["scale"], e["rotation"]
    c = e["content"]
    if op <= 0.002:
        return ""
    origin = c.get("origin", "top left")
    tag = f'data-el="{name}" data-kind="{e["kind"]}"'
    base = (f"position:absolute;left:{x:.1f}px;top:{y:.1f}px;"
            f"opacity:{op:.3f};transform:scale({sc:.4f}) rotate({rot:.2f}deg);"
            f"transform-origin:{origin};")

    if e["kind"] == "bar":
        c1 = c.get("color1", ORANGE)
        c2 = c.get("color2", PINK)
        return f"""<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;
            background:linear-gradient(180deg,{c1},{c2});
            box-shadow:0 0 40px rgba(255,106,0,.35);"></div>"""

    if e["kind"] == "headline":
        return f"""<div {tag} style="{base}width:{w:.1f}px;">
            <div style="color:{ORANGE};font-size:{c.get('kicker_size',24)}px;font-weight:800;letter-spacing:9px;margin-bottom:20px;{FONT}">{c.get('kicker','')}</div>
            <div style="color:#fff;font-size:{c.get('size',100)}px;font-weight:900;line-height:1.03;letter-spacing:-2px;{FONT}">{c.get('text','')}</div>
        </div>"""

    if e["kind"] == "subtext":
        return f"""<div {tag} style="{base}width:{w:.1f}px;color:{c.get('color','#ddd')};
            text-align:{c.get('align','left')};
            font-size:{c.get('size',28)}px;font-weight:700;line-height:1.4;letter-spacing:.5px;{FONT}">{c.get('text','')}</div>"""

    if e["kind"] == "big_stat":
        align = c.get("align", "left")
        return f"""<div {tag} style="{base}width:{w:.1f}px;">
            <div style="text-align:{align};width:100%;color:{ORANGE};font-size:{c.get('kicker_size',20)}px;font-weight:800;letter-spacing:7px;margin-bottom:18px;{FONT}">{c.get('kicker','')}</div>
            <div style="text-align:{align};width:100%;color:#fff;font-size:{c.get('size',220)}px;font-weight:900;line-height:.82;letter-spacing:-7px;margin-bottom:24px;{FONT}">{c.get('number','')}</div>
            <div style="text-align:{align};width:100%;color:#ddd;font-size:{c.get('desc_size',28)}px;font-weight:700;letter-spacing:1.5px;line-height:1.4;{FONT}">{c.get('desc','')}</div>
        </div>"""

    if e["kind"] == "quote":
        return f"""<div {tag} style="{base}width:{w:.1f}px;color:#fff;font-size:{c.get('size',46)}px;
            font-weight:700;font-style:italic;line-height:1.32;{FONT}">&ldquo;{c.get('text','')}&rdquo;</div>"""

    if e["kind"] == "timeline_track":
        return f"""<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;
            background:linear-gradient(90deg,{ORANGE},{PINK});"></div>"""

    if e["kind"] == "timeline_marker":
        return f"""<div {tag} style="{base}">
            <div style="width:18px;height:18px;border-radius:50%;background:#fff;
                box-shadow:0 0 0 4px rgba(255,106,0,.35);margin-bottom:14px;"></div>
            <div style="color:{ORANGE};font-size:15px;font-weight:800;letter-spacing:2px;margin-bottom:6px;{FONT}">{c.get('date','')}</div>
            <div style="color:#eee;font-size:19px;font-weight:700;{FONT}">{c.get('label','')}</div>
        </div>"""

    if e["kind"] == "list_container":
        return f"""<div {tag} style="{base}width:{w:.1f}px;">
            <div style="color:{ORANGE};font-size:20px;font-weight:800;letter-spacing:6px;{FONT}">{c.get('title','')}</div>
        </div>"""

    if e["kind"] == "list_item":
        return f"""<div {tag} style="{base}width:{w:.1f}px;display:flex;align-items:baseline;gap:18px;">
            <div style="color:{ORANGE};font-size:34px;font-weight:900;{FONT}">{c.get('rank','')}</div>
            <div style="color:#fff;font-size:30px;font-weight:700;{FONT}">{c.get('text','')}</div>
        </div>"""

    if e["kind"] == "map_bg":
        line_c = "rgba(255,255,255,.06)"
        lines = "".join(f'<div style="position:absolute;left:{i*80}px;top:0;width:1px;height:{h:.0f}px;background:{line_c};"></div>' for i in range(int(w // 80) + 1))
        lines += "".join(f'<div style="position:absolute;left:0;top:{i*80}px;width:{w:.0f}px;height:1px;background:{line_c};"></div>' for i in range(int(h // 80) + 1))
        return f"""<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;background:#0d0f10;overflow:hidden;">{lines}</div>"""

    if e["kind"] == "pin":
        ring = c.get("ring", 1.0)
        return f"""<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;">
            <div style="position:absolute;left:50%;top:50%;width:{w*ring:.1f}px;height:{w*ring:.1f}px;
                margin:-{w*ring/2:.1f}px 0 0 -{w*ring/2:.1f}px;border-radius:50%;
                border:2px solid {ORANGE};opacity:{max(0,1-ring*0.8):.2f};"></div>
            <div style="position:absolute;left:50%;top:50%;width:{w:.1f}px;height:{w:.1f}px;
                margin:-{w/2:.1f}px 0 0 -{w/2:.1f}px;border-radius:50% 50% 50% 0;
                transform:rotate(-45deg);background:linear-gradient(135deg,{ORANGE},{PINK});
                box-shadow:0 10px 30px rgba(0,0,0,.6);"></div>
        </div>"""

    if e["kind"] == "caption_panel":
        pad = c.get("padding", "28px 32px")
        k_sz = c.get("kicker_size", 16)
        t_sz = c.get("text_size", 28)
        kicker_html = f'<div style="color:{ORANGE};font-size:{k_sz}px;font-weight:800;letter-spacing:5px;margin-bottom:12px;{FONT}">{c.get("kicker","")}</div>' if c.get("kicker") else ""
        text_html = f'<div style="color:#fff;font-size:{t_sz}px;font-weight:800;line-height:1.28;{FONT}">{c.get("text","")}</div>' if c.get("text") else ""
        return f"""<div {tag} style="{base}width:{w:.1f}px;background:rgba(10,10,10,.94);
            padding:{pad};border-radius:10px;box-shadow:0 24px 80px rgba(0,0,0,.8);border:1px solid rgba(255,255,255,.08);">
            {kicker_html}{text_html}
        </div>"""

    if e["kind"] == "image":
        src = c.get("src", "")
        if src and os.path.exists(src):
            bg = f"background-image:url('file://{src}');background-size:cover;background-position:left center;"
        else:
            bg = f"background:linear-gradient(145deg,{c.get('c1', '#2a2a2a')},{c.get('c2', '#111')});"
        return f"""<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;{bg}overflow:hidden;
            box-shadow:0 40px 120px rgba(0,0,0,.85);border:1px solid rgba(255,255,255,.08);"></div>"""

    if e["kind"] == "title_chip":
        border_w = c.get("border_w", 6)
        pad = c.get("padding", "18px 24px")
        l1_size = c.get("label1_size", 22)
        l2_size = c.get("label2_size", 12)
        l2_html = f'<div style="color:#aaa;font-size:{l2_size}px;font-weight:700;letter-spacing:5px;margin-top:5px;{FONT}">{c.get("label2","")}</div>' if c.get("label2") else ""
        return f"""<div {tag} style="{base}display:flex;align-items:stretch;box-shadow:0 24px 70px rgba(0,0,0,.75);border-radius:4px;overflow:hidden;">
            <div style="width:{border_w}px;background:linear-gradient(180deg,{ORANGE},{PINK});"></div>
            <div style="background:rgba(12,10,8,.95);padding:{pad};">
                <div style="color:#fff;font-size:{l1_size}px;font-weight:900;{FONT}">{c.get('label1','')}</div>
                {l2_html}
            </div>
        </div>"""

    if e["kind"] == "logo_chip":
        size = c.get("size", 48)
        pad = c.get("padding", "14px 18px")
        src = c.get("src", "")
        if src and os.path.exists(src):
            img_html = f"<img src='file://{src}' style='height:{size}px;display:block;'>"
        else:
            img_html = f"<div style='height:{size}px;width:{size}px;background:linear-gradient(135deg,{ORANGE},{PINK});border-radius:8px;'></div>"
        return f"""<div {tag} style="{base}padding:{pad};background:rgba(12,10,8,.94);
            border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,.7);border:1px solid rgba(255,255,255,.08);">{img_html}</div>"""

    if e["kind"] == "chart_axis":
        return f"""<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;
            border-left:3px solid rgba(255,255,255,.5);border-bottom:3px solid rgba(255,255,255,.5);"></div>"""

    if e["kind"] == "chart_bars":
        bars = c.get("bars", [])
        n = max(1, len(bars))
        gap = w / n
        bw = gap * 0.6
        inner = "".join(
            f'<div style="position:absolute;left:{i*gap:.1f}px;bottom:0;width:{bw:.1f}px;'
            f'height:{bv*h:.1f}px;background:linear-gradient(180deg,{ORANGE},{PINK});border-radius:4px 4px 0 0;"></div>'
            for i, bv in enumerate(bars)
        )
        return f"""<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;">{inner}</div>"""

    if e["kind"] == "chart_label":
        return f"""<div {tag} style="{base}color:#fff;font-size:{c.get('size',22)}px;font-weight:800;{FONT}">{c.get('text','')}</div>"""

    if e["kind"] == "alert_badge":
        return f"""<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;position:relative;">
            <div style="width:0;height:0;border-left:{w/2:.1f}px solid transparent;
                border-right:{w/2:.1f}px solid transparent;border-bottom:{h*0.86:.1f}px solid {ORANGE};
                filter:drop-shadow(0 10px 24px rgba(255,106,0,.5));"></div>
            <div style="position:absolute;left:0;top:{h*0.22:.1f}px;width:{w:.1f}px;text-align:center;
                color:#0a0806;font-size:{w*0.42:.1f}px;font-weight:900;{FONT}">!</div>
        </div>"""

    if e["kind"] == "tile_grid":
        items = c.get("items", [])
        n = max(1, len(items))
        cols = c.get("cols", n)
        gap = 18
        tile_w = (w - gap * (cols - 1)) / cols
        tile_h = h
        tiles = "".join(
            f'<div style="position:absolute;left:{i*(tile_w+gap):.1f}px;top:0;width:{tile_w:.1f}px;height:{tile_h:.1f}px;'
            f'background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:10px;'
            f'display:flex;align-items:center;justify-content:center;color:#eee;font-size:16px;font-weight:800;'
            f'text-align:center;padding:8px;{FONT}">{label}</div>'
            for i, label in enumerate(items)
        )
        return f"""<div {tag} style="{base}width:{w:.1f}px;height:{h:.1f}px;">{tiles}</div>"""

    if e["kind"] == "credit_line":
        n_sz = c.get("name_size", 38)
        r_sz = c.get("role_size", 18)
        return f"""<div {tag} style="{base}width:{w:.1f}px;">
            <div style="color:#fff;font-size:{n_sz}px;font-weight:800;letter-spacing:-.5px;{FONT}">{c.get('name','')}</div>
            <div style="color:{ORANGE};font-size:{r_sz}px;font-weight:700;letter-spacing:2.5px;margin-top:6px;{FONT}">{c.get('role','')}</div>
        </div>"""

    if e["kind"] == "radial_progress":
        pct = max(0.0, min(1.0, c.get("pct", 0.0))) * 100
        n_sz = c.get("number_size", int(w * 0.22))
        l_sz = c.get("label_size", max(14, int(w * 0.055)))
        ring_ratio = c.get("ring_ratio", 0.74)
        ring = f"conic-gradient({ORANGE} 0% {pct:.1f}%, rgba(255,255,255,.10) {pct:.1f}% 100%)"
        inner = w * ring_ratio
        return f"""<div {tag} style="{base}width:{w:.1f}px;height:{w:.1f}px;border-radius:50%;
            background:{ring};display:flex;align-items:center;justify-content:center;
            box-shadow:0 30px 80px rgba(0,0,0,.75);">
            <div style="width:{inner:.1f}px;height:{inner:.1f}px;border-radius:50%;background:#0d0a08;
                display:flex;flex-direction:column;align-items:center;justify-content:center;">
                <div style="color:#fff;font-size:{n_sz}px;font-weight:900;letter-spacing:-2px;{FONT}">{c.get('number','')}</div>
                <div style="color:{ORANGE};font-size:{l_sz}px;font-weight:800;letter-spacing:2px;margin-top:8px;{FONT}">{c.get('label','')}</div>
            </div>
        </div>"""

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
    return f"""
    <div style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;
        transform:translate({out_x:.1f}px,{out_y:.1f}px);opacity:{1-m:.3f};">{a_html}</div>
    <div style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;
        transform:translate({in_x:.1f}px,{in_y:.1f}px);opacity:{m:.3f};">{b_html}</div>
    """

def cut_html(elements_a: dict, elements_b: dict, mix: float) -> str:
    return render_elements(elements_b if mix >= 0.5 else elements_a)

def wrap_frame(inner_html, bg="linear-gradient(180deg,#100d0a,#0a0806)"):
    return f"""<!DOCTYPE html><html><head><style>
    html,body{{margin:0;padding:0;width:{W}px;height:{H}px;overflow:hidden;}}
    *{{box-sizing:border-box;}}
    </style></head><body style="margin:0;background:{bg};overflow:hidden;">
    <div style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;background:{bg};">
        {inner_html}
    </div>
    </body></html>"""

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
                a_fn, b_fn = seg[1], seg[2]
                a_state, b_state = a_fn(1.0), b_fn(1.0)
                if kind == "morph":
                    mix = eio(local)
                    return "morph", {"a": a_fn.__name__, "b": b_fn.__name__, "mix": mix,
                                      "elements": morph(a_state, b_state, mix)}
                if kind == "slide":
                    return "slide", {"a": a_fn.__name__, "b": b_fn.__name__, "mix": local,
                                      "a_elements": a_state, "b_elements": b_state}
                if kind == "cut":
                    return "cut", {"a": a_fn.__name__, "b": b_fn.__name__, "mix": local,
                                    "a_elements": a_state, "b_elements": b_state}
        return "hold", {"template": "none", "p": 0.0, "elements": {}}

    def html_at(self, t):
        kind, info = self.resolve(t)
        if kind == "slide":
            return slide_handoff_html(info["a_elements"], info["b_elements"], info["mix"])
        if kind == "cut":
            return cut_html(info["a_elements"], info["b_elements"], info["mix"])
        return render_elements(info["elements"])

    @property
    def start_elements(self):
        """Elements dict at the very start (p=0 of the first state)."""
        first_tpl = self.segments[0][1]
        return first_tpl(0.0)

    @property
    def end_elements(self):
        """Elements dict at the very end (steady look of the last state)."""
        last_tpl = self.segments[-1][1]
        return last_tpl(1.0)

