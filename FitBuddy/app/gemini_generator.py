from google import genai
from google.genai import types
from .config import get_settings
from .gemini_client import generate_content_with_retry

SYSTEM_PROMPT = """
You are FitBuddy, a conservative wellness and exercise planning assistant.
Create practical, age-appropriate movement plans. Do not diagnose conditions, prescribe
medication, recommend extreme dieting, fasting, starvation, dehydration, or unsafe exercise.
Never provide calorie targets. Do not shame bodies or promise specific weight changes.
For users under 18, focus on healthy movement, technique, recovery, sleep, hydration,
regular balanced meals, and enjoyment; do not recommend weight-loss dieting.
If pain, dizziness, fainting, chest pain, breathing difficulty, or another concerning
symptom is reported, recommend stopping the relevant activity and getting help from a
parent/guardian and an appropriate healthcare professional.
Return a clearly labeled 7-day plan. Each day must include Focus, Warm-up, Main workout
with exercise and sets/reps or duration, and Cool-down/recovery. Include rest days where appropriate.
"""

def _client():
    key=get_settings().gemini_api_key
    if not key: raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=key)

def generate_workout_gemini(name, age, weight, goal, intensity, language="en-US"):
    s=get_settings()
    prompt=f"""Create a personalized 7-day beginner-friendly wellness workout plan.
Name: {name}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Preferred intensity: {intensity}
Write the entire plan in the language for locale {language}.
Use weight only as profile information. Do not calculate calories, BMI targets, or weight-loss prescriptions.
"""
    with _client() as client:
        r=generate_content_with_retry(client,
            model=s.gemini_workout_model, contents=prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT,temperature=0.6,max_output_tokens=5000))
    text=(r.text or "").strip()
    if not text: raise RuntimeError("Gemini returned an empty workout plan.")
    return text
