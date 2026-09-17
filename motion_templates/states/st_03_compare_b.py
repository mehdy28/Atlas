"""Two-Stat Comparison - state B (compare family)

Category: compare  |  Family: compare  |  Exposes: ['primary_stat', 'accent_line']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_03b', 'category': 'compare', 'family': 'compare', 'label': 'Two-Stat Comparison (b)', 'exposes': ['primary_stat', 'accent_line']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'primary_stat': elem('big_stat', 130, 170, w=480, scale=0.85, kicker=c.get('kicker') or c.get('category') or c.get('subtitle') or 'BEFORE', number=c.get('number') or c.get('stat') or c.get('value') or '1,200', desc=c.get('desc') or c.get('label') or c.get('detail') or 'STAFF ON<br>THE PROJECT', size=180, kicker_size=18, desc_size=26), 'accent_line': elem('bar', 660, 130, w=4, h=320)}
