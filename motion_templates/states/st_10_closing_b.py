"""Outro / Closing Card - state B (closing family)

Category: closing  |  Family: closing  |  Exposes: ['logo_chip', 'tagline']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_10b', 'category': 'closing', 'family': 'closing', 'label': 'Outro / Closing Card (b)', 'exposes': ['logo_chip', 'tagline']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'logo_chip': elem('logo_chip', 575, 160, size=76, padding='24px 28px', src=''), 'tagline': elem('subtext', 220, 330, w=840, text=c.get('text') or c.get('kicker') or c.get('headline') or c.get('quote') or c.get('body') or c.get('label') or 'More of this story next episode.', size=38, color='#fff', align='center')}
