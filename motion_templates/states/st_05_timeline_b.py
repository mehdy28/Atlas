"""Timeline / Sequence of Events - state B (timeline family)

Category: timeline  |  Family: timeline  |  Exposes: ['timeline_track', 'marker_1']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_05b',
    'category': 'timeline',
    'family': 'timeline',
    'label': 'Timeline / Sequence of Events (b)',
    'exposes': ['timeline_track', 'marker_1'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "timeline_track": elem('timeline_track', 140, 360, w=1000, h=4),
        "marker_1": elem('timeline_marker', 200, 390, w=200, date='MONDAY', label='Budget freeze announced company-wide'),
    }
