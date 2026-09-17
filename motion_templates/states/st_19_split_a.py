"""50/50 Split Panel - state A (split family)

Category: split  |  Family: split  |  Exposes: ['panel']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_19a', 'category': 'split', 'family': 'split', 'label': '50/50 Split Panel (a)', 'exposes': ['panel']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'panel': elem('image', 0, 0, w=620, h=720, c1='#2a1a10', c2='#0a0806')}
