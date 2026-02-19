import streamlit as st
from profile import save_profile, get_profile
from generator import build_week, save_plan_to_file
from coach import explain_workout
from ai_coach import get_api_key, build_system_prompt, chat

st.set_page_config(page_title="Hybrix", page_icon="💪", layout="wide")

# ---- Chat UI CSS ----
st.markdown("""
<style>
/* ---------- chat bubble styles ---------- */
.chat-container {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    min-height: 70vh;
    padding-bottom: 1rem;
}
.chat-row {
    display: flex;
    margin: 0.35rem 0;
    max-width: 100%;
}
.chat-row.user {
    justify-content: flex-end;
}
.chat-row.assistant {
    justify-content: flex-start;
}
.chat-bubble {
    padding: 0.65rem 1rem;
    border-radius: 1rem;
    max-width: 70%;
    word-wrap: break-word;
    line-height: 1.45;
    font-size: 0.95rem;
}
.chat-row.user .chat-bubble {
    background-color: #2563eb;
    color: #fff;
    border-bottom-right-radius: 0.25rem;
}
.chat-row.assistant .chat-bubble {
    background-color: #374151;
    color: #f3f4f6;
    border-bottom-left-radius: 0.25rem;
}
.chat-label {
    font-size: 0.7rem;
    color: #9ca3af;
    margin-bottom: 0.15rem;
}
.chat-row.user .chat-label {
    text-align: right;
}

/* ---------- pin the chat input to the bottom ---------- */
section[data-testid="stTabs"] [data-testid="stChatInput"] {
    position: fixed;
    bottom: 0;
    z-index: 100;
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

        def _render_bubble(role, text):
            """Return HTML for a single chat bubble."""
            label = "You" if role == "user" else "Coach"
            safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            return (
                f'<div class="chat-row {role}">'
                f'  <div>'
                f'    <div class="chat-label">{label}</div>'
                f'    <div class="chat-bubble">{safe}</div>'
                f'  </div>'
                f'</div>'
            )

        # Build the full chat HTML (messages grow upward from bottom)
        bubbles_html = ""
        for msg in st.session_state["chat_history"]:
            bubbles_html += _render_bubble(msg["role"], msg["content"])

        st.markdown(
            f'<div class="chat-container">{bubbles_html}</div>',
            unsafe_allow_html=True,
        )

        # Chat input (Streamlit pins this at bottom via our CSS)
        if prompt := st.chat_input("Ask your AI coach anything..."):
            st.session_state["chat_history"].append(
                {"role": "user", "content": prompt}
            )

            # Build messages for API call
            profile = st.session_state.get("user_profile")
            week = st.session_state.get("week_plan")
            system_prompt = build_system_prompt(profile, week)

            api_messages = [{"role": "system", "content": system_prompt}]
            api_messages.extend(st.session_state["chat_history"])

            # Call AI and get response
            with st.spinner("Coach is thinking..."):
                try:
                    reply = chat(api_key, api_messages)
                except Exception as e:
                    reply = f"Sorry, I hit an error: {e}"

            st.session_state["chat_history"].append(
                {"role": "assistant", "content": reply}
            )
            st.rerun()
