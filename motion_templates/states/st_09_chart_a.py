"""Simple Chart Reveal - state A (chart family)

Category: chart  |  Family: chart  |  Exposes: ['chart_axis']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_09a', 'category': 'chart', 'family': 'chart', 'label': 'Simple Chart Reveal (a)', 'exposes': ['chart_axis']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'chart_axis': elem('chart_axis', 200, 180, w=880, h=360)}
