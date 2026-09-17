# tpl_25_broadcast_lowerthird.py - Broadcast Gradient Lower Third
import os, sys
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import FONT, ORANGE, PINK, wrap_frame, in_out

META = {
    'id': 'tpl_25_broadcast_lowerthird',
    'category': 'lowerthird',
    'family': 'overlay',
    'duration_s': 5.0,
    'description': 'Broadcast speaker lower-third with gradient nametag card'
}

def render_html(t, duration=5.0, name="DR. AMARA OKONKWO", title="Marine Biologist — Reef Restoration Project",
                transparent=True):
    p = in_out(t, 0.12, 0.12, duration)
    tx = int(-420 * (1.0 - p))
    inner = f'''
    <div style="position:absolute;left:70px;bottom:90px;{FONT}transform:translateX({tx}px);opacity:{p:.3f};box-shadow:0 20px 60px rgba(0,0,0,.75);">
        <div style="background:linear-gradient(90deg,{ORANGE},{PINK});color:#fff;font-size:38px;
            font-weight:900;letter-spacing:.5px;padding:12px 32px;border-radius:8px 8px 0 0;">{name}</div>
        <div style="background:rgba(12,10,8,.94);color:#eee;font-size:20px;font-weight:700;padding:10px 32px;
            border-radius:0 0 8px 8px;border:1px solid rgba(255,255,255,.08);border-top:none;">{title}</div>
    </div>
    '''
    return wrap_frame(inner, transparent=transparent)
