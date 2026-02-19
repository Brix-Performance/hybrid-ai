import os
import streamlit as st
import google.generativeai as genai

MODEL = "gemini-2.0-flash"


def get_api_key():
    """Return the Gemini API key from secrets or env, or None."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("GEMINI_API_KEY")


def build_system_prompt(profile=None, week_plan=None):
    """Build the system message for the AI coach."""
    prompt = (
        "You are the Hybrix AI Coach, an expert hybrid fitness coach. "
        "Hybrid training blends strength training (squat, bench, deadlift "
        "variations), conditioning (EMOMs, AMRAPs, interval work), and "
        "aerobic base building (Zone 2 cardio). You give concise, practical "
        "advice about workouts, exercise form, programming, recovery, and "
        "nutrition for hybrid athletes. Keep answers focused and under 200 "
        "words unless the user asks for more detail."
    )

    if profile:
        prompt += (
            f"\n\nCurrent user: {profile['name']}, "
            f"fitness level: {profile['level']}, "
            f"training {profile['days']} days per week."
        )

    if week_plan:
        prompt += "\n\nTheir current weekly plan:\n"
        for i, (day_name, details) in enumerate(week_plan, start=1):
            prompt += f"\nDay {i}: {day_name}\n"
            for line in details:
                prompt += f"  - {line}\n"
    elif not profile:
        prompt += (
            "\n\nNo plan has been generated yet. If the user asks about "
            "their plan, encourage them to go to the Plan Generator tab first."
        )

    return prompt


def chat(api_key, messages):
    """Send messages to Gemini and return the assistant reply."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=next(
            (m["content"] for m in messages if m["role"] == "system"), None
        ),
    )

    # Convert messages to Gemini format (skip the system message)
    history = []
    for m in messages:
        if m["role"] == "system":
            continue
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})

    # The last message is the current user turn
    current = history.pop()
    chat_session = model.start_chat(history=history)
    response = chat_session.send_message(current["parts"])
    return response.text or "No response generated."
