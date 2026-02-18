import streamlit as st
from profile import save_profile, get_profile
from generator import build_week, save_plan_to_file
from coach import explain_workout

st.set_page_config(page_title="Hybrix", page_icon="💪")

st.title("Hybrix 💪")
st.write("Hybrid training plans for general hybrid athletes.")

name = st.text_input("Name", value="")

col1, col2 = st.columns(2)

with col1:
    level = st.selectbox("Fitness level", ["beginner", "intermediate", "advanced"])
with col2:
    days = st.selectbox("Training days per week", [3, 4, 5, 6], index=2)

if name:
    existing = get_profile(name)
    if existing:
        st.info(f"Saved profile found: level={existing['level']}, days={existing['days']}")

use_saved = st.checkbox("Use saved profile (if available)", value=True)

if st.button("Generate Weekly Plan"):
    if not name.strip():
        st.error("Enter a name first.")
    else:
        if use_saved and get_profile(name):
            prof = get_profile(name)
            level = prof["level"]
            days = prof["days"]
        else:
            save_profile(name, level, days)

        week = build_week(level, days)
        save_plan_to_file(name, week)

        st.success("Plan generated + saved to /plans")

        for i, (day_name, details) in enumerate(week, start=1):
            st.subheader(f"Day {i}: {day_name}")
            for line in details:
                st.write(f"- {line}")
            st.write(explain_workout(day_name, details))
