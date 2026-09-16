"""Lower Third Caption - state A (lowerthird family)

Category: lowerthird  |  Family: lowerthird  |  Exposes: ['bar_bg']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_18a',
    'category': 'lowerthird',
    'family': 'lowerthird',
    'label': 'Lower Third Caption (a)',
    'exposes': ['bar_bg'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "bar_bg": elem('caption_panel', 120, 530, w=780, kicker='', text='', padding='24px 34px'),
    }
