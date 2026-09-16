"""Simple Chart Reveal - state B (chart family)

Category: chart  |  Family: chart  |  Exposes: ['chart_axis', 'chart_bars']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_09b',
    'category': 'chart',
    'family': 'chart',
    'label': 'Simple Chart Reveal (b)',
    'exposes': ['chart_axis', 'chart_bars'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "chart_axis": elem('chart_axis', 200, 180, w=880, h=360),
        "chart_bars": elem('chart_bars', 200, 180, w=880, h=360, bars=[0.3, 0.55, 0.4, 0.85, 0.6]),
    }
