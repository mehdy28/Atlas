"""Warning / Alert Card - state C (warning family)

Category: warning  |  Family: warning  |  Exposes: ['badge', 'headline', 'detail']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_14c',
    'category': 'warning',
    'family': 'warning',
    'label': 'Warning / Alert Card (c)',
    'exposes': ['badge', 'headline', 'detail'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "badge": elem('alert_badge', 160, 260, w=90, h=80),
        "headline": elem('headline', 290, 250, w=820, kicker='', text="THIS WASN'T IN<br>THE PRESS RELEASE", size=52, kicker_size=1),
        "detail": elem('subtext', 290, 410, w=700, text='Internal documents tell a different story.', size=24, color='#ccc'),
    }
