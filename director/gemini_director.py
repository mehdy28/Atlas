
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
You are the lead investigative writer and creative director for a premier US everyday economics YouTube channel (in the style of Vox, Economics Explained, and Johnny Harris).
Given a topic, write ONLY the spoken narration script and footage keywords.

TARGET LENGTH: approximately {target_minutes} minutes of spoken narration at ~{wpm} words per minute (~{target_words} words total).

MANDATORY EVERYDAY ECONOMICS SCRIPT FORMULA:

1. ACT 1: THE TENSION HOOK (Paragraph 0):
   - Start immediately with a tangible, relatable everyday consumer sticker shock (a supermarket receipt, a gas pump total, a rent bill, or credit card statement).
   - Establish the PARADOX: Consumers are paying record-high prices, yet the workers or producers (farmers, line cooks, drivers) are barely breaking even.
   - Ask the central investigative question: "If the people making it aren't seeing this money, where is that extra cash actually going?"

2. ACT 2: THE EVIDENCE & THE TWIST (Middle ~70%):
   - Structure as modular investigative beats ({min_paragraphs}-{max_paragraphs} paragraphs total).
   - For short videos (2m): Follow 1 sharp investigation into the hidden structural bottleneck (e.g. corporate oligopolies, supply chain tollbooths, algorithmic pricing).
   - For long videos (10-20m): Cascade across multiple structural layers (Layer 1: The Raw Materials, Layer 2: The Middlemen Cartel, Layer 3: Wall Street Financialization).
   - Alternate between vivid storytelling and sharp economic math (e.g. "margins surged 300% while input costs only grew 12%").

3. ACT 3: THE BOTTOM LINE (Final 1-2 paragraphs):
   - Reveal who captured the margin and what it means for everyday Americans.
   - End with a lingering, thought-provoking conclusion on why this is the new normal.

RULES:
- Short, punchy, conversational spoken sentences with natural pauses and rhythmic variation.
- No robotic corporate narration. Speak with curiosity, urgency, and precision.
- No headers, timestamps, scene directions, or speaker labels—ONLY words spoken aloud.

Also provide "footage_keywords": 15-25 concrete, visual search phrases (2-4 words each) focusing on real everyday items, store aisles, factory lines, freight, receipts, and workers.

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
You are the motion-graphics director for a high-end YouTube economics documentary.
Below is the finalized narration script, broken into numbered paragraphs.
Your job is ONLY to design the motion graphics plan for it.

Rules for the graphics plan:
- DYNAMIC PACING: In high-retention news documentaries, visual stimuli must occur every 8 to 12 seconds.
  Add 2 to 3 graphic cues per paragraph.
  Freely use "breaking_ticker", "warning", "stat_callout", "comparison", and "text_box".
  Alternate frequently between "layout": "full" (warm brown background takeover) and "layout": "overlay" (transparent lower-third).
- Every graphic MUST specify a "layout":
  * "full": Full-screen takeover with our signature warm brown canvas. Use this whenever explaining deep economic concepts, charts, timelines, or big stat reveals to give visual contrast and cut away from B-roll.
  * "overlay": Transparent lower-third or corner graphic that floats on top of B-roll footage.
- Choose "type" from: stat_callout, text_box, bar_chart, line_chart, comparison, list_reveal, quote_card.
- Each graphic cue MUST include a "trigger_phrase": an exact, verbatim substring copied from that paragraph's text.
- "content" structure:
  - stat_callout: {{"stat": "85%", "label": "Market controlled by 4 firms"}}
  - text_box: {{"heading": "The Bottleneck", "body": "Four processors dictate cattle prices."}}
  - bar_chart: {{"title": "Profit Margin Surge", "categories": ["2019", "2024"], "values": [12, 48], "unit": "%"}}
  - line_chart: {{"title": "Beef Price vs Rancher Pay", "x_labels": ["2019","2021","2024"], "values": [100, 140, 195], "unit": "index"}}
  - comparison: {{"left_label": "Supermarket Price", "left_value": "+54%", "right_label": "Rancher Cut", "right_value": "-8%"}}
  - list_reveal: {{"heading": "The Big 4 Processors", "items": ["Tyson Foods", "JBS", "Cargill", "National Beef"]}}
  - quote_card: {{"quote": "...", "attribution": "..."}}

SCRIPT (numbered paragraphs):
{numbered_script}

Return ONLY valid JSON:
{{
  "graphics": [
    {{
      "paragraph_index": 0,
      "trigger_phrase": "string",
      "type": "stat_callout",
      "layout": "full",
      "content": {{ ... }}
    }},
    ...
  ]
}}
"""

IMAGE_PROMPT_INSTRUCTIONS_TEMPLATE = """
You are a visual director writing prompts for an AI image generator (Stable Diffusion).
You are given a list of narration paragraphs that need custom visual B-roll images.

For each paragraph below, write ONE concise, visually concrete prompt (under 35 words)
describing the specific scene, subjects, and setting.

CRITICAL RULES:
1. SEMANTIC MATCHING: The prompt is used for semantic search matching against the paragraph.
   You MUST directly incorporate the key nouns, context, and subject matter from the paragraph
   (e.g., specific concepts like "beef processing facility shutdown", "drought-stricken cattle pasture", "rising grain and feed costs", "cargo shipping containers at port").
2. NO META FILLER: Do NOT append buzzwords like "photojournalism", "documentary style", "photorealistic",
   or "hyperrealistic". Simply describe the actual visual scene directly.
3. NO VISIBLE TEXT: Avoid text, signs with words, or letters appearing in the image.
4. PARAGRAPH INDEX: In the output JSON, you MUST set "paragraph_index" to the EXACT integer ID
   shown in brackets `[ID]` for that paragraph. Do NOT renumber from 0.

PARAGRAPHS NEEDING GENERATED IMAGES:
{numbered_paragraphs}

Return ONLY valid JSON matching this exact structure:
{{
  "image_prompts": [
    {{"paragraph_index": 2, "prompt": "concrete descriptive prompt using key nouns from paragraph 2"}},
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
