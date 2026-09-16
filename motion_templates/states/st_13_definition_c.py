"""Definition / Glossary Card - state C (definition family)

Category: definition  |  Family: definition  |  Exposes: ['term', 'definition_text', 'tag']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_13c',
    'category': 'definition',
    'family': 'definition',
    'label': 'Definition / Glossary Card (c)',
    'exposes': ['term', 'definition_text', 'tag'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "term": elem('headline', 160, 200, w=1000, scale=0.85, kicker='', text='GOLDEN PARACHUTE', size=72, kicker_size=1),
        "definition_text": elem('subtext', 160, 310, w=820, text='A payout guaranteed to executives if they lose their job after a merger or takeover.', size=26, color='#ddd'),
        "tag": elem('subtext', 160, 430, w=600, text='WHY IT MATTERS HERE', size=16, color='#ff6a00'),
    }
