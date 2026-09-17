"""Simple Chart Reveal - state C (chart family)

Category: chart  |  Family: chart  |  Exposes: ['chart_axis', 'chart_bars', 'chart_label']
Auto-generated placeholder content - edit freely, keep the element NAMES
stable if you want morphs into/out of this state to keep working.
"""
import sys, os
_here = os.path.dirname(__file__)
sys.path.append(os.path.join(_here, '..', 'engine'))
from motion_engine import elem
META = {'id': 'st_09c', 'category': 'chart', 'family': 'chart', 'label': 'Simple Chart Reveal (c)', 'exposes': ['chart_axis', 'chart_bars', 'chart_label']}

def state(p: float, content: dict=None) -> dict:
    c = content or {}
    "Returns the steady/resting look of this state.\n    p is only meaningful if this state is used as the FIRST state in a\n    template's own Sequence (its own entrance) - every other landing is\n    reached via morph()/slide, which call this at p=1.0.\n    "
    return {'chart_axis': elem('chart_axis', 200, 180, w=880, h=360), 'chart_bars': elem('chart_bars', 200, 180, w=880, h=360, bars=[0.3, 0.55, 0.4, 0.85, 0.6]), 'chart_label': elem('chart_label', 200, 130, text=c.get('text') or c.get('kicker') or c.get('headline') or c.get('quote') or c.get('body') or c.get('label') or 'SPENDING ROSE EVERY QUARTER', size=26)}
