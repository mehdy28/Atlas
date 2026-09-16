"""Enumerated / Ranked List - state A (list family)

Category: list  |  Family: list  |  Exposes: ['list_container']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_06a',
    'category': 'list',
    'family': 'list',
    'label': 'Enumerated / Ranked List (a)',
    'exposes': ['list_container'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "list_container": elem('list_container', 160, 200, w=800, title='THREE THINGS THAT CHANGED'),
    }
