"""Lower Third Caption - state C (lowerthird family)

Category: lowerthird  |  Family: lowerthird  |  Exposes: ['bar_bg', 'name_text', 'tag']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem

META = {
    'id': 'st_18c',
    'category': 'lowerthird',
    'family': 'lowerthird',
    'label': 'Lower Third Caption (c)',
    'exposes': ['bar_bg', 'name_text', 'tag'],
}

def state(p: float) -> dict:
    """Returns the steady/resting look of this state.
    p is only meaningful if this state is used as the FIRST state in a
    template's own Sequence (its own entrance) - every other landing is
    reached via morph()/slide, which call this at p=1.0.
    """
    return {
        "bar_bg": elem('caption_panel', 120, 530, w=780, kicker='FORMER VP OF OPERATIONS', text='Daniel Cho', kicker_size=16, text_size=32, padding='24px 34px'),
        "tag": elem('subtext', 154, 662, w=700, text='SPOKE ON CONDITION OF ANONYMITY', size=15, color='#888'),
    }
