# tpl_23_feature_to_split_world.py - Continuous 3D World Camera Pan
import os, sys
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import FONT, ORANGE, PINK, c01, eoc, eio, ph, wrap_frame

META = {
    'id': 'tpl_23_feature_to_split_world',
    'category': 'world',
    'family': 'world_sequence',
    'duration_s': 12.0,
    'description': 'Camera starts on Memo feature (T1), pans across dark ambient space, and settles on $10B split (T2)'
}

W, H = 1280, 720
WORLD_W, WORLD_H = 2400, 1800
T1_CX, T1_CY = 700, 1200
T2_CX, T2_CY = 1800, 550

CAMERA_KEYS = [
    (0.0, T1_CX, T1_CY, 1.0),
    (5.0, T1_CX, T1_CY, 1.0),
    (6.8, T2_CX, T2_CY, 1.0),
    (12.0, T2_CX, T2_CY, 1.0),
]

def camera_at(t):
    if t <= CAMERA_KEYS[0][0]: return CAMERA_KEYS[0][1:]
    if t >= CAMERA_KEYS[-1][0]: return CAMERA_KEYS[-1][1:]
    for i in range(len(CAMERA_KEYS) - 1):
        t0, x0, y0, z0 = CAMERA_KEYS[i]
        t1, x1, y1, z1 = CAMERA_KEYS[i + 1]
        if t0 <= t <= t1:
            p = eio(ph(t, t0, t1))
            return (x0 + (x1 - x0) * p, y0 + (y1 - y0) * p, z0 + (z1 - z0) * p)
    return CAMERA_KEYS[-1][1:]

def cam_transform(cam_x, cam_y, zoom=1.0):
    tx = W / 2.0 - cam_x * zoom
    ty = H / 2.0 - cam_y * zoom
    return f"translate({tx:.2f}px, {ty:.2f}px) scale({zoom:.4f})"

def render_html(t, duration=12.0, transparent=False):
    cam_x, cam_y, zoom = camera_at(t)
    tf = cam_transform(cam_x, cam_y, zoom)

    # T1 elements (located at T1_CX, T1_CY)
    ox1, oy1 = (T1_CX - 550), (T1_CY - 360)
    img_enter = eoc(ph(t, 0.0, 2.0))
    title_enter = eoc(ph(t, 0.5, 2.2))
    logo_enter = eoc(ph(t, 0.8, 2.4))
    mp = eio(ph(t, 3.2, 4.4))
    img_w = 900 + (520 - 900) * mp
    img_x = (ox1 + 100) + ((ox1 + 60) - (ox1 + 100)) * mp
    img_y = (oy1 + 79) + (1 - img_enter) * 40
    title_op = title_enter * (1 - eoc(ph(mp, 0.0, 0.4)))
    panel_op = eoc(ph(mp, 0.35, 1.0))
    panel_x = ox1 + 700 + (1 - panel_op) * 60

    t1_html = f'''
    <div style="position:absolute;left:{img_x:.1f}px;top:{img_y:.1f}px;width:{img_w:.1f}px;height:562px;
        background:linear-gradient(135deg,#2e241c,#151210);opacity:{img_enter:.3f};
        box-shadow:0 40px 120px rgba(0,0,0,.85);border:1px solid rgba(255,255,255,.08);border-radius:6px;"></div>
    <div style="position:absolute;left:{img_x+30:.1f}px;top:{img_y+30:.1f}px;opacity:{title_op:.3f};
        display:flex;align-items:stretch;box-shadow:0 20px 60px rgba(0,0,0,.7);">
        <div style="width:6px;background:{ORANGE};"></div>
        <div style="background:rgba(12,10,8,.95);padding:18px 24px;">
            <div style="color:#fff;font-size:22px;font-weight:900;{FONT}">THE NUMBER</div>
            <div style="color:#aaa;font-size:12px;font-weight:700;letter-spacing:5px;margin-top:5px;{FONT}">A WEEK OF CUTS</div>
        </div>
    </div>
    <div style="position:absolute;left:{panel_x:.1f}px;top:{oy1+170}px;width:380px;opacity:{panel_op:.3f};">
        <div style="color:{ORANGE};font-size:16px;font-weight:800;letter-spacing:7px;margin-bottom:14px;{FONT}">THE NUMBER</div>
        <div style="color:#fff;font-size:120px;font-weight:900;line-height:.85;letter-spacing:-5px;margin-bottom:14px;{FONT}">3,300</div>
        <div style="width:160px;height:4px;background:linear-gradient(90deg,{ORANGE},{PINK});margin-bottom:20px;"></div>
        <div style="color:#ddd;font-size:20px;font-weight:700;letter-spacing:2px;line-height:1.4;{FONT}">JOBS ELIMINATED<br>IN ONE WEEK</div>
    </div>
    '''

    # T2 elements (located at T2_CX, T2_CY)
    ox2, oy2 = (T2_CX - 550), (T2_CY - 300)
    num_p = eoc(ph(t, 5.8, 6.9))
    img_p = eoc(ph(t, 6.2, 7.3))
    bar_p = eoc(ph(t, 6.6, 7.2))

    t2_html = f'''
    <div style="position:absolute;left:{ox2+620}px;top:{oy2+60}px;width:4px;height:{int(480*bar_p)}px;
        background:linear-gradient(180deg,{ORANGE},{PINK});box-shadow:0 0 40px rgba(255,106,0,.5);"></div>
    <div style="position:absolute;left:{ox2+80}px;top:{oy2+100+(1-num_p)*30}px;opacity:{num_p:.3f};">
        <div style="color:{ORANGE};font-size:18px;font-weight:800;letter-spacing:8px;margin-bottom:20px;{FONT}">THE REAL STORY</div>
        <div style="color:#fff;font-size:160px;font-weight:900;line-height:.85;letter-spacing:-6px;margin-bottom:24px;{FONT}">$10B</div>
        <div style="color:#ddd;font-size:24px;font-weight:700;letter-spacing:2px;line-height:1.4;{FONT}">INVESTED IN ROBOTAXI</div>
        <div style="color:#999;font-size:16px;font-weight:600;letter-spacing:3px;margin-top:14px;{FONT}">IN THE SAME WEEK</div>
    </div>
    <div style="position:absolute;left:{ox2+700}px;top:{oy2+40+(1-img_p)*40}px;width:340px;height:520px;
        background:linear-gradient(135deg,#1f1a24,#0c0812);opacity:{img_p:.3f};
        box-shadow:0 40px 120px rgba(0,0,0,.85);border:1px solid rgba(255,255,255,.08);border-radius:6px;"></div>
    '''

    world_html = f'''
    <div style="position:absolute;left:0;top:0;width:{WORLD_W}px;height:{WORLD_H}px;
        transform:{tf};transform-origin:0 0;
        background:
        radial-gradient(ellipse at 30% 65%, rgba(255,106,0,.06) 0%, transparent 50%),
        radial-gradient(ellipse at 75% 30%, rgba(238,9,121,.05) 0%, transparent 50%),
        linear-gradient(180deg, #100d0a 0%, #0a0806 100%);">
        {t1_html}
        {t2_html}
    </div>
    '''
    return wrap_frame(world_html, transparent=transparent)
