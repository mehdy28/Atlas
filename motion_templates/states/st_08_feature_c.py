"""Image-Led Feature - state C (feature family)

Category: feature  |  Family: feature  |  Exposes: ['image', 'logo_chip', 'stat_panel']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_08c',
    'category': 'feature',
    'family': 'feature',
    'label': 'Image-Led Feature (c)',
    'exposes': ['image', 'logo_chip', 'stat_panel'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "image": elem('image', 190, 139, w=520, h=562, c1='#2a2a2a', c2='#111'),
        "logo_chip": elem('logo_chip', 620, 611, src=''),
        "stat_panel": elem('big_stat', 830, 230, w=380, kicker='THE NUMBER', number='3,300', desc='JOBS CUT<br>IN ONE WEEK', size=120, kicker_size=16, desc_size=20),
    }
