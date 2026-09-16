"""Single Stat Reveal - state B (stat family)

Category: stat  |  Family: stat  |  Exposes: ['big_stat']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_02b',
    'category': 'stat',
    'family': 'stat',
    'label': 'Single Stat Reveal (b)',
    'exposes': ['big_stat'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "big_stat": elem('big_stat', 140, 160, w=760, kicker='THE HEADLINE FIGURE', number='47%', desc='OF THE BUDGET<br>MOVED IN ONE MEETING', size=230, kicker_size=20, desc_size=30),
    }
