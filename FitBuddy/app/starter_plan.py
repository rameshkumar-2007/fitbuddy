FOCUS = {
    "muscle gain": "Practice progressive, balanced strength work with recovery between sessions.",
    "weight loss": "Build a sustainable mix of strength and enjoyable cardio without extreme exercise or dieting.",
    "flexibility": "Practice gentle mobility and balance; never force a stretch or work through pain.",
    "general wellness": "Balance strength, easy cardio, mobility, and rest.",
}

SCHEDULES = {
    "muscle gain": [
        ("Full-body strength A", "Chair squats, incline push-ups, backpack rows, and glute bridges", "strength"),
        ("Easy cardio and mobility", "Walk or cycle", "mixed"),
        ("Upper-body strength", "Incline push-ups, light rows, and wall slides", "strength"),
        ("Recovery", "Rest or take a relaxed walk; keep any mobility gentle", "recovery"),
        ("Lower-body strength", "Sit-to-stands, supported step-ups, calf raises, and hip hinges", "strength"),
        ("Full-body strength B", "Supported reverse lunges, wall push-ups, bird-dogs, and glute bridges", "strength"),
        ("Rest", "Rest; an easy walk is optional", "rest"),
    ],
    "weight loss": [
        ("Comfortable cardio", "Walk, cycle, or dance at a conversational pace", "cardio"),
        ("Full-body strength A", "Chair squats, incline push-ups, rows, and glute bridges", "strength"),
        ("Enjoyable cardio", "Choose a comfortable walk, swim, cycle, or dance", "cardio"),
        ("Mobility and recovery", "Gentle hip, ankle, back, and shoulder mobility", "recovery"),
        ("Full-body strength B", "Sit-to-stands, supported step-ups, wall push-ups, and bird-dogs", "strength"),
        ("Longer comfortable cardio", "Choose a low-impact activity you enjoy and keep the pace conversational", "cardio"),
        ("Rest", "Rest; an easy walk is optional", "rest"),
    ],
    "flexibility": [
        ("Full-body mobility", "Gentle shoulder circles, cat-cow, hip hinges, and ankle rocks", "mobility"),
        ("Balance and light strength", "Supported single-leg balance, sit-to-stands, and bird-dogs", "strength"),
        ("Hip and ankle mobility", "Comfortable hip-flexor, hamstring, and calf mobility; do not force range", "mobility"),
        ("Recovery walk", "Easy walking", "cardio"),
        ("Upper-back and shoulder mobility", "Wall slides, chest opening, and comfortable thoracic rotations", "mobility"),
        ("Gentle full-body flow", "Move slowly through comfortable hip, spine, shoulder, and ankle ranges", "mobility"),
        ("Rest", "Rest; gentle movement is optional", "rest"),
    ],
    "general wellness": [
        ("Full-body strength", "Chair squats, incline push-ups, rows, and glute bridges", "strength"),
        ("Easy cardio", "Walk, cycle, or dance at a conversational pace", "cardio"),
        ("Upper-body strength and posture", "Incline push-ups, light rows, and wall slides", "strength"),
        ("Mobility and recovery", "Gentle hip, ankle, back, and shoulder mobility", "recovery"),
        ("Lower-body strength", "Sit-to-stands, supported reverse lunges, calf raises, and glute bridges", "strength"),
        ("Enjoyable movement", "Choose a comfortable walk, bike ride, swim, or recreational activity", "cardio"),
        ("Rest", "Rest; a relaxed walk is optional", "rest"),
    ],
}

def build_starter_plan(goal, intensity, age):
    goal = goal if goal in SCHEDULES else "general wellness"
    intensity = intensity if intensity in ("low", "medium", "high") else "low"
    if age < 18:
        effort = "2 sets of 8 comfortable repetitions"
        cardio = 20
    else:
        effort = {
            "low": "2 sets of 8 comfortable repetitions",
            "medium": "2 sets of 10 comfortable repetitions",
            "high": "3 sets of 8 controlled repetitions",
        }[intensity]
        cardio = {"low": 20, "medium": 30, "high": 35}[intensity]

    days = []
    for day_number, (title, activities, kind) in enumerate(SCHEDULES[goal], start=1):
        if kind == "rest":
            warmup = "None required."
            main = activities
            cooldown = "Prioritize sleep and regular balanced meals."
        elif kind == "strength":
            warmup = "5 minutes of easy movement and comfortable joint warm-ups."
            main = f"{activities}; {effort} for each exercise. Rest between sets and keep good form."
            cooldown = "Walk easily for 3 minutes and stretch gently."
        elif kind == "mobility":
            warmup = "3-5 minutes of easy walking or marching in place."
            main = f"10-15 minutes: {activities}. Move only through a comfortable range."
            cooldown = "Breathe slowly and stop any movement that causes pain."
        elif kind == "recovery":
            warmup = "3 minutes of comfortable walking."
            main = f"10-15 minutes: {activities}. Keep this session easy."
            cooldown = "Rest, hydrate, and keep movement pain-free."
        elif kind == "mixed":
            warmup = "5 minutes at an easy pace."
            main = f"{activities} for {cardio} minutes at a conversational pace, then 5-10 minutes of gentle shoulder and hip mobility."
            cooldown = "Slow down gradually, drink water, and keep mobility comfortable."
        else:
            warmup = "5 minutes at an easy pace."
            main = f"{activities} for {cardio} minutes at a pace where conversation is comfortable."
            cooldown = "Slow down for 5 minutes and drink water."
        days.append(f"Day {day_number} - {title}\nWarm-up: {warmup}\nMain workout: {main}\nCool-down/recovery: {cooldown}")

    return "\n\n".join([
        "7-Day Starter Plan",
        f"Goal: {goal.title()}\nPreferred intensity: {intensity.title()}\nFocus: {FOCUS[goal]}",
        *days,
        "Safety: Stop if you feel pain, dizziness, or unwell. This starter plan is general wellness guidance, not medical advice.",
    ])


def build_starter_tip(goal, age):
    if age < 18:
        return "Aim for regular balanced meals, water, and enough sleep to support growth and activity. Avoid restrictive diets or weight-loss supplements; ask a trusted adult or health professional about personal nutrition concerns."
    if goal == "muscle gain":
        return "Include a protein-rich food, carbohydrates, and fruits or vegetables in regular meals to support training and recovery. Hydration and sleep matter too; no supplements or calorie targets are needed here."
    if goal == "weight loss":
        return "Choose regular meals with a variety of vegetables or fruit, protein foods, and whole grains. Avoid extreme restriction; consistency, hydration, and sleep support general wellbeing."
    if goal == "flexibility":
        return "Pair gentle mobility with regular meals and water, and give your body time to recover. Ease off any stretch that causes pain."
    return "Build regular meals around a variety of vegetables or fruit, protein foods, and whole grains. Drink water and allow time for sleep and recovery."