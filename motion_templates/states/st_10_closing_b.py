"""Outro / Closing Card - state B (closing family)

Category: closing  |  Family: closing  |  Exposes: ['logo_chip', 'tagline']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_10b',
    'category': 'closing',
    'family': 'closing',
    'label': 'Outro / Closing Card (b)',
    'exposes': ['logo_chip', 'tagline'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "logo_chip": elem('logo_chip', 575, 160, size=76, padding='24px 28px', src=''),
        "tagline": elem('subtext', 220, 330, w=840, text='More of this story next episode.', size=38, color='#fff', align='center'),
    }
