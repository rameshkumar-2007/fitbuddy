from google import genai
from google.genai import types
from .config import get_settings
from .gemini_client import generate_content_with_retry

def generate_nutrition_tip_with_flash(goal, age, language="en-US"):
    s=get_settings()
    if not s.gemini_api_key: raise RuntimeError("GEMINI_API_KEY is not configured.")
    if age < 18:
        rule="The user is under 18. Give a short healthy-food/recovery suggestion. Do not discuss calorie restriction, fasting, supplements, weight-loss diets, or body-size targets. Encourage regular balanced meals, hydration and sleep."
    else:
        rule="Give general wellness nutrition/recovery advice. Do not prescribe calorie targets or supplements."
    prompt=f"Give one concise practical nutrition or recovery tip for the fitness goal: {goal}. {rule} Write in the language for locale {language}. Keep it to 2-4 sentences and avoid medical claims."
    with genai.Client(api_key=s.gemini_api_key) as client:
        r=generate_content_with_retry(client,
            model=s.gemini_tip_model, contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4,max_output_tokens=300))
    text=(r.text or "").strip()
    if not text: raise RuntimeError("Gemini returned an empty nutrition tip.")
    return text
