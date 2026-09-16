"""Progress / Milestone Fill - state B (progress family)

Category: progress  |  Family: progress  |  Exposes: ['track', 'fill', 'pct_text']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_11b',
    'category': 'progress',
    'family': 'progress',
    'label': 'Progress / Milestone Fill (b)',
    'exposes': ['track', 'fill', 'pct_text'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "track": elem('bar', 140, 300, w=900, h=8, color1='#3a3a3a', color2='#3a3a3a'),
        "fill": elem('bar', 140, 300, w=738.0, h=8),
        "pct_text": elem('headline', 140, 150, w=500, kicker='BUDGET REALLOCATED', text='82%', size=96, kicker_size=20),
    }
