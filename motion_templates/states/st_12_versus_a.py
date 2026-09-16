"""Versus / Split Comparison - state A (versus family)

Category: versus  |  Family: versus  |  Exposes: ['side_left', 'divider']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_12a',
    'category': 'versus',
    'family': 'versus',
    'label': 'Versus / Split Comparison (a)',
    'exposes': ['side_left', 'divider'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "side_left": elem('headline', 220, 240, w=360, kicker='', text='BEFORE', size=76, kicker_size=1),
        "divider": elem('bar', 637, 180, w=3, h=280, color1='#444', color2='#444'),
    }
