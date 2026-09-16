"""Grid / Roster Reveal - state A (grid family)

Category: grid  |  Family: grid  |  Exposes: ['title']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_15a',
    'category': 'grid',
    'family': 'grid',
    'label': 'Grid / Roster Reveal (a)',
    'exposes': ['title'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "title": elem('subtext', 160, 220, w=700, text='WHO SIGNED OFF', size=22, color='#ff6a00'),
    }
