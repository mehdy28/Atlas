import sys
import hashlib
import importlib
import os

TEMPLATES_ROOT = "/content/Atlas/motion_templates"
if TEMPLATES_ROOT + "/engine" not in sys.path:
    sys.path.append(TEMPLATES_ROOT + "/engine")
if TEMPLATES_ROOT + "/templates" not in sys.path:
    sys.path.append(TEMPLATES_ROOT + "/templates")

# Clean semantic mapping to templates with matching visual slots
TYPE_TO_TEMPLATES = {
    # Templates with big headline numbers:
    "stat": ["tpl_02_stat_intro", "tpl_17_takeover_intro"],
    "stat_callout": ["tpl_02_stat_intro", "tpl_17_takeover_intro"],
    
    # Progress percentage:
    "progress": ["tpl_11_progress_intro", "tpl_20_radial_intro"],
    
    # Quotes:
    "quote": ["tpl_04_quote_intro"],
    "quote_card": ["tpl_04_quote_intro"],
    
    # Side-by-side / Before-After:
    "compare": ["tpl_03_compare_intro", "tpl_12_versus_intro"],
    "comparison": ["tpl_03_compare_intro", "tpl_12_versus_intro"],
    
    # Timelines:
    "timeline": ["tpl_05_timeline_intro"],
    
    # Lists & Grids:
    "list": ["tpl_06_list_intro", "tpl_15_grid_intro"],
    "list_reveal": ["tpl_06_list_intro", "tpl_15_grid_intro"],
    
    # Charts:
    "chart": ["tpl_09_chart_intro"],
    "bar_chart": ["tpl_09_chart_intro"],
    "line_chart": ["tpl_09_chart_intro", "tpl_05_timeline_intro"],
    
    # Lower Thirds / Speaker IDs:
    "lowerthird": ["tpl_18_lowerthird_intro"],
    
    # Section Headers & Titles:
    "title": ["tpl_01_title_intro"],
    
    # Definition & Warning callouts:
    "text_box": ["tpl_08_feature_intro", "tpl_13_definition_intro"],
    "warning": ["tpl_14_warning_intro"],
    "badge": ["tpl_21_badge_intro"],
}

def pick_variant(candidates, seed_key):
    h = int(hashlib.md5(str(seed_key).encode()).hexdigest(), 16)
    return candidates[h % len(candidates)]

def select_and_build_sequence(graphic):
    """
    Takes graphic dict: {"type": "...", "content": {...}, ...}
    Returns (sequence, template_meta)
    """
    g_type = graphic.get("type", "stat")
    candidates = TYPE_TO_TEMPLATES.get(g_type, ["tpl_02_stat_intro"])
    seed = graphic.get("trigger_phrase", "") + str(graphic.get("paragraph_index", 0))
    template_name = pick_variant(candidates, seed)

    module = importlib.import_module(template_name)
    content = graphic.get("content", {})

    sequence = module.build_sequence(content=content)
    meta = getattr(module, "META", {"id": template_name})
    return sequence, meta
