"""Pull Quote - state C (quote family)

Category: quote  |  Family: quote  |  Exposes: ['quote_text', 'quote_attr', 'accent_line']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_04c',
    'category': 'quote',
    'family': 'quote',
    'label': 'Pull Quote (c)',
    'exposes': ['quote_text', 'quote_attr', 'accent_line'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "quote_text": elem('quote', 220, 200, w=840, text="We didn't expect the cut to land this fast, or this deep.", size=48),
        "accent_line": elem('bar', 140, 180, w=5, h=320),
        "quote_attr": elem('subtext', 220, 420, w=600, text='SENIOR ENGINEER, INTERNAL MEMO', size=18, color='#999'),
    }
