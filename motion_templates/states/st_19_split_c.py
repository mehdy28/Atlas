"""50/50 Split Panel - state C (split family)

Category: split  |  Family: split  |  Exposes: ['panel', 'headline', 'caption']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_19c',
    'category': 'split',
    'family': 'split',
    'label': '50/50 Split Panel (c)',
    'exposes': ['panel', 'headline', 'caption'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "panel": elem('image', 0, 0, w=620, h=720, c1='#2a1a10', c2='#0a0806'),
        "headline": elem('headline', 720, 230, w=460, kicker='THE FACILITY', text='BUILT IN<br>18 MONTHS', size=64, kicker_size=18),
        "caption": elem('subtext', 720, 480, w=460, text='Construction records, obtained via FOIA request.', size=18, color='#999'),
    }
