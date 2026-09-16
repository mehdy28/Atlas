"""APPROVAL - state A (radial family)

Category: radial  |  Family: radial  |  Exposes: ['ring']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_20a',
    'category': 'radial',
    'family': 'radial',
    'label': 'APPROVAL (a)',
    'exposes': ['ring'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "ring": elem('radial_progress', 460, 120, w=360, pct=0.0, number='', label='', number_size=84, label_size=18),
    }
