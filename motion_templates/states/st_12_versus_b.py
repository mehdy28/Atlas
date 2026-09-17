"""Versus / Split Comparison - state B (versus family)

Category: versus  |  Family: versus  |  Exposes: ['side_left', 'side_right', 'divider']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_12b', 'category': 'versus', 'family': 'versus', 'label': 'Versus / Split Comparison (b)', 'exposes': ['side_left', 'side_right', 'divider']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'side_left': elem('headline', 220, 240, w=360, kicker=c.get('kicker') or c.get('category') or c.get('subtitle') or '', text=c.get('text') or c.get('kicker') or c.get('headline') or c.get('quote') or c.get('body') or c.get('label') or 'BEFORE', size=76, kicker_size=1), 'divider': elem('bar', 637, 180, w=3, h=280), 'side_right': elem('headline', 700, 240, w=360, kicker=c.get('kicker') or c.get('category') or c.get('subtitle') or '', text=c.get('text') or c.get('kicker') or c.get('headline') or c.get('quote') or c.get('body') or c.get('label') or 'AFTER', size=76, kicker_size=1)}
