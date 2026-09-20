import json
import time
from google import genai
from google.genai import types
from google.genai import errors as genai_errors

STORYBOARD_DIRECTOR_PROMPT = """
You are an award-winning documentary director and visual showrunner (in the style of Vox, Economics Explained, and Johnny Harris).
Your job is to direct a complete, dynamic visual documentary on the given topic.

TARGET DURATION: Approximately {target_minutes} minutes (~{wpm} words per minute, ~{target_words} words total).

DIRECTING PRINCIPLES:
1. NARRATIVE SCRIPT:
   - Break the script into short, punchy paragraphs (each 10 to 18 seconds of narration, ~25-45 words).
   - Conversational, curious, investigative tone. No boring corporate monologues.
   - Structure:
     * Hook (Act 1): A tangible everyday moment (e.g., pulling up to McDonald's, looking at the receipt, sticker shock) + the core paradox.
     * Investigation (Act 2): Modular beats uncovering hidden structural causes (franchise fees, dynamic pricing, private equity debt).
     * The Verdict (Act 3): The ultimate takeaway for everyday consumers.

2. IDEA-BY-IDEA VISUAL STORYBOARD (CRITICAL):
   - DO NOT assign one visual to a whole paragraph.
   - You MUST break EVERY paragraph into 3 to 5 rapid, idea-level visual beats (cuts lasting 2.5 to 4.0 seconds each).
   - BALANCE THE VISUAL RHYTHM across two types:
     * "generated_image": For specific narrative actions, characters, conceptual diagrams, or scenes stock footage won't have (e.g. "A driver staring in shock at an $18 drive-thru screen", "An exploded diagram of a burger showing royalty cuts", "A customer handing a worn credit card through a drive-thru window").
     * "stock_video": For broad atmospheric b-roll that adds real-world motion (e.g. "Fast food neon sign glowing at night", "French fries dropping into boiling oil", "Busy drive-thru traffic queue", "Close-up of burger patties sizzling on flat grill").

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
  "topic": "string",
  "target_duration_seconds": {target_seconds},
  "broad_footage_keywords": ["broad search phrase 1", "broad search phrase 2", ...],
  "paragraphs": [
    {{
      "paragraph_index": 0,
      "text": "spoken narration text...",
      "visual_beats": [
        {{
          "beat_index": 0,
          "action_or_concept": "Customer drives car into fast food parking lot",
          "visual_type": "stock_video",
          "query_or_prompt": "Drive thru lane exterior with cars waiting",
          "duration_est_seconds": 3.0
        }},
        {{
          "beat_index": 1,
          "action_or_concept": "Close-up of driver looking stressed at digital menu board",
          "visual_type": "generated_image",
          "query_or_prompt": "Inside a car, driver looking through open window in disbelief at an illuminated drive-thru menu board glowing 18 dollars",
          "duration_est_seconds": 3.5
        }},
        {{
          "beat_index": 2,
          "action_or_concept": "Food packaging and receipt handoff",
          "visual_type": "generated_image",
          "query_or_prompt": "Macro close-up of a greasy fast-food paper bag and crumpled receipt showing an 18 dollar total",
          "duration_est_seconds": 3.0
        }}
      ],
      "graphics": [
        {{
          "trigger_phrase": "exact phrase from text",
          "type": "stat_callout",
          "layout": "overlay",
          "content": {{"stat": "$18.29", "label": "Average combo price in 2024"}}
        }},
        {{
          "trigger_phrase": "another exact phrase",
          "type": "comparison",
          "layout": "full",
          "content": {{"left_label": "2019 Combo", "left_value": "$6.49", "right_label": "2024 Combo", "right_value": "$18.29"}}
        }}
      ]
    }}
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
            return response.text
        except Exception as e:
            print(f"Gemini call attempt {attempt+1} failed: {e}. Retrying...")
            time.sleep(4)
    raise RuntimeError("Failed to get valid response from Gemini.")

def generate_full_documentary_direction(topic, api_key, model_name="gemini-2.5-flash", target_minutes=2, words_per_minute=150):
    client = genai.Client(api_key=api_key)
    target_words = int(target_minutes * words_per_minute)
    target_seconds = int(target_minutes * 60)
    
    prompt = STORYBOARD_DIRECTOR_PROMPT.format(
        target_minutes=target_minutes,
        wpm=words_per_minute,
        target_words=target_words,
        target_seconds=target_seconds,
    ) + f"\n\nTOPIC TO DIRECT: {topic}"

    print(f"Calling Gemini Director for '{topic}' (~{target_minutes} min)...")
    raw_json = _call_gemini_json(client, model_name, prompt)
    
    # Strip markdown markers if present
    cleaned = raw_json.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
        
    return json.loads(cleaned.strip())
