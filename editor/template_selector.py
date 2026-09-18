
import sys
import hashlib
import importlib

TEMPLATES_ROOT = "/content/Atlas/motion_templates"
if TEMPLATES_ROOT + "/engine" not in sys.path:
    sys.path.append(TEMPLATES_ROOT + "/engine")
if TEMPLATES_ROOT + "/templates" not in sys.path:
    sys.path.append(TEMPLATES_ROOT + "/templates")

# Standard family: state()/build_sequence(content=...) driven, Sequence-based.
TYPE_TO_TEMPLATES = {
    "stat_callout": ["tpl_02_stat_intro", "tpl_11_progress_intro", "tpl_21_badge_intro"],
    "text_box": ["tpl_08_feature_intro", "tpl_13_definition_intro", "tpl_18_lowerthird_intro"],
    "bar_chart": ["tpl_09_chart_intro"],
    "line_chart": ["tpl_09_chart_intro", "tpl_05_timeline_intro"],
    "comparison": ["tpl_03_compare_intro", "tpl_12_versus_intro"],
    "list_reveal": ["tpl_06_list_intro", "tpl_15_grid_intro"],
    "quote_card": ["tpl_04_quote_intro"],
}

# Legacy family: render_html(t, duration, **content_kwargs) directly, no
# Sequence/state() wrapper. Different vintage, kept as its own path rather
# than force-fit into the state/build_sequence contract.
LEGACY_TEMPLATES = {
    "comparison": ["tpl_22_stat_split_full"],
    "text_box": ["tpl_24_breaking_ticker", "tpl_25_broadcast_lowerthird"],
}

# Content key mapping: our Gemini content dicts use generic keys
# (heading/body/stat/label/etc.) - legacy templates expect their own
# specific kwarg names. This translates between them per template id.
LEGACY_CONTENT_MAP = {
    "tpl_22_stat_split_full": lambda c: {
        "kicker": c.get("left_label", c.get("kicker", "THE STORY")),
        "number": c.get("right_value", c.get("left_value", c.get("number", ""))),
        "desc": c.get("right_label", c.get("desc", "")),
    },
    "tpl_24_breaking_ticker": lambda c: {
        "text": c.get("body", c.get("heading", "")),
        "badge": "BREAKING",
    },
    "tpl_25_broadcast_lowerthird": lambda c: {
        "name": c.get("heading", ""),
        "title": c.get("body", ""),
    },
}


class LegacySequenceAdapter:
    """
    Wraps a legacy render_html(t, duration, **kwargs) function so it
    exposes the same .duration / .html_at(t) interface the renderer
    expects from a real Sequence object.
    """
    def __init__(self, render_html_fn, duration, kwargs):
        self._render_html_fn = render_html_fn
        self.duration = duration
        self._kwargs = kwargs

    def html_at(self, t):
        return self._render_html_fn(t, duration=self.duration, **self._kwargs)


def pick_variant(candidates, seed_key):
    h = int(hashlib.md5(str(seed_key).encode()).hexdigest(), 16)
    return candidates[h % len(candidates)]


def load_template_module(template_name):
    return importlib.import_module(template_name)


def select_and_build_sequence(graphic):
    g_type = graphic["type"]
    content = graphic.get("content", {})
    seed = graphic.get("trigger_phrase", "") + str(graphic.get("paragraph_index", 0))

    # Combine both pools so legacy templates are genuinely in rotation,
    # not bolted on as an always-second-choice fallback.
    standard_candidates = TYPE_TO_TEMPLATES.get(g_type, [])
    legacy_candidates = LEGACY_TEMPLATES.get(g_type, [])
    all_candidates = [("standard", n) for n in standard_candidates] + [("legacy", n) for n in legacy_candidates]

    if not all_candidates:
        raise ValueError("No template mapping for graphic type: " + g_type)

    kind, template_name = pick_variant(all_candidates, seed)
    module = load_template_module(template_name)

    if kind == "standard":
        try:
            sequence = module.build_sequence(content=content)
        except TypeError:
            sequence = module.build_sequence()
        return sequence, module.META

    # kind == "legacy"
    mapped_kwargs = LEGACY_CONTENT_MAP.get(template_name, lambda c: {})(content)
    duration = module.META.get("duration_s", 5.0)
    sequence = LegacySequenceAdapter(module.render_html, duration, mapped_kwargs)
    return sequence, module.META
