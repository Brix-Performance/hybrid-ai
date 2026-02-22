import datetime
import streamlit as st
from profile import (
    save_profile, get_profile, save_onboarding, is_onboarded,
    log_workout, get_streaks, register_user, authenticate,
    get_current_user, delete_all_users,
)
from generator import build_week, save_plan_to_file
from coach import explain_workout
from ai_coach import get_api_key, build_system_prompt, chat

st.set_page_config(page_title="Hybrix", page_icon="💪", layout="wide")

# ──────────────────────────────────────────
# Global CSS
# ──────────────────────────────────────────
st.markdown("""
<style>
/* ---- chat bubble styles ---- */
.coach-chat-wrap {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    min-height: 60vh;
    padding-bottom: 4.5rem;
}
.user-bubble {
    display: flex; justify-content: flex-end; margin: 0.3rem 0;
}
.user-bubble .bubble-inner {
    background-color: #2563eb; color: #fff;
    padding: 0.6rem 1rem; border-radius: 1rem 1rem 0.25rem 1rem;
    max-width: 80%; overflow-wrap: break-word; line-height: 1.45; font-size: 0.95rem;
}
.coach-bubble {
    display: flex; justify-content: flex-start; margin: 0.3rem 0;
}
.coach-bubble .bubble-inner {
    background-color: #374151; color: #f3f4f6;
    padding: 0.6rem 1rem; border-radius: 1rem 1rem 1rem 0.25rem;
    max-width: 80%; overflow-wrap: break-word; line-height: 1.45; font-size: 0.95rem;
}
.bubble-label {
    font-size: 0.7rem; color: #9ca3af; margin-bottom: 0.1rem;
}
.user-bubble .bubble-label { text-align: right; }
.coach-bubble .bubble-label { text-align: left; }

/* ---- pin chat input to bottom ---- */
[data-testid="stChatInput"] {
    position: fixed !important; bottom: 0 !important;
    left: 0 !important; right: 0 !important;
    z-index: 999; background: var(--background-color, #0e1117);
    padding: 0.5rem 1rem;
}

/* ---- metric cards ---- */
.metric-card {
    background: #1e293b; border-radius: 0.75rem; padding: 1.2rem;
    text-align: center;
}
.metric-card .metric-value {
    font-size: 2rem; font-weight: 700; color: #60a5fa;
}
.metric-card .metric-label {
    font-size: 0.85rem; color: #94a3b8; margin-top: 0.25rem;
}

/* ---- workout card ---- */
.workout-card {
    background: #1e293b; border-radius: 0.75rem; padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
}
.workout-card h4 {
    margin: 0 0 0.5rem 0; color: #f1f5f9;
}
.workout-card li {
    color: #cbd5e1; font-size: 0.9rem; margin-bottom: 0.15rem;
}

/* ---- option buttons for onboarding ---- */
div.stButton > button {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────
# Session-state defaults
# ──────────────────────────────────────────
def _default(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_default("page", "login")            # login | signup | onboarding | home | coach | plan
_default("username", "")
_default("onboard_step", 0)          # 0-4 for the onboarding questions
_default("onboard_answers", {})
_default("onboard_messages", [])     # chat-style message list for onboarding
_default("chat_history", [])
_default("week_plan", None)
_default("user_profile", None)

# ── Auto-login: if a user exists on disk and session is fresh, restore them ──
if st.session_state["page"] == "login" and not st.session_state["username"]:
    saved_user, saved_profile = get_current_user()
    if saved_user and saved_profile and saved_profile.get("onboarding_complete"):
        st.session_state["username"] = saved_user
        st.session_state["page"] = "home"


# ──────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────
def _bubble(role, text):
    label = "You" if role == "user" else "Coach"
    cls = "user-bubble" if role == "user" else "coach-bubble"
    safe = (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace("\n", "<br>"))
    return (f'<div class="{cls}"><div>'
            f'<div class="bubble-label">{label}</div>'
            f'<div class="bubble-inner">{safe}</div>'
            f'</div></div>')


def _get_today_workout(week_plan):
    """Return (day_name, details) for today based on weekday index."""
    if not week_plan:
        return None
    idx = datetime.date.today().weekday()  # 0=Mon … 6=Sun
    if idx < len(week_plan):
        return week_plan[idx]
    return week_plan[0]


def _get_tomorrow_workout(week_plan):
    """Return (day_name, details) for tomorrow."""
    if not week_plan:
        return None
    idx = (datetime.date.today().weekday() + 1) % 7
    if idx < len(week_plan):
        return week_plan[idx]
    return week_plan[0]


def _ensure_plan(name):
    """Load or generate the user's weekly plan into session state."""
    if st.session_state["week_plan"] is not None:
        return
    profile = get_profile(name)
    if not profile:
        return
    level = profile.get("level", "beginner")
    days = profile.get("days", 5)
    week = build_week(level, days)
    save_plan_to_file(name, week)
    st.session_state["week_plan"] = week
    st.session_state["user_profile"] = {
        "name": name, "level": level, "days": days
    }


# ──────────────────────────────────────────
# PAGE: Login
# ──────────────────────────────────────────
def page_login():
    st.markdown("## Welcome to Hybrix 💪")
    st.write("Your personal hybrid training coach.")
    st.write("")

    # Check if an account already exists
    existing_user, _ = get_current_user()

    if existing_user:
        # Account exists — show login form
        st.markdown(f"**Account found:** {existing_user}")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Log in", type="primary"):
            if authenticate(existing_user, password):
                st.session_state["username"] = existing_user
                if is_onboarded(existing_user):
                    _ensure_plan(existing_user)
                    st.session_state["page"] = "home"
                else:
                    st.session_state["onboard_step"] = 0
                    st.session_state["onboard_answers"] = {}
                    st.session_state["onboard_messages"] = []
                    st.session_state["page"] = "onboarding"
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.write("")
        st.caption("Not you?")
        if st.button("Create a new account"):
            st.session_state["page"] = "signup"
            st.rerun()
    else:
        # No account — redirect to signup
        st.session_state["page"] = "signup"
        st.rerun()


# ──────────────────────────────────────────
# PAGE: Sign Up
# ──────────────────────────────────────────
def page_signup():
    st.markdown("## Create your account 💪")
    st.write("Set up your Hybrix profile to get started.")
    st.write("")
    name = st.text_input("Username", key="signup_name")
    password = st.text_input("Password", type="password", key="signup_pw")
    confirm = st.text_input("Confirm password", type="password", key="signup_confirm")

    if st.button("Create account", type="primary"):
        if not name.strip():
            st.error("Please enter a username.")
            return
        if not password:
            st.error("Please enter a password.")
            return
        if password != confirm:
            st.error("Passwords don't match.")
            return

        clean = name.strip()
        # Wipe any existing user and register the new one
        register_user(clean, password)
        st.session_state["username"] = clean
        st.session_state["onboard_step"] = 0
        st.session_state["onboard_answers"] = {}
        st.session_state["onboard_messages"] = []
        st.session_state["page"] = "onboarding"
        st.rerun()

    # If an account already exists, let them go back to login
    existing_user, _ = get_current_user()
    if existing_user:
        st.write("")
        st.caption("Already have an account?")
        if st.button("Back to login"):
            st.session_state["page"] = "login"
            st.rerun()


# ──────────────────────────────────────────
# PAGE: Onboarding Chat
# ──────────────────────────────────────────
ONBOARD_QUESTIONS = [
    {
        "coach_msg": (
            "Hey {name}! I'm your Hybrix AI Coach. "
            "I'm going to ask you a few quick questions so I can build "
            "a training program just for you.\n\n"
            "First — what kind of training are you most interested in?"
        ),
        "key": "training_type",
        "options": ["Hybrid (strength + conditioning)", "Mostly strength", "Mostly cardio/endurance", "General fitness"],
    },
    {
        "coach_msg": (
            "Great choice! Now, what's the main goal for your training? "
            "Are you working toward something specific or just staying fit?"
        ),
        "key": "goal",
        "options": ["Training for a race", "Training for an event/competition", "Hit a specific goal (PR, weight, etc.)", "Generally improving fitness"],
    },
    {
        "coach_msg": (
            "Got it. How many days per week can you commit to training?"
        ),
        "key": "days",
        "options": ["3 days", "4 days", "5 days", "6 days"],
    },
    {
        "coach_msg": (
            "Last question — how long do you want this program to run? "
            "I can build anything from 1 to 8 weeks."
        ),
        "key": "duration_weeks",
        "options": ["2 weeks", "4 weeks", "6 weeks", "8 weeks"],
    },
]


def page_onboarding():
    name = st.session_state["username"]
    step = st.session_state["onboard_step"]
    messages = st.session_state["onboard_messages"]

    st.markdown("## Chat with your Coach")

    # If we just arrived at a new step, add the coach question to messages
    if step < len(ONBOARD_QUESTIONS):
        q = ONBOARD_QUESTIONS[step]
        coach_text = q["coach_msg"].format(name=name)
        # Only add if not already the last coach message
        if not messages or messages[-1].get("content") != coach_text:
            messages.append({"role": "assistant", "content": coach_text})

    # Render all messages
    html = "".join(_bubble(m["role"], m["content"]) for m in messages)
    st.markdown(f'<div class="coach-chat-wrap">{html}</div>', unsafe_allow_html=True)

    # Show options for current step
    if step < len(ONBOARD_QUESTIONS):
        q = ONBOARD_QUESTIONS[step]
        st.write("")
        cols = st.columns(len(q["options"]))
        for i, option in enumerate(q["options"]):
            with cols[i]:
                if st.button(option, key=f"onboard_{step}_{i}"):
                    # Record user answer
                    messages.append({"role": "user", "content": option})

                    # Parse the answer to store
                    key = q["key"]
                    if key == "days":
                        st.session_state["onboard_answers"][key] = int(option.split()[0])
                    elif key == "duration_weeks":
                        st.session_state["onboard_answers"][key] = int(option.split()[0])
                    else:
                        st.session_state["onboard_answers"][key] = option

                    st.session_state["onboard_step"] = step + 1
                    st.rerun()

    # All questions answered — finalize
    if step >= len(ONBOARD_QUESTIONS):
        # Add the completion message if not already there
        done_msg = (
            f"Awesome, {name}! I've got everything I need. "
            "Let me build your personalized training program now..."
        )
        if not messages or messages[-1].get("content") != done_msg:
            messages.append({"role": "assistant", "content": done_msg})

            # Save onboarding
            answers = st.session_state["onboard_answers"]
            save_onboarding(name, answers)

            # Generate plan
            level = "beginner"  # default for new users
            days = answers.get("days", 5)
            week = build_week(level, days)
            save_plan_to_file(name, week)
            st.session_state["week_plan"] = week
            st.session_state["user_profile"] = {
                "name": name, "level": level, "days": days
            }
            st.rerun()

        # Show the final message and a button to go home
        html = "".join(_bubble(m["role"], m["content"]) for m in messages)
        st.markdown(f'<div class="coach-chat-wrap">{html}</div>', unsafe_allow_html=True)

        st.write("")
        if st.button("Go to my Dashboard →", type="primary"):
            st.session_state["page"] = "home"
            st.rerun()


# ──────────────────────────────────────────
# PAGE: Home Dashboard
# ──────────────────────────────────────────
def page_home():
    name = st.session_state["username"]
    profile = get_profile(name)
    _ensure_plan(name)
    week_plan = st.session_state.get("week_plan")

    # ---- Header ----
    st.markdown(f"## Welcome back, {name} 💪")

    # ---- Navigation row ----
    nav_cols = st.columns(4)
    with nav_cols[0]:
        if st.button("🏠 Home"):
            st.session_state["page"] = "home"
            st.rerun()
    with nav_cols[1]:
        if st.button("💬 AI Coach"):
            st.session_state["page"] = "coach"
            st.rerun()
    with nav_cols[2]:
        if st.button("📋 Full Plan"):
            st.session_state["page"] = "plan"
            st.rerun()
    with nav_cols[3]:
        if st.button("🚪 Logout"):
            delete_all_users()
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    st.divider()

    # ---- Profile summary ----
    if profile:
        info_cols = st.columns(4)
        with info_cols[0]:
            st.markdown(f"**Training Type:** {profile.get('training_type', 'Hybrid')}")
        with info_cols[1]:
            st.markdown(f"**Goal:** {profile.get('goal', 'General fitness')}")
        with info_cols[2]:
            st.markdown(f"**Days/week:** {profile.get('days', '—')}")
        with info_cols[3]:
            duration = profile.get('duration_weeks', '—')
            st.markdown(f"**Program:** {duration} weeks")

    st.divider()

    # ---- Streak Metrics ----
    streaks = get_streaks(name)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{streaks["daily_streak"]}</div>'
            f'<div class="metric-label">Day Streak</div>'
            f'</div>', unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{streaks["weekly_streak"]}</div>'
            f'<div class="metric-label">Week Streak</div>'
            f'</div>', unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{streaks["total_workouts"]}</div>'
            f'<div class="metric-label">Total Workouts</div>'
            f'</div>', unsafe_allow_html=True
        )

    st.write("")

    # ---- Today's & Tomorrow's Workout ----
    if week_plan:
        w_today = _get_today_workout(week_plan)
        w_tomorrow = _get_tomorrow_workout(week_plan)

        col_today, col_tomorrow = st.columns(2)

        with col_today:
            st.subheader("Today's Workout")
            if w_today:
                day_name, details = w_today
                st.markdown(f"**{day_name}**")
                for line in details:
                    st.write(f"- {line}")
                st.write("")
                today_str = datetime.date.today().isoformat()
                already_logged = today_str in (profile or {}).get("workouts_completed", [])
                if already_logged:
                    st.success("Completed today!")
                else:
                    if st.button("Mark as Complete ✓", type="primary"):
                        log_workout(name)
                        st.rerun()

        with col_tomorrow:
            st.subheader("Tomorrow's Workout")
            if w_tomorrow:
                day_name, details = w_tomorrow
                st.markdown(f"**{day_name}**")
                for line in details:
                    st.write(f"- {line}")
    else:
        st.info("No plan generated yet. Head to AI Coach to get started!")


# ──────────────────────────────────────────
# PAGE: AI Coach (free chat)
# ──────────────────────────────────────────
def page_coach():
    name = st.session_state["username"]
    _ensure_plan(name)

    # ---- Top nav ----
    cols = st.columns([1, 6])
    with cols[0]:
        if st.button("← Home"):
            st.session_state["page"] = "home"
            st.rerun()
    with cols[1]:
        st.markdown("## AI Coach")

    api_key = get_api_key()
    if not api_key:
        st.warning(
            "AI Coach is not configured yet. Add your Gemini API key "
            "to `.streamlit/secrets.toml`:\n\n"
            '```\nGEMINI_API_KEY = "your-key-here"\n```\n\n'
            "Get a key at https://aistudio.google.com/apikey"
        )
        return

    # Display chat history using native Streamlit chat messages
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask your AI coach anything..."):
        st.session_state["chat_history"].append(
            {"role": "user", "content": prompt}
        )
        with st.chat_message("user"):
            st.markdown(prompt)

        profile = st.session_state.get("user_profile")
        week = st.session_state.get("week_plan")
        system_prompt = build_system_prompt(profile, week)

        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages.extend(st.session_state["chat_history"])

        with st.chat_message("assistant"):
            with st.spinner("Coach is thinking..."):
                try:
                    reply = chat(api_key, api_messages)
                except Exception as e:
                    reply = f"Sorry, I hit an error: {e}"
            st.markdown(reply)

        st.session_state["chat_history"].append(
            {"role": "assistant", "content": reply}
        )


# ──────────────────────────────────────────
# PAGE: Full Plan View
# ──────────────────────────────────────────
def page_plan():
    name = st.session_state["username"]
    _ensure_plan(name)
    week_plan = st.session_state.get("week_plan")

    cols = st.columns([1, 6])
    with cols[0]:
        if st.button("← Home"):
            st.session_state["page"] = "home"
            st.rerun()
    with cols[1]:
        st.markdown("## Your Weekly Plan")

    if week_plan:
        for i, (day_name, details) in enumerate(week_plan, start=1):
            st.subheader(f"Day {i}: {day_name}")
            for line in details:
                st.write(f"- {line}")
            st.write(explain_workout(day_name, details))
    else:
        st.info("No plan generated yet.")


# ──────────────────────────────────────────
# Router
# ──────────────────────────────────────────
page = st.session_state["page"]

if page == "login":
    page_login()
elif page == "signup":
    page_signup()
elif page == "onboarding":
    page_onboarding()
elif page == "home":
    page_home()
elif page == "coach":
    page_coach()
elif page == "plan":
    page_plan()
else:
    page_login()
