"""Full-Bleed Number Takeover - state B (takeover family)

Category: takeover  |  Family: takeover  |  Exposes: ['kicker', 'big_number']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_17b', 'category': 'takeover', 'family': 'takeover', 'label': 'Full-Bleed Number Takeover (b)', 'exposes': ['kicker', 'big_number']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'kicker': elem('subtext', 0, 190, w=1280, text=c.get('text') or c.get('kicker') or c.get('headline') or c.get('quote') or c.get('body') or c.get('label') or 'IN TOTAL', size=22, color='#ff6a00', align='center'), 'big_number': elem('big_stat', 0, 250, w=1280, kicker=c.get('kicker') or c.get('category') or c.get('subtitle') or '', number=c.get('number') or c.get('stat') or c.get('value') or '10X', desc=c.get('desc') or c.get('label') or c.get('detail') or '', size=280, kicker_size=1, desc_size=1, align='center')}
