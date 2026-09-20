
import json
import time
from google import genai
from google.genai import types
from google.genai import errors as genai_errors

GRAPHIC_TYPES = [
    "stat_callout", "text_box", "bar_chart", "line_chart",
    "comparison", "list_reveal", "quote_card"
]

SCRIPT_INSTRUCTIONS_TEMPLATE = """
You are the senior investigative writer and showrunner for a premier US everyday economics YouTube channel (in the style of Vox, Economics Explained, and Johnny Harris).
Given a topic, write ONLY the spoken narration script and footage keywords.

TARGET LENGTH: approximately {target_minutes} minutes of spoken narration at ~{wpm} words per minute (~{target_words} words total).

MANDATORY SCRIPT STRUCTURE & PACING:
- Break into {min_paragraphs}-{max_paragraphs} punchy paragraphs (each 10 to 18 seconds of spoken audio, ~25-45 words each).
- NEVER write long, slow monologue blocks. Write with rapid rhythm, curiosity, and conversational punch.

ACT 1: THE DRIVE-THRU / STICKER SHOCK (Paragraph 0):
- Start at the point of purchase (the receipt, the drive-thru menu board, the credit card chime).
- Hit the paradox immediately: Consumers are paying sit-down dinner prices for cardboard-wrapped fast food, while franchise owners claim their margins are razor thin.
- Hook question: "If the food is cheaper to produce than ever, where did your $18 actually go?"

ACT 2: THE SYSTEMIC INVESTIGATION (Middle paragraphs):
- Each paragraph uncovers ONE specific structural mechanism:
  * Beat A: The Dollar Menu illusion & commodity costs.
  * Beat B: The Franchise Trap (royalty fees, mandatory software, and corporate landlord rent).
  * Beat C: Dynamic Pricing & App Extraction (how loyalty apps test how much pain your wallet can take).
  * Beat D: Private Equity consolidation & debt servicing.
- Use concrete numbers and vivid contrasts in every beat.

ACT 3: THE VERDICT (Final paragraph):
- Reveal why the $5 combo is dead forever and how fast food quietly pivoted from a volume business to a luxury margin trap.

RULES:
- Pure spoken words only. No headers, timestamps, scene directions, or speaker labels.

Provide "footage_keywords": 20-30 short, concrete phrases (2-3 words) covering both real-world items (drive thru window, digital receipt, frying fries, POS terminal) and economic visuals.

Return ONLY valid JSON:
{{
  "title": "string",
  "footage_keywords": ["string", ...],
  "paragraphs": [
    {{"paragraph_index": 0, "text": "string"}},
    ...
  ]
}}
"""

GRAPHICS_INSTRUCTIONS_TEMPLATE = """
You are the motion-graphics director for a high-retention YouTube economics documentary.
Below is the narration script broken into numbered paragraphs.

CRITICAL PACING RULE:
High-retention documentaries require a visual event (graphic) every 7 to 10 seconds.
You MUST generate 2 to 3 graphic cues per paragraph. Never leave the viewer on plain footage for more than 8 seconds.

LAYOUT MODES:
- "full": FULL-SCREEN TAKEOVER with our warm brown signature canvas. Use this for charts, definitions, timelines, and major stat reveals to cut away from B-roll completely.
- "overlay": Transparent lower-third, corner badge, or crawler that overlays on top of B-roll.

TEMPLATES & TYPES:
- stat_callout: {{"stat": "+140%", "label": "Fast food price surge since 2014"}}
- comparison: {{"left_label": "2019 Combo", "left_value": "$6.49", "right_label": "2024 Combo", "right_value": "$17.89"}}
- bar_chart: {{"title": "Where The $18 Goes", "categories": ["Ingredients", "Labor", "Franchise Rent", "Corporate Profit"], "values": [18, 25, 30, 27], "unit": "%"}}
- line_chart: {{"title": "Price of Big Mac vs Inflation", "x_labels": ["2015","2019","2022","2024"], "values": [3.99, 4.89, 6.20, 8.49], "unit": "$"}}
- text_box: {{"heading": "Dynamic Pricing", "body": "Algorithmic price shifts based on weather and demand."}}
- list_reveal: {{"heading": "The Corporate Royalty Stack", "items": ["4% Royalty Fee", "5% Advertising Fund", "12% Land Lease"]}}

Each graphic cue MUST include a "trigger_phrase": an exact verbatim substring from that paragraph.

SCRIPT:
{numbered_script}

Return ONLY valid JSON:
{{
  "graphics": [
    {{
      "paragraph_index": 0,
      "trigger_phrase": "exact phrase from text",
      "type": "comparison",
      "layout": "full",
      "content": {{ ... }}
    }},
    ...
  ]
}}
"""

IMAGE_PROMPT_INSTRUCTIONS_TEMPLATE = """
You are a conceptual visual director generating prompts for Stable Diffusion.
You are given narration paragraphs that need conceptual, diagrammatic, or macro visuals that stock footage libraries NEVER carry.

FOR EACH PARAGRAPH, write ONE high-concept prompt (under 35 words):
- Examples:
  * "A printed restaurant receipt close-up with dramatic red highlighter marking an 18 dollar total and line items."
  * "An exploded infographic diagram of a fast food paper cup breaking down royalty fees and profit margins."
  * "A dark conceptual map of America glowing with corporate franchise logos and supply chain distribution routes."
  * "A digital mobile app screen wireframe showing algorithmic pricing surge calculations glowing orange."

RULES:
1. SEMANTIC ALIGNMENT: Directly incorporate the key nouns and subject from the paragraph.
2. NO GENERIC BUZZWORDS: Do not write "photorealistic" or "documentary style". Describe the physical scene and lighting directly.
3. PARAGRAPH INDEX: Set "paragraph_index" to the exact integer ID from the bracket `[ID]`.

PARAGRAPHS:
{numbered_paragraphs}

Return ONLY valid JSON:
{{
  "image_prompts": [
    {{"paragraph_index": 0, "prompt": "..."}},
    ...
  ]
}}
"""


def _call_gemini_json(client, model_name, system_instructions, prompt, max_output_tokens,
                       max_retries=5, base_delay=10):
    """
    Retries on 503 (server overloaded) and 429 (rate limited) with
    exponential backoff. max_output_tokens MUST be nested inside
    GenerateContentConfig, not passed as a top-level kwarg.
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instructions,
                    response_mime_type="application/json",
                    max_output_tokens=max_output_tokens,
                ),
            )
            return response.text
        except genai_errors.ServerError as e:
            last_error = e
            delay = base_delay * (2 ** attempt)
            print("Gemini server error (attempt " + str(attempt + 1) + "/" + str(max_retries) +
                  "): " + str(e)[:150] + " - retrying in " + str(delay) + "s...")
            time.sleep(delay)
        except genai_errors.ClientError as e:
            if getattr(e, "code", None) == 429:
                last_error = e
                delay = base_delay * (2 ** attempt)
                print("Gemini rate limited (attempt " + str(attempt + 1) + "/" + str(max_retries) +
                      ") - retrying in " + str(delay) + "s...")
                time.sleep(delay)
            else:
                raise

    raise RuntimeError(
        "Gemini API still unavailable after " + str(max_retries) + " retries. "
        "This is a temporary outage on Google's side - wait a few minutes and try again. "
        "Last error: " + str(last_error)
    )


def _parse_json_with_recovery(client, model_name, system_instructions, prompt, raw_text, max_output_tokens):
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        print("JSON parse failed (" + str(e) + ") - likely response was truncated. Retrying with a larger token budget...")
        raw_text_retry = _call_gemini_json(
            client, model_name, system_instructions, prompt,
            max_output_tokens=min(max_output_tokens * 2, 65536)
        )
        try:
            return json.loads(raw_text_retry)
        except json.JSONDecodeError as e2:
            raise RuntimeError(
                "Gemini response could not be parsed as valid JSON even after retry. "
                "Original error: " + str(e2)
            )


def generate_script_and_graphics(topic, api_key, model_name="gemini-2.5-flash",
                                  target_minutes=10, words_per_minute=150):
    if not api_key or len(api_key.strip()) < 10:
        raise ValueError("API key looks empty or too short (got " + str(len(api_key or "")) + " chars).")

    target_words = target_minutes * words_per_minute
    min_paragraphs = max(12, int(target_minutes * 4))
    max_paragraphs = int(target_minutes * 6)

    script_token_budget = max(8192, int(target_words * 3))
    graphics_token_budget = max(8192, int(max_paragraphs * 200))

    client = genai.Client(api_key=api_key)

    script_instructions = SCRIPT_INSTRUCTIONS_TEMPLATE.format(
        target_minutes=target_minutes, wpm=words_per_minute, target_words=target_words,
        min_paragraphs=min_paragraphs, max_paragraphs=max_paragraphs,
    )
    script_prompt = "Topic: " + topic

    print("Generating script (budget: " + str(script_token_budget) + " tokens)...")
    raw_script = _call_gemini_json(client, model_name, script_instructions, script_prompt, script_token_budget)
    script_data = _parse_json_with_recovery(client, model_name, script_instructions, script_prompt, raw_script, script_token_budget)

    paragraphs = script_data.get("paragraphs", [])
    if not paragraphs:
        raise RuntimeError("Gemini returned no paragraphs for the script call.")

    numbered_script = "\n".join(
        "[" + str(p["paragraph_index"]) + "] " + p["text"]
        for p in sorted(paragraphs, key=lambda x: x["paragraph_index"])
    )
    graphics_instructions = GRAPHICS_INSTRUCTIONS_TEMPLATE.format(numbered_script=numbered_script)
    graphics_prompt = "Design the graphics plan for the script above."

    print("Generating graphics plan (budget: " + str(graphics_token_budget) + " tokens)...")
    raw_graphics = _call_gemini_json(client, model_name, graphics_instructions, graphics_prompt, graphics_token_budget)
    graphics_data = _parse_json_with_recovery(client, model_name, graphics_instructions, graphics_prompt, raw_graphics, graphics_token_budget)

    graphics = graphics_data.get("graphics", [])
    paragraph_lookup = {p["paragraph_index"]: p["text"] for p in paragraphs}

    validated_graphics = []
    dropped = []
    for g in graphics:
        p_idx = g.get("paragraph_index")
        phrase = g.get("trigger_phrase", "")
        paragraph_text = paragraph_lookup.get(p_idx, "")

        if not phrase or phrase.lower() not in paragraph_text.lower():
            dropped.append(g)
            continue
        if g.get("type") not in GRAPHIC_TYPES:
            dropped.append(g)
            continue
        validated_graphics.append(g)

    return {
        "title": script_data.get("title", topic),
        "paragraphs": paragraphs,
        "graphics": validated_graphics,
        "dropped_graphics": dropped,
        "footage_keywords": script_data.get("footage_keywords", []),
    }


def generate_image_prompts_batch(paragraphs_needing_images, api_key, model_name="gemini-2.5-flash"):
    """
    paragraphs_needing_images: list of {"paragraph_index": int, "text": str}
    Returns list of {"paragraph_index": int, "prompt": str}
    """
    if not paragraphs_needing_images:
        return []

    client = genai.Client(api_key=api_key)

    numbered = "\n".join(
        "[" + str(p["paragraph_index"]) + "] " + p["text"]
        for p in paragraphs_needing_images
    )
    instructions = IMAGE_PROMPT_INSTRUCTIONS_TEMPLATE.format(numbered_paragraphs=numbered)
    prompt = "Write the image prompts as specified above."

    token_budget = max(2048, len(paragraphs_needing_images) * 100)

    raw = _call_gemini_json(client, model_name, instructions, prompt, token_budget)
    data = _parse_json_with_recovery(client, model_name, instructions, prompt, raw, token_budget)

    return data.get("image_prompts", [])
