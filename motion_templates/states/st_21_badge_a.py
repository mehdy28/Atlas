"""Corner Badge Expand - state A (badge family)

Category: badge  |  Family: badge  |  Exposes: ['chip']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_21a',
    'category': 'badge',
    'family': 'badge',
    'label': 'Corner Badge Expand (a)',
    'exposes': ['chip'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "chip": elem('title_chip', 680, 80, label1='UPDATE', label2='', label1_size=30, border_w=8, padding='18px 28px'),
    }
