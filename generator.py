import datetime
from coach import explain_workout
from profile import save_profile, get_profile


# -----------------------
# WORKOUT BLOCKS (vary by level)
# -----------------------

def strength_block(body_part, level):
    if body_part == "lower":
        if level == "beginner":
            return [
                "Goblet Squat: 3 x 10–12",
                "Leg Press (light): 3 x 10–12",
                "Bodyweight Lunges: 3 x 10 each leg",
                "Plank: 3 x 30s",
            ]
        elif level == "intermediate":
            return [
                "Front Squat: 4 x 6–10 @ RPE 7–8",
                "Leg Press: 3 x 8–12",
                "Walking Lunges: 3 x 8–12 each leg",
                "Core: Plank 3 x 45–60s",
            ]
        elif level == "advanced":
            return [
                "Back Squat: 5 x 5 @ RPE 8–9",
                "Romanian Deadlift: 4 x 6–8",
                "Bulgarian Split Squat: 3 x 8 each leg",
                "Hanging Leg Raise: 3 x 12–15",
            ]
        else:  # elite
            return [
                "Back Squat: 5 x 3–5 @ 85%+ 1RM",
                "Deficit Deadlift: 4 x 4–6",
                "Barbell Walking Lunges: 4 x 6 each leg",
                "Weighted Plank: 4 x 45s",
            ]

    elif body_part == "upper":
        if level == "beginner":
            return [
                "DB Bench Press: 3 x 10–12",
                "Lat Pulldown: 3 x 10–12",
                "DB Shoulder Press: 3 x 10–12",
                "Seated Cable Row: 3 x 10–12",
            ]
        elif level == "intermediate":
            return [
                "Bench Press: 4 x 6–10 @ RPE 7–8",
                "Lat Pulldown: 3 x 8–12",
                "Overhead Press: 3 x 8–12",
                "DB Row: 3 x 8–12",
            ]
        elif level == "advanced":
            return [
                "Bench Press: 5 x 5 @ RPE 8–9",
                "Weighted Pull-ups: 4 x 6–8",
                "Push Press: 4 x 6–8",
                "Pendlay Row: 4 x 6–8",
            ]
        else:  # elite
            return [
                "Bench Press: 5 x 3–5 @ 85%+ 1RM",
                "Strict Pull-ups: 4 x max reps (weighted)",
                "Push Press: 4 x 4–6 @ RPE 9",
                "Barbell Row: 4 x 5–7",
                "Ring Dips: 3 x max reps",
            ]

    else:  # full body
        if level == "beginner":
            return [
                "Goblet Squat: 3 x 10–12",
                "DB Bench Press: 3 x 10–12",
                "Cable Row: 3 x 10–12",
                "Farmer Carry: 3 x 30m",
            ]
        elif level == "intermediate":
            return [
                "Front Squat (moderate): 3 x 8–12",
                "DB Bench: 3 x 8–12",
                "Row Variation: 3 x 8–12",
                "Farmer Carry: 4 x 40m",
            ]
        elif level == "advanced":
            return [
                "Clean & Press: 4 x 5",
                "Front Squat: 4 x 6–8",
                "Weighted Pull-ups: 4 x 6–8",
                "Farmer Carry: 4 x 50m (heavy)",
            ]
        else:  # elite
            return [
                "Power Clean: 5 x 3",
                "Front Squat: 4 x 4–6 @ RPE 9",
                "Strict HSPU: 4 x max reps",
                "Heavy Farmer Carry: 4 x 60m",
            ]

    return []


def engine_block(engine_type, level):
    if engine_type == "short_engine":
        if level == "beginner":
            return [
                "8 min AMRAP (go at your own pace):",
                "  8 cal row or bike",
                "  6 push-ups (knees OK)",
            ]
        elif level == "intermediate":
            return [
                "10 min EMOM:",
                "  10 cal row",
                "  8 push-ups",
            ]
        elif level == "advanced":
            return [
                "12 min EMOM:",
                "  12 cal row",
                "  8 burpees",
            ]
        else:  # elite
            return [
                "15 min EMOM:",
                "  15 cal row",
                "  10 burpees",
                "  5 bar muscle-ups",
            ]

    elif engine_type == "intervals":
        if level == "beginner":
            return [
                "Run/walk 4 x 200m at moderate effort",
                "Rest 2 min between efforts",
            ]
        elif level == "intermediate":
            return [
                "Run 6 x 400m at hard but controlled pace",
                "Rest 90s between efforts",
            ]
        elif level == "advanced":
            return [
                "Run 8 x 400m at 90% effort",
                "Rest 60s between efforts",
            ]
        else:  # elite
            return [
                "Run 10 x 400m at race pace",
                "Rest 45s between efforts",
            ]

    elif engine_type == "conditioning":
        if level == "beginner":
            return [
                "3 rounds (rest as needed):",
                "  200m walk/jog",
                "  8 KB swings (light)",
                "  8 box step-ups",
            ]
        elif level == "intermediate":
            return [
                "4 rounds:",
                "  400m run",
                "  12 KB swings",
                "  10 box step-ups",
            ]
        elif level == "advanced":
            return [
                "5 rounds for time:",
                "  400m run",
                "  15 KB swings (heavy)",
                "  12 box jumps",
                "  10 burpees",
            ]
        else:  # elite
            return [
                "For time:",
                "  1 mile run",
                "  50 KB swings (heavy)",
                "  30 box jumps (24/20)",
                "  20 burpee pull-ups",
            ]

    elif engine_type == "zone2":
        if level == "beginner":
            return [
                "Zone 2 cardio: 25–30 min (walk, bike, or easy jog)",
                "Keep effort conversational — you should be able to talk easily",
            ]
        elif level == "intermediate":
            return [
                "Zone 2 cardio: 35–40 min",
                "Keep pace conversational",
            ]
        elif level == "advanced":
            return [
                "Zone 2 cardio: 45 min",
                "Stay in HR Zone 2 (nasal breathing)",
            ]
        else:  # elite
            return [
                "Zone 2 cardio: 50–60 min",
                "Maintain HR Zone 2, nasal breathing throughout",
            ]

    elif engine_type == "long_zone2":
        if level == "beginner":
            return [
                "Long easy cardio: 35–40 min (walk, bike, or easy jog)",
            ]
        elif level == "intermediate":
            return [
                "Long Zone 2 cardio: 50–55 min",
            ]
        elif level == "advanced":
            return [
                "Long Zone 2 cardio: 60–70 min",
            ]
        else:  # elite
            return [
                "Long Zone 2 cardio: 75–90 min",
            ]

    elif engine_type == "rest":
        if level in ("beginner",):
            return [
                "10–15 min easy walking",
                "Light stretching or yoga",
            ]
        else:
            return [
                "10–20 min walking",
                "Light mobility work",
            ]

    return []


# -----------------------
# WARMUP BY LEVEL
# -----------------------

WARMUPS = {
    "lower": {
        "beginner": "Warm-up: 5 min easy cardio + leg swings & bodyweight squats",
        "intermediate": "Warm-up: 5–8 min cardio + dynamic mobility",
        "advanced": "Warm-up: 8 min cardio + dynamic mobility + activation work",
        "elite": "Warm-up: 10 min progressive cardio + banded activation + warm-up sets",
    },
    "upper": {
        "beginner": "Warm-up: 5 min easy cardio + arm circles & band pull-aparts",
        "intermediate": "Warm-up: 5–8 min cardio + band work",
        "advanced": "Warm-up: 8 min cardio + band work + rotator cuff activation",
        "elite": "Warm-up: 10 min progressive warm-up + banded activation + warm-up sets",
    },
    "full": {
        "beginner": "Warm-up: 5 min easy cardio + full-body dynamic stretches",
        "intermediate": "Warm-up: 6–10 min full-body dynamic",
        "advanced": "Warm-up: 8–10 min progressive warm-up + activation",
        "elite": "Warm-up: 10–12 min full-body dynamic + sport-specific prep",
    },
}


# -----------------------
# WEEK TEMPLATES (by training days)
# -----------------------

def _week_template(days):
    if days <= 3:
        return [
            ("Full Body Strength + Conditioning", "full"),
            ("Rest / Active Recovery", "rest"),
            ("Zone 2 Cardio", "zone2"),
            ("Rest / Active Recovery", "rest"),
            ("Full Body Strength + Short Engine", "full"),
            ("Rest / Active Recovery", "rest"),
            ("Rest / Active Recovery", "rest"),
        ]
    elif days == 4:
        return [
            ("Lower Strength + Short Engine", "lower"),
            ("Zone 2 Cardio", "zone2"),
            ("Rest / Active Recovery", "rest"),
            ("Upper Strength + Intervals", "upper"),
            ("Full Body Conditioning", "full"),
            ("Rest / Active Recovery", "rest"),
            ("Rest / Active Recovery", "rest"),
        ]
    elif days == 5:
        return [
            ("Lower Strength + Short Engine", "lower"),
            ("Zone 2 Cardio", "zone2"),
            ("Upper Strength + Intervals", "upper"),
            ("Rest / Active Recovery", "rest"),
            ("Full Body Strength + Conditioning", "full"),
            ("Long Zone 2 Cardio", "long_zone2"),
            ("Rest / Active Recovery", "rest"),
        ]
    else:  # 6
        return [
            ("Lower Strength + Short Engine", "lower"),
            ("Zone 2 Cardio", "zone2"),
            ("Upper Strength + Intervals", "upper"),
            ("Rest / Active Recovery", "rest"),
            ("Full Body Strength + Conditioning", "full"),
            ("Conditioning", "conditioning"),
            ("Long Zone 2 Cardio", "long_zone2"),
        ]


def build_week(level, days):
    days = max(3, min(6, days))
    template = _week_template(days)
    week = []

    for name, day_type in template:
        details = []

        if day_type == "lower":
            details.append(WARMUPS["lower"].get(level, WARMUPS["lower"]["intermediate"]))
            details.extend(strength_block("lower", level))
            details.extend(engine_block("short_engine", level))

        elif day_type == "upper":
            details.append(WARMUPS["upper"].get(level, WARMUPS["upper"]["intermediate"]))
            details.extend(strength_block("upper", level))
            details.extend(engine_block("intervals", level))

        elif day_type == "full":
            details.append(WARMUPS["full"].get(level, WARMUPS["full"]["intermediate"]))
            details.extend(strength_block("full", level))
            details.extend(engine_block("conditioning", level))

        elif day_type == "zone2":
            details.append("Warm-up: 5 min easy")
            details.extend(engine_block("zone2", level))

        elif day_type == "long_zone2":
            details.append("Warm-up: 8 min easy")
            details.extend(engine_block("long_zone2", level))

        elif day_type == "conditioning":
            details.append(WARMUPS["full"].get(level, WARMUPS["full"]["intermediate"]))
            details.extend(engine_block("conditioning", level))

        else:  # rest
            details.extend(engine_block("rest", level))

        week.append((name, details))

    return week


# -----------------------
# SAVE PLAN TO FILE
# -----------------------

def save_plan_to_file(name, week):
    date = datetime.date.today().isoformat()
    filename = f"plans/{name}_{date}.txt"

    with open(filename, "w") as f:
        f.write(f"Hybrix Weekly Plan for {name} — {date}\n\n")
        for i, (day_name, details) in enumerate(week, start=1):
            f.write(f"Day {i}: {day_name}\n")
            for line in details:
                f.write(f"  - {line}\n")
            f.write("\n")


# -----------------------
# MAIN PROGRAM (CLI)
# -----------------------

def main():
    print("\nWelcome to Hybrix — Hybrid Fitness Generator\n")

    name = input("Enter your name: ").strip()
    existing = get_profile(name)

    if existing:
        print(f"\nWelcome back, {name}!")
        print(f"Saved profile: level={existing['level']}, days={existing['days']}")
        use_saved = input("Use saved profile? (y/n): ").strip().lower()
        if use_saved == "y":
            level = existing["level"]
            days = existing["days"]
        else:
            level = pick_level()
            days = pick_days()
            save_profile(name, level, days)
    else:
        level = pick_level()
        days = pick_days()
        save_profile(name, level, days)

    week = build_week(level, days)
    save_plan_to_file(name, week)

    print("\nYour Hybrix Weekly Plan:\n")
    for i, (day_name, details) in enumerate(week, start=1):
        print(f"Day {i}: {day_name}")
        for line in details:
            print(f"  - {line}")
        print(explain_workout(day_name, details))
        print()


def pick_level():
    while True:
        level = input("Enter your fitness level (beginner/intermediate/advanced): ").strip().lower()
        if level in ["beginner", "intermediate", "advanced"]:
            return level
        print("Invalid input. Please type beginner, intermediate, or advanced.")


def pick_days():
    while True:
        try:
            days = int(input("Training days per week (3–6): ").strip())
            if 3 <= days <= 6:
                return days
        except ValueError:
            pass
        print("Enter a number from 3 to 6.")


if __name__ == "__main__":
    main()
