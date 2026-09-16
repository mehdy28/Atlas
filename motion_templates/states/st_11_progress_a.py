"""Progress / Milestone Fill - state A (progress family)

Category: progress  |  Family: progress  |  Exposes: ['track', 'kicker_label']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_11a',
    'category': 'progress',
    'family': 'progress',
    'label': 'Progress / Milestone Fill (a)',
    'exposes': ['track', 'kicker_label'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "track": elem('bar', 140, 300, w=900, h=8, color1='#3a3a3a', color2='#3a3a3a'),
        "kicker_label": elem('subtext', 140, 240, w=700, text='BUDGET REALLOCATED', size=20, color='#ff6a00'),
    }
