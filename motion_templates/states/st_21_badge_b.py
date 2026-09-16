"""Corner Badge Expand - state B (badge family)

Category: badge  |  Family: badge  |  Exposes: ['chip', 'detail']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_21b',
    'category': 'badge',
    'family': 'badge',
    'label': 'Corner Badge Expand (b)',
    'exposes': ['chip', 'detail'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "chip": elem('title_chip', 680, 80, label1='UPDATE', label2='', label1_size=30, border_w=8, padding='18px 28px'),
        "detail": elem('subtext', 680, 175, w=480, text='FILED 3 DAYS LATER', size=26, color='#fff'),
    }
