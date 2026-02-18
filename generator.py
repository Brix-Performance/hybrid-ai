import random

def generate_workout(level="intermediate"):
    
    lower_body = [
        "Back Squat 4x6-10",
        "Romanian Deadlift 3x8-12",
        "Walking Lunges 3x12",
        "Leg Press 3x10"
    ]
    
    upper_body = [
        "Bench Press 4x6-10",
        "Pullups or Lat Pulldown 4x6-12",
        "Shoulder Press 3x8-12",
        "Dumbbell Rows 3x10"
    ]
    
    conditioning = [
        "Run 10 minutes moderate pace",
        "Bike 12 minutes steady",
        "Row 2000 meters",
        "Stair machine 10 minutes"
    ]
    
    interval_counts = {
        "beginner": 4,
        "intermediate": 6,
        "advanced": 8
    }
    
    intervals = f"Run {interval_counts[level]} x 400m, rest 90 sec"
    
    workout = {
        "Lower Body Day": random.sample(lower_body, 3) + [random.choice(conditioning)],
        "Upper Body Day": random.sample(upper_body, 3) + [intervals],
        "Cardio Day": [f"Zone 2 cardio for {30 if level=='beginner' else 45 if level=='intermediate' else 60} minutes"]
    }
    
    return workout


if __name__ == "__main__":
    
    plan = generate_workout("intermediate")
    
    print("\nYour Hybrid Workout Plan:\n")
    
    for day, exercises in plan.items():
        print(day)
        for exercise in exercises:
            print("-", exercise)
        print()
