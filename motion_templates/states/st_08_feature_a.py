"""Image-Led Feature - state A (feature family)

Category: feature  |  Family: feature  |  Exposes: ['image', 'title_chip', 'logo_chip']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_08a', 'category': 'feature', 'family': 'feature', 'label': 'Image-Led Feature (a)', 'exposes': ['image', 'title_chip', 'logo_chip']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'image': elem('image', 230, 139, w=900, h=562, c1='#2a2a2a', c2='#111'), 'title_chip': elem('title_chip', 260, 169, label1=c.get('label1') or c.get('heading') or c.get('title') or c.get('label') or c.get('kicker') or 'THE MEMO', label2=c.get('label2') or c.get('subtitle') or c.get('detail') or c.get('text') or c.get('desc') or 'OBTAINED BY OUR TEAM'), 'logo_chip': elem('logo_chip', 1040, 611, src='')}
