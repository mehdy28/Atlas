"""Enumerated / Ranked List - state A (list family)

Category: list  |  Family: list  |  Exposes: ['list_container']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_06a', 'category': 'list', 'family': 'list', 'label': 'Enumerated / Ranked List (a)', 'exposes': ['list_container']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'list_container': elem('list_container', 160, 200, w=800, title=c.get('title') or c.get('heading') or c.get('text') or 'THREE THINGS THAT CHANGED')}
