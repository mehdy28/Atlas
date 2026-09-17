"""Definition / Glossary Card - state B (definition family)

Category: definition  |  Family: definition  |  Exposes: ['term', 'definition_text']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_13b', 'category': 'definition', 'family': 'definition', 'label': 'Definition / Glossary Card (b)', 'exposes': ['term', 'definition_text']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'term': elem('headline', 160, 200, w=1000, scale=0.85, kicker=c.get('kicker') or c.get('category') or c.get('subtitle') or '', text=c.get('text') or c.get('kicker') or c.get('headline') or c.get('quote') or c.get('body') or c.get('label') or 'GOLDEN PARACHUTE', size=72, kicker_size=1), 'definition_text': elem('subtext', 160, 310, w=820, text=c.get('text') or c.get('kicker') or c.get('headline') or c.get('quote') or c.get('body') or c.get('label') or 'A payout guaranteed to executives if they lose their job after a merger or takeover.', size=26, color='#ddd')}
