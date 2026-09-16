"""Title / Section Header - state B (banner family)

Category: title  |  Family: banner  |  Exposes: ['headline', 'accent_line']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_01b',
    'category': 'title',
    'family': 'banner',
    'label': 'Title / Section Header (b)',
    'exposes': ['headline', 'accent_line'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "headline": elem('headline', 140, 70, w=1100, scale=0.6, kicker='PART ONE', text='THE DECISION<br>NOBODY SAW COMING', size=84, kicker_size=22),
        "accent_line": elem('bar', 140, 204, w=100, h=4),
    }
