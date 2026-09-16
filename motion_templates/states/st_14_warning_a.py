"""Warning / Alert Card - state A (warning family)

Category: warning  |  Family: warning  |  Exposes: ['badge']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_14a',
    'category': 'warning',
    'family': 'warning',
    'label': 'Warning / Alert Card (a)',
    'exposes': ['badge'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "badge": elem('alert_badge', 160, 260, w=90, h=80),
    }
