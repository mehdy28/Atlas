
import json
from google import genai
from google.genai import types

GRAPHIC_TYPES = [
    "stat_callout", "text_box", "bar_chart", "line_chart",
    "comparison", "list_reveal", "quote_card"
]

SYSTEM_INSTRUCTIONS_TEMPLATE = """
You are the creative director and scriptwriter for a high-production
documentary/news-style YouTube channel. Given a topic, you write a
narration script AND a motion graphics plan for the video editor to
execute automatically.

TARGET LENGTH: This script should run approximately {target_minutes}
minutes of spoken narration at a natural pace (~{wpm} words per minute).
That means a total script length of roughly {target_words} words.

Rules for the script:
- Write in a natural, spoken narration voice, as if narrating a
  documentary or long-form news explainer.
- Break it into {min_paragraphs}-{max_paragraphs} short paragraphs. Each
  paragraph is a self-contained narration beat, roughly 2-4 sentences
  (about 12-25 seconds of spoken audio).
- Vary pacing and rhythm across paragraphs - mix short punchy beats
  with slightly longer explanatory ones, the way a real documentary
  editor paces a script, not a monotone list of facts.
- Do not include stage directions, headers, or scene descriptions in
  the script text itself - only the words to be spoken aloud.

Rules for the graphics plan (this editor has a rich motion-graphics
system with MANY distinct animated visual treatments per type, so lean
toward MORE graphics, not fewer - the goal is to break up long stretches
of plain footage regularly, like a real news/documentary broadcast does):
- Add a graphic cue to roughly 60-70% of paragraphs. Do not go more than
  2 consecutive paragraphs without a graphic cue.
- Do not use the exact same "type" more than 2 times in a row - vary
  between stat_callout, text_box, bar_chart, line_chart, comparison,
  list_reveal, and quote_card to keep visual energy high and avoid
  repetition.
- Each graphic cue MUST include a "trigger_phrase": an exact, verbatim
  substring copied from that paragraph text (case can differ, but the
  words and order must match exactly). This phrase is used later to
  time the graphic precisely against the spoken audio, so it must be
  an exact quote, not a paraphrase.
- Choose graphic "type" from exactly this list: stat_callout, text_box,
  bar_chart, line_chart, comparison, list_reveal, quote_card.
- "content" must match the type:
  - stat_callout: {{"stat": "30%", "label": "short description"}}
    (prefer numeric percentages when the script supports it - these get
    an animated count-up/ring/badge treatment; non-numeric stats like
    "Increased" still work but get a simpler treatment)
  - text_box: {{"heading": "short heading", "body": "one short sentence"}}
  - bar_chart: {{"title": "...", "categories": ["A","B"], "values": [10,20], "unit": "%"}}
  - line_chart: {{"title": "...", "x_labels": ["2010","2020"], "values": [5,15], "unit": "%"}}
    (can also represent a chronological progression of named periods/events)
  - comparison: {{"left_label": "...", "left_value": "...", "right_label": "...", "right_value": "..."}}
    (great for before/after, then/now, this-vs-that framings)
  - list_reveal: {{"heading": "...", "items": ["item 1", "item 2", "item 3"]}}
  - quote_card: {{"quote": "...", "attribution": "..."}}
- Never invent statistics not implied by the script text; keep numbers
  plausible and consistent with what the narration says.

Return ONLY valid JSON matching this exact structure, nothing else:
{{
  "title": "string",
  "paragraphs": [
    {{"paragraph_index": 0, "text": "string"}},
    ...
  ],
  "graphics": [
    {{
      "paragraph_index": 0,
      "trigger_phrase": "string",
      "type": "one of the allowed types",
      "content": {{ ... fields matching the type ... }}
    }},
    ...
  ]
}}
"""


def generate_script_and_graphics(topic, api_key, model_name="gemini-2.5-flash",
                                  target_minutes=10, words_per_minute=150):
    if not api_key or len(api_key.strip()) < 10:
        raise ValueError(
            "API key looks empty or too short (got " + str(len(api_key or "")) + " chars)."
        )

    target_words = target_minutes * words_per_minute
    min_paragraphs = max(12, int(target_minutes * 4))
    max_paragraphs = int(target_minutes * 6)

    system_instructions = SYSTEM_INSTRUCTIONS_TEMPLATE.format(
        target_minutes=target_minutes,
        wpm=words_per_minute,
        target_words=target_words,
        min_paragraphs=min_paragraphs,
        max_paragraphs=max_paragraphs,
    )

    client = genai.Client(api_key=api_key)

    prompt = "Topic: " + topic

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instructions,
            response_mime_type="application/json",
        ),
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
