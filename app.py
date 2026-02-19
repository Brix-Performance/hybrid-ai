import streamlit as st
from profile import save_profile, get_profile
from generator import build_week, save_plan_to_file
from coach import explain_workout
from ai_coach import get_api_key, build_system_prompt, chat

st.set_page_config(page_title="Hybrix", page_icon="💪")

# ---- Chat UI CSS ----
st.markdown("""
<style>
/* ---- wrapper: push messages to the bottom ---- */
.coach-chat-wrap {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    min-height: 70vh;
    padding-bottom: 4.5rem;          /* room for the fixed input bar */
}

/* ---- user messages: right-aligned, blue ---- */
.user-bubble {
    display: flex;
    justify-content: flex-end;
    margin: 0.3rem 0;
}
.user-bubble .bubble-inner {
    background-color: #2563eb;
    color: #ffffff;
    padding: 0.6rem 1rem;
    border-radius: 1rem 1rem 0.25rem 1rem;
    max-width: 90%;
    overflow-wrap: break-word;
    word-break: normal;
    line-height: 1.45;
    font-size: 0.95rem;
}

/* ---- coach messages: left-aligned, gray ---- */
.coach-bubble {
    display: flex;
    justify-content: flex-start;
    margin: 0.3rem 0;
}
.coach-bubble .bubble-inner {
    background-color: #374151;
    color: #f3f4f6;
    padding: 0.6rem 1rem;
    border-radius: 1rem 1rem 1rem 0.25rem;
    max-width: 90%;
    overflow-wrap: break-word;
    word-break: normal;
    line-height: 1.45;
    font-size: 0.95rem;
}

.bubble-label {
    font-size: 0.7rem;
    color: #9ca3af;
    margin-bottom: 0.1rem;
}
.user-bubble .bubble-label { text-align: right; }
.coach-bubble .bubble-label { text-align: left; }

/* ---- pin chat input to the bottom ---- */
[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 999;
    background: var(--background-color, #0e1117);
    padding: 0.5rem 1rem;
}
</style>
""", unsafe_allow_html=True)

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

        # --- render each message as its own HTML bubble ---
        st.markdown('<div class="coach-chat-wrap">', unsafe_allow_html=True)

        for msg in st.session_state["chat_history"]:
            safe = (msg["content"]
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", "<br>"))
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="user-bubble">'
                    f'  <div><div class="bubble-label">You</div>'
                    f'  <div class="bubble-inner">{safe}</div></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="coach-bubble">'
                    f'  <div><div class="bubble-label">Coach</div>'
                    f'  <div class="bubble-inner">{safe}</div></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('</div>', unsafe_allow_html=True)

        # --- chat input (pinned to bottom via CSS) ---
        if prompt := st.chat_input("Ask your AI coach anything..."):
            st.session_state["chat_history"].append(
                {"role": "user", "content": prompt}
            )

            # Show the user bubble immediately so it's visible during the API call
            safe_prompt = (prompt
                           .replace("&", "&amp;")
                           .replace("<", "&lt;")
                           .replace(">", "&gt;")
                           .replace("\n", "<br>"))
            st.markdown(
                f'<div class="user-bubble">'
                f'  <div><div class="bubble-label">You</div>'
                f'  <div class="bubble-inner">{safe_prompt}</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            profile = st.session_state.get("user_profile")
            week = st.session_state.get("week_plan")
            system_prompt = build_system_prompt(profile, week)

            api_messages = [{"role": "system", "content": system_prompt}]
            api_messages.extend(st.session_state["chat_history"])

            with st.spinner("Coach is thinking..."):
                try:
                    reply = chat(api_key, api_messages)
                except Exception as e:
                    reply = f"Sorry, I hit an error: {e}"

            st.session_state["chat_history"].append(
                {"role": "assistant", "content": reply}
            )
            st.rerun()
