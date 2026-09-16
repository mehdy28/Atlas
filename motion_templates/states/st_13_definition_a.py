"""Definition / Glossary Card - state A (definition family)

Category: definition  |  Family: definition  |  Exposes: ['term']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_13a',
    'category': 'definition',
    'family': 'definition',
    'label': 'Definition / Glossary Card (a)',
    'exposes': ['term'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "term": elem('headline', 160, 200, w=1000, kicker='', text='GOLDEN PARACHUTE', size=72, kicker_size=1),
    }
