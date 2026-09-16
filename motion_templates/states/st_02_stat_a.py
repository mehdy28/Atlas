"""Single Stat Reveal - state A (stat family)

Category: stat  |  Family: stat  |  Exposes: ['kicker_only']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_02a',
    'category': 'stat',
    'family': 'stat',
    'label': 'Single Stat Reveal (a)',
    'exposes': ['kicker_only'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "kicker_only": elem('subtext', 140, 160, w=600, text='THE HEADLINE FIGURE', size=20, color='#ff6a00'),
    }
