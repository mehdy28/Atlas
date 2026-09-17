# tpl_24_breaking_ticker.py - Breaking News Crawl Bar
import os, sys
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import FONT, wrap_frame, in_out

META = {
    'id': 'tpl_24_breaking_ticker',
    'category': 'ticker',
    'family': 'overlay',
    'duration_s': 6.0,
    'description': 'Full-width bottom breaking news crawler with animated horizontal scroll'
}

def render_html(t, duration=6.0, text="Central bank raises interest rates for the third consecutive quarter amid inflation concerns",
                badge="BREAKING", transparent=True):
    p = in_out(t, 0.08, 0.08, duration)
    # Scroll from beyond the right edge across the full screen
    scroll_x = int(1280 - (1280 + 1100) * (t / float(duration)))
    inner = f'''
    <div style="position:absolute;left:0;bottom:0;width:100%;height:70px;background:rgba(5,5,5,.92);
        opacity:{p:.3f};display:flex;align-items:center;{FONT};border-top:2px solid #e50914;box-shadow:0 -10px 40px rgba(0,0,0,.8);">
        <div style="background:#e50914;color:#fff;font-weight:900;font-size:20px;letter-spacing:2px;
            padding:14px 28px;height:100%;display:flex;align-items:center;z-index:2;box-shadow:5px 0 20px rgba(0,0,0,.6);">{badge}</div>
        <div style="position:absolute;left:{scroll_x}px;color:#fff;font-size:22px;font-weight:700;white-space:nowrap;letter-spacing:.3px;">
            {text}
        </div>
    </div>
    '''
    return wrap_frame(inner, transparent=transparent)
