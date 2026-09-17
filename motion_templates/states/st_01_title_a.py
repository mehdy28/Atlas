"""Title / Section Header - state A (banner family)

Category: title  |  Family: banner  |  Exposes: ['headline', 'accent_line']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_01a', 'category': 'title', 'family': 'banner', 'label': 'Title / Section Header (a)', 'exposes': ['headline', 'accent_line']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'headline': elem('headline', 140, 140, w=1100, kicker=c.get('kicker') or c.get('category') or c.get('subtitle') or 'PART ONE', text=c.get('text') or c.get('kicker') or c.get('headline') or c.get('quote') or c.get('body') or c.get('label') or 'THE DECISION<br>NOBODY SAW COMING', size=84, kicker_size=22), 'accent_line': elem('bar', 140, 380, w=220, h=6)}
