"""Two-Stat Comparison - state C (compare family)

Category: compare  |  Family: compare  |  Exposes: ['primary_stat', 'secondary_stat', 'accent_line']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_03c',
    'category': 'compare',
    'family': 'compare',
    'label': 'Two-Stat Comparison (c)',
    'exposes': ['primary_stat', 'secondary_stat', 'accent_line'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "primary_stat": elem('big_stat', 130, 170, w=480, scale=0.85, kicker='BEFORE', number='1,200', desc='STAFF ON<br>THE PROJECT', size=180, kicker_size=18, desc_size=26),
        "accent_line": elem('bar', 660, 130, w=4, h=320),
        "secondary_stat": elem('big_stat', 740, 170, w=440, kicker='AFTER', number='340', desc='STAFF ON<br>THE PROJECT', size=180, kicker_size=18, desc_size=26),
    }
