def explain_workout(day_name, exercises):

    explanation = f"\nCoach Notes for {day_name}:\n"

    if "Strength" in day_name:
        explanation += "- Focus on controlled reps and proper form.\n"
        explanation += "- Leave 1–3 reps in reserve on each set.\n"

    if "Zone 2" in day_name:
        explanation += "- Keep heart rate conversational.\n"
        explanation += "- This builds aerobic base and recovery.\n"

    if "Intervals" in day_name:
        explanation += "- Push hard but stay consistent.\n"
        explanation += "- This improves VO2 max and speed.\n"

    if "Conditioning" in day_name:
        explanation += "- Maintain steady effort.\n"
        explanation += "- Focus on breathing and pacing.\n"

    return explanation
