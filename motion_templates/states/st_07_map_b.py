"""Map / Location Reveal - state B (map family)

Category: map  |  Family: map  |  Exposes: ['map_bg', 'pin']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_07b',
    'category': 'map',
    'family': 'map',
    'label': 'Map / Location Reveal (b)',
    'exposes': ['map_bg', 'pin'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "map_bg": elem('map_bg', 0, 0, w=1280, h=720),
        "pin": elem('pin', 610, 320, w=90, h=90, ring=0.0),
    }
