"""50/50 Split Panel - state B (split family)

Category: split  |  Family: split  |  Exposes: ['panel', 'headline']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_19b', 'category': 'split', 'family': 'split', 'label': '50/50 Split Panel (b)', 'exposes': ['panel', 'headline']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'panel': elem('image', 0, 0, w=620, h=720, c1='#2a1a10', c2='#0a0806'), 'headline': elem('headline', 720, 230, w=460, kicker=c.get('kicker') or c.get('category') or c.get('subtitle') or 'THE FACILITY', text=c.get('text') or c.get('kicker') or c.get('headline') or c.get('quote') or c.get('body') or c.get('label') or 'BUILT IN<br>18 MONTHS', size=64, kicker_size=18)}
