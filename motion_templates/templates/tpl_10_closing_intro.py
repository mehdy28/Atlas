"""Outro / Closing Card - "intro" template (A->B)

Category: closing  |  Family: closing
All states in one template are, by definition, similar (same family) ->
every internal transition here is morph. When chaining this template to
ANOTHER template in the final sequence: same category/family -> morph,
different category/family -> slide or cut. See docs/TEMPLATES.md.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
sys.path.append(os.path.join(_here, '..', 'states'))
from motion_engine import Sequence
from st_10_closing_a import state as state_a
from st_10_closing_b import state as state_b

META = {
    'id': 'tpl_10_closing_intro',
    'category': 'closing',
    'family': 'closing',
    'states_used': ['st_10a', 'st_10b'],
    'duration_s': 5.40,
}

def build_sequence() -> Sequence:
    return Sequence([
        ('hold', state_a, 0.00, 2.20),
        ('morph', state_a, state_b, 2.20, 3.20),
        ('hold', state_b, 3.20, 5.40),
    ])
