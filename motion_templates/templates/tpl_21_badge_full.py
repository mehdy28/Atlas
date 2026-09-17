"""Corner Badge Expand - "full" template (A->B->C)

Category: badge  |  Family: badge
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
from st_21_badge_a import state as state_a
from st_21_badge_b import state as state_b
from st_21_badge_c import state as state_c

META = {
    'id': 'tpl_21_badge_full',
    'category': 'badge',
    'family': 'badge',
    'states_used': ['st_21a', 'st_21b', 'st_21c'],
    'duration_s': 7.80,
}

def build_sequence(content: dict = None) -> Sequence:
    return Sequence([
        ('hold', state_a, 0.00, 2.00),
        ('morph', state_a, state_b, 2.00, 2.90),
        ('hold', state_b, 2.90, 4.90),
        ('morph', state_b, state_c, 4.90, 5.80),
        ('hold', state_c, 5.80, 7.80),
    ], content=content)
