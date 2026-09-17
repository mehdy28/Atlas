"""Pull Quote - state B (quote family)

Category: quote  |  Family: quote  |  Exposes: ['quote_text', 'accent_line']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_04b', 'category': 'quote', 'family': 'quote', 'label': 'Pull Quote (b)', 'exposes': ['quote_text', 'accent_line']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'quote_text': elem('quote', 220, 200, w=840, text=c.get('text') or c.get('kicker') or c.get('headline') or c.get('quote') or c.get('body') or c.get('label') or "We didn't expect the cut to land this fast, or this deep.", size=48), 'accent_line': elem('bar', 140, 180, w=5, h=320)}
