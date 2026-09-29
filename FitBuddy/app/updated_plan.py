from google import genai
from google.genai import types
from .config import get_settings
from .gemini_client import generate_content_with_retry

SYSTEM_PROMPT="""
You update an existing wellness workout plan using feedback. Keep it safe and realistic.
Do not prescribe medical treatment, extreme dieting, fasting, dehydration, or unsafe exercise.
Do not provide calorie targets. For users under 18, do not turn feedback into weight-loss dieting
or body-size targets. If concerning symptoms are mentioned, prioritize stopping the activity and
seeking help from a parent/guardian and an appropriate healthcare professional.
Return a complete revised 7-day plan.
"""

def update_workout_plan(original_plan, feedback, age, goal, intensity, language="en-US"):
    s=get_settings()
    if not s.gemini_api_key: raise RuntimeError("GEMINI_API_KEY is not configured.")
    prompt=f"""Revise this 7-day wellness plan.
Age: {age}; Goal: {goal}; Preferred intensity: {intensity}
Write the entire revised plan in the language for locale {language}.
Original plan:
---BEGIN PLAN---
{original_plan}
---END PLAN---
User feedback:
---BEGIN FEEDBACK---
{feedback}
---END FEEDBACK---
Apply reasonable changes while preserving warm-up, main workout, cool-down/recovery and appropriate rest.
Do not blindly follow feedback that would make exercise unsafe.
"""
    with genai.Client(api_key=s.gemini_api_key) as client:
        r=generate_content_with_retry(client,
            model=s.gemini_workout_model, contents=prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT,temperature=0.6,max_output_tokens=5000))
    text=(r.text or "").strip()
    if not text: raise RuntimeError("Gemini returned an empty revised plan.")
    return text
