import json
import time
import os
from google import genai
from google.genai import types

STORYBOARD_DIRECTOR_PROMPT = """
You are an award-winning documentary director and visual showrunner (in the style of Vox, Economics Explained, and Johnny Harris).
Your job is to direct a complete, dynamic visual documentary on the given topic.

TARGET DURATION: Approximately {target_minutes} minutes (~{wpm} words per minute, ~{target_words} words total).

DIRECTING PRINCIPLES:
1. NARRATIVE SCRIPT:
   - Break the script into {min_paragraphs}-{max_paragraphs} punchy paragraphs (each 10 to 18 seconds of narration, ~25-45 words).
   - Conversational, curious, investigative tone.
   - Structure:
     * Hook (Act 1): A tangible everyday consumer sticker shock (e.g. drive-thru total, receipt) + the core paradox.
     * Investigation (Act 2): Modular beats uncovering hidden structural causes (franchise fees, dynamic pricing algorithms, private equity debt).
     * The Verdict (Act 3): The ultimate takeaway for everyday consumers.

2. BROAD FOOTAGE KEYWORDS:
   - Provide 25-30 concrete, visual search phrases (2-3 words) for real-world B-roll (e.g. "drive thru lane", "burger on grill", "french fries frying", "credit card terminal", "restaurant cash register").

3. DENSE MOTION GRAPHICS (Every 7 to 10 seconds):
   - Provide 2 to 3 graphic events per paragraph.
   - Alternate between:
     * "layout": "full" (Full-screen takeover using our warm brown gradient canvas for big charts, definitions, comparisons, and math reveals).
     * "layout": "overlay" (Transparent lower-third, ticker crawler, or stat badge that floats over the video/image).
   - Types: stat_callout, comparison, bar_chart, line_chart, text_box, list_reveal, quote_card.
   - Each graphic MUST have a "trigger_phrase" matching an exact substring of that paragraph.

OUTPUT FORMAT:
Return ONLY valid JSON matching this exact structure:
{{
  "title": "string",
  "footage_keywords": ["drive thru window", "frying french fries", "burger patty grill", "credit card machine", ...],
  "paragraphs": [
    {{
      "paragraph_index": 0,
      "text": "spoken narration text...",
      "graphics": [
        {{
          "trigger_phrase": "exact phrase from text",
          "type": "stat_callout",
          "layout": "overlay",
          "content": {{"stat": "$18.29", "label": "Average combo price"}}
        }},
        {{
          "trigger_phrase": "another exact phrase",
          "type": "comparison",
          "layout": "full",
          "content": {{"left_label": "2010 Combo", "left_value": "$5.99", "right_label": "2024 Combo", "right_value": "$18.29"}}
        }}
      ]
    }}
  ]
}}
"""

IMAGE_PROMPT_PROMPT = """
You are a conceptual visual director writing prompts for a 35-step Stable Diffusion generator.
Write ONE high-concept photographic visual prompt (under 35 words) for each paragraph below.
Describe authentic documentary scenes (e.g. close-up of a crumpled fast-food receipt, exploded burger diagram showing fee layers, boardroom with private equity executives, digital menu board with surge pricing).

CRITICAL RULES:
1. SEMANTIC MATCHING: Use the key nouns and subject from the paragraph.
2. NO GENERIC BUZZWORDS: Do not write "photorealistic" or "documentary style". Describe the physical scene and lighting directly.
3. PARAGRAPH INDEX: Set "paragraph_index" to the exact integer ID from the bracket `[ID]`.

PARAGRAPHS:
{numbered_paragraphs}

Return ONLY valid JSON:
{{
  "image_prompts": [
    {{"paragraph_index": 0, "prompt": "..."}}
  ]
}}
"""

def _call_gemini_json(client, model_name, prompt, max_output_tokens=16384):
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    max_output_tokens=max_output_tokens,
                    temperature=0.7,
                ),
            )
            raw = response.text.strip()
            if raw.startswith("```json"): raw = raw[7:]
            if raw.endswith("```"): raw = raw[:-3]
            return json.loads(raw.strip())
        except Exception as e:
            print(f"Gemini call attempt {attempt+1} failed: {e}. Retrying in 4s...")
            time.sleep(4)
    raise RuntimeError("Failed to get valid JSON from Gemini.")

def generate_script_and_graphics(topic, api_key, model_name="gemini-2.5-flash",
                                 target_minutes=2, words_per_minute=150):
    client = genai.Client(api_key=api_key)
    target_words = int(target_minutes * words_per_minute)
    min_paragraphs = max(4, int(target_minutes * 2.5))
    max_paragraphs = max(6, int(target_minutes * 4.0))

    prompt = STORYBOARD_DIRECTOR_PROMPT.format(
        target_minutes=target_minutes,
        wpm=words_per_minute,
        target_words=target_words,
        min_paragraphs=min_paragraphs,
        max_paragraphs=max_paragraphs,
    ) + f"\n\nTOPIC TO DIRECT: {topic}"

    print(f"Calling Gemini Director for '{topic}' (~{target_minutes} min)...")
    data = _call_gemini_json(client, model_name, prompt)

    paragraphs = []
    flattened_graphics = []

    for p in data.get("paragraphs", []):
        p_idx = p["paragraph_index"]
        p_text = p["text"]
        paragraphs.append({"paragraph_index": p_idx, "text": p_text})

        for g in p.get("graphics", []):
            g["paragraph_index"] = p_idx
            flattened_graphics.append(g)

    # Save full storyboard
    os.makedirs("/content/AtlasData/production", exist_ok=True)
    with open("/content/AtlasData/production/directed_storyboard.json", "w") as f:
        json.dump(data, f, indent=2)

    return {
        "title": data.get("title", topic),
        "paragraphs": paragraphs,
        "graphics": flattened_graphics,
        "dropped_graphics": [],
        "footage_keywords": data.get("footage_keywords", [
            "drive thru window", "frying french fries", "burger patty grill", "credit card machine", "fast food receipt"
        ]),
    }

def generate_image_prompts_batch(paragraphs_needing_images, api_key, model_name="gemini-2.5-flash"):
    client = genai.Client(api_key=api_key)
    numbered = "\n".join(f"[{p['paragraph_index']}] {p['text']}" for p in paragraphs_needing_images)
    prompt = IMAGE_PROMPT_PROMPT.format(numbered_paragraphs=numbered)

    data = _call_gemini_json(client, model_name, prompt)
    return data.get("image_prompts", [])
