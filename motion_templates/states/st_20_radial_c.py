"""APPROVAL - state C (radial family)

Category: radial  |  Family: radial  |  Exposes: ['ring', 'desc']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_20c',
    'category': 'radial',
    'family': 'radial',
    'label': 'APPROVAL (c)',
    'exposes': ['ring', 'desc'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "ring": elem('radial_progress', 460, 120, w=360, pct=0.73, number='73%', label='APPROVAL', number_size=84, label_size=18),
        "desc": elem('subtext', 320, 520, w=640, text='Among employees surveyed internally.', size=24, color='#ccc', align='center'),
    }
