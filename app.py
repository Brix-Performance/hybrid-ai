import streamlit as st
from profile import save_profile, get_profile
from generator import build_week, save_plan_to_file
from coach import explain_workout
from ai_coach import get_api_key, build_system_prompt, chat

st.set_page_config(page_title="Hybrix", page_icon="💪")

st.title("Hybrix 💪")
st.write("Hybrid training plans for general hybrid athletes.")

tab1, tab2 = st.tabs(["Plan Generator", "AI Coach"])

# ---- Tab 1: Plan Generator (existing functionality) ----

with tab1:
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

            st.session_state["week_plan"] = week
            st.session_state["user_profile"] = {
                "name": name, "level": level, "days": days
            }

            st.success("Plan generated + saved to /plans")

            for i, (day_name, details) in enumerate(week, start=1):
                st.subheader(f"Day {i}: {day_name}")
                for line in details:
                    st.write(f"- {line}")
                st.write(explain_workout(day_name, details))

# ---- Tab 2: AI Coach ----

with tab2:
    api_key = get_api_key()

    if not api_key or api_key == "your-nvidia-nim-api-key-here":
        st.warning(
            "AI Coach is not configured yet. To enable it, add your free "
            "NVIDIA NIM API key to `.streamlit/secrets.toml`:\n\n"
            '```\nKIMI_API_KEY = "nvapi-your-key-here"\n```\n\n'
            "Get a free key at https://build.nvidia.com/moonshotai/kimi-k2.5"
        )
    else:
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        # Display existing messages
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input("Ask your AI coach anything..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state["chat_history"].append(
                {"role": "user", "content": prompt}
            )

            # Build messages for API call
            profile = st.session_state.get("user_profile")
            week = st.session_state.get("week_plan")
            system_prompt = build_system_prompt(profile, week)

            api_messages = [{"role": "system", "content": system_prompt}]
            api_messages.extend(st.session_state["chat_history"])

            # Call AI and display response
            with st.chat_message("assistant"):
                with st.spinner("Coach is thinking... (free tier can take up to 2 min)"):
                    try:
                        reply = chat(api_key, api_messages)
                    except Exception as e:
                        reply = f"Sorry, I hit an error: {e}"
                st.markdown(reply)

            st.session_state["chat_history"].append(
                {"role": "assistant", "content": reply}
            )
