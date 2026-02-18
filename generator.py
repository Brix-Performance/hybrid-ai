import random
import datetime
from coach import explain_workout
from profile import save_profile, get_profile


# -----------------------
# INPUT FUNCTIONS
# -----------------------

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


# -----------------------
# WORKOUT BLOCKS
# -----------------------

def strength_block(type, level):

    if type == "lower":
        return [
            "Front Squat: 4 x 6–10 @ RPE 7–8",
            "Leg Press: 3 x 8–12",
            "Walking Lunges: 3 x 8–12",
            "Core: Plank 3 x 45–60s"
        ]

    if type == "upper":
        return [
            "Bench Press: 4 x 6–10 @ RPE 7–8",
            "Lat Pulldown: 3 x 8–12",
            "Overhead Press: 3 x 8–12",
            "DB Row: 3 x 8–12"
        ]

    if type == "full":
        return [
            "Front Squat (moderate): 3 x 8–12",
            "DB Bench: 3 x 8–12",
            "Row Variation: 3 x 8–12",
            "Farmer Carry: 4 x 40m"
        ]

    return []


def engine_block(type, level):

    if type == "short_engine":
        return [
            "10 min EMOM:",
            "10 cal row",
            "8 pushups"
        ]

    if type == "intervals":
        return [
            "Run 6 x 400m hard but controlled",
            "Rest 90 seconds between efforts"
        ]

    if type == "conditioning":
        return [
            "4 rounds:",
            "400m run",
            "12 KB swings",
            "10 box step-ups"
        ]

    if type == "zone2":
        return [
            "Zone 2 cardio 40 minutes",
            "Keep pace conversational"
        ]

    if type == "long_zone2":
        return [
            "Long Zone 2 cardio 55 minutes"
        ]

    if type == "rest":
        return [
            "10–20 min walking",
            "Light mobility"
        ]

    return []


# -----------------------
# WEEK STRUCTURE
# -----------------------

DAY_TEMPLATES = [

    ("Lower Strength + Short Engine", "lower"),
    ("Zone 2 Cardio", "zone2"),
    ("Upper Strength + Intervals", "upper"),
    ("Rest / Mobility", "rest"),
    ("Full Body Strength + Conditioning", "full"),
    ("Long Zone 2 Cardio", "long_zone2"),
    ("Rest", "rest")

]


def build_week(level, days):

    week = []

    for name, type in DAY_TEMPLATES:

        details = []

        if type == "lower":

            details.append("Warm-up: 5–8 min cardio + dynamic mobility")

            details.extend(strength_block("lower", level))

            details.extend(engine_block("short_engine", level))

        elif type == "upper":

            details.append("Warm-up: 5–8 min cardio + band work")

            details.extend(strength_block("upper", level))

            details.extend(engine_block("intervals", level))

        elif type == "full":

            details.append("Warm-up: 6–10 min full-body dynamic")

            details.extend(strength_block("full", level))

            details.extend(engine_block("conditioning", level))

        elif type == "zone2":

            details.append("Warm-up: 5 min easy")

            details.extend(engine_block("zone2", level))

        elif type == "long_zone2":

            details.append("Warm-up: 8 min easy")

            details.extend(engine_block("long_zone2", level))

        else:

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

    print(f"\nPlan saved to {filename}\n")


# -----------------------
# MAIN PROGRAM
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


# -----------------------

if __name__ == "__main__":

    main()
