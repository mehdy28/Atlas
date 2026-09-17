# tpl_22_stat_split_full.py - $10B Robotaxi Stat + Image Split
import os, sys
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import FONT, ORANGE, PINK, wrap_frame, in_out, eoc, ph

META = {
    'id': 'tpl_22_stat_split_full',
    'category': 'split',
    'family': 'split',
    'duration_s': 5.0,
    'description': '$10B Stat reveal paired with a vertical divider and photo panel'
}

def render_html(t, duration=5.0, kicker="THE REAL STORY", number="$10B",
                desc="INVESTED IN ROBOTAXI", note="IN THE SAME WEEK",
                image_src="", transparent=False):
    num_p = eoc(ph(t, 0.0, 1.1))
    img_p = eoc(ph(t, 0.4, 1.5))
    bar_p = eoc(ph(t, 0.7, 1.3))

    ox, oy = (1280 // 2 - 550), (720 // 2 - 300)
    num_x = ox + 80
    num_y = oy + 100 + (1 - num_p) * 30
    img_x = ox + 700
    img_y = oy + 40 + (1 - img_p) * 40

    img_style = f"background-image:url('file://{image_src}');background-size:cover;" if image_src and os.path.exists(image_src) else "background:linear-gradient(135deg,#1f1a24 0%,#0c0812 100%);"

    inner = f'''
    <div style="position:absolute;left:{ox+620}px;top:{oy+60}px;
        width:4px;height:{int(480*bar_p)}px;
        background:linear-gradient(180deg,{ORANGE},{PINK});
        box-shadow:0 0 40px rgba(255,106,0,.5);"></div>
    <div style="position:absolute;left:{num_x}px;top:{num_y}px;opacity:{num_p:.3f};">
        <div style="color:{ORANGE};font-size:18px;font-weight:800;letter-spacing:8px;margin-bottom:20px;{FONT}">{kicker}</div>
        <div style="color:#fff;font-size:160px;font-weight:900;line-height:.85;letter-spacing:-6px;margin-bottom:24px;{FONT}">{number}</div>
        <div style="color:#ddd;font-size:24px;font-weight:700;letter-spacing:2px;line-height:1.4;{FONT}">{desc}</div>
        <div style="color:#999;font-size:16px;font-weight:600;letter-spacing:3px;margin-top:14px;{FONT}">{note}</div>
    </div>
    <div style="position:absolute;left:{img_x}px;top:{img_y}px;
        width:340px;height:520px;{img_style}
        opacity:{img_p:.3f};box-shadow:0 40px 120px rgba(0,0,0,.85);
        border:1px solid rgba(255,255,255,.08);border-radius:6px;"></div>
    '''
    return wrap_frame(inner, transparent=transparent)
