"""Credits Roll - state C (credits family)

Category: credits  |  Family: credits  |  Exposes: ['heading', 'credit_1', 'credit_2']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_16c', 'category': 'credits', 'family': 'credits', 'label': 'Credits Roll (c)', 'exposes': ['heading', 'credit_1', 'credit_2']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'heading': elem('subtext', 180, 160, w=800, text=c.get('text') or c.get('kicker') or c.get('headline') or c.get('quote') or c.get('body') or c.get('label') or 'REPORTING', size=22, color='#ff6a00'), 'credit_1': elem('credit_line', 180, 225, w=750, name=c.get('name') or c.get('author') or c.get('speaker') or 'Jordan Ellis', role=c.get('role') or c.get('title') or c.get('tagline') or 'LEAD RESEARCH', name_size=40, role_size=18), 'credit_2': elem('credit_line', 180, 355, w=750, name=c.get('name') or c.get('author') or c.get('speaker') or 'Priya Nair', role=c.get('role') or c.get('title') or c.get('tagline') or 'DATA VERIFICATION', name_size=40, role_size=18)}
