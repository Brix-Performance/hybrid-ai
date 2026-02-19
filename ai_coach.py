import os
import streamlit as st
from openai import OpenAI

BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL = "moonshotai/kimi-k2.5"


def get_api_key():
    """Return the Kimi API key from secrets or env, or None."""
    try:
        return st.secrets["KIMI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("KIMI_API_KEY")


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
    """Send messages to Kimi K2.5 and return the assistant reply."""
    client = OpenAI(base_url=BASE_URL, api_key=api_key, timeout=120.0)
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.6,
        max_tokens=1024,
        extra_body={"thinking": {"type": "disabled"}},
    )
    return response.choices[0].message.content or "No response generated."
