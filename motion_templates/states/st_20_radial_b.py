"""APPROVAL - state B (radial family)

Category: radial  |  Family: radial  |  Exposes: ['ring']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_20b', 'category': 'radial', 'family': 'radial', 'label': 'APPROVAL (b)', 'exposes': ['ring']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'ring': elem('radial_progress', 460, 120, w=360, pct=0.73, number=c.get('number') or c.get('stat') or c.get('value') or '73%', label=c.get('label') or c.get('desc') or c.get('text') or 'APPROVAL', number_size=84, label_size=18)}
