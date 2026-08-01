
import json
import google.generativeai as genai

GRAPHIC_TYPES = [
    "stat_callout", "text_box", "bar_chart", "line_chart",
    "comparison", "list_reveal", "quote_card"
]

SYSTEM_INSTRUCTIONS = """
You are the creative director and scriptwriter for a documentary-style
YouTube channel. Given a topic, you write a narration script AND a
motion graphics plan for the video editor to execute automatically.

Rules for the script:
- Write in a natural, spoken narration voice, as if narrating a documentary.
- Break it into 12-22 short paragraphs. Each paragraph is a self-contained
  narration beat, roughly 2-4 sentences.
- Do not include stage directions, headers, or scene descriptions in the
  script text itself - only the words to be spoken aloud.

Rules for the graphics plan:
- For roughly HALF of the paragraphs, add one motion graphic cue that
  visually reinforces a specific fact, number, or claim in that paragraph.
- Each graphic cue MUST include a "trigger_phrase": an exact, verbatim
  substring copied from that paragraph's text (case can differ, but the
  words and order must match exactly). This phrase is used later to time
  the graphic precisely against the spoken audio, so it must be an exact
  quote, not a paraphrase.
- Choose graphic "type" from exactly this list: stat_callout, text_box,
  bar_chart, line_chart, comparison, list_reveal, quote_card.
- "content" must match the type:
  - stat_callout: {"stat": "30%", "label": "short description"}
  - text_box: {"heading": "short heading", "body": "one short sentence"}
  - bar_chart: {"title": "...", "categories": ["A","B"], "values": [10,20], "unit": "%"}
  - line_chart: {"title": "...", "x_labels": ["2010","2020"], "values": [5,15], "unit": "%"}
  - comparison: {"left_label": "...", "left_value": "...", "right_label": "...", "right_value": "..."}
  - list_reveal: {"heading": "...", "items": ["item 1", "item 2", "item 3"]}
  - quote_card: {"quote": "...", "attribution": "..."}
- Do not put a graphic on every paragraph - only where it genuinely adds value.
- Never invent statistics not implied by the script text; keep numbers
  plausible and consistent with what the narration says.

Return ONLY valid JSON matching this exact structure, nothing else:
{
  "title": "string",
  "paragraphs": [
    {"paragraph_index": 0, "text": "string"},
    ...
  ],
  "graphics": [
    {
      "paragraph_index": 0,
      "trigger_phrase": "string",
      "type": "one of the allowed types",
      "content": { ... fields matching the type ... }
    },
    ...
  ]
}
"""


def generate_script_and_graphics(topic, api_key, model_name="gemini-2.5-flash"):
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_INSTRUCTIONS,
    )

    prompt = "Topic: " + topic

    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )

    raw_text = response.text
    data = json.loads(raw_text)

    paragraphs = data.get("paragraphs", [])
    graphics = data.get("graphics", [])

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
        "title": data.get("title", topic),
        "paragraphs": paragraphs,
        "graphics": validated_graphics,
        "dropped_graphics": dropped,
    }
