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
    level = profile.get("level", "intermediate")
    days = profile.get("days", 5)
    display_name = profile.get("display_name", name)
    week = build_week(level, days)
    save_plan_to_file(name, week)
    st.session_state["week_plan"] = week
    st.session_state["user_profile"] = {
        "name": display_name, "level": level, "days": days
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

# Map fitness-level answers → generator level
FITNESS_LEVEL_MAP = {
    "Just getting started": "beginner",
    "Lightly active": "beginner",
    "Moderately fit": "intermediate",
    "Well-trained": "advanced",
    "Competitive athlete": "elite",
}

# Map current-training answers → int (informational only)
CURRENT_DAYS_MAP = {
    "I don't really train right now": 0,
    "1–2 days": 2,
    "3–4 days": 4,
    "5–6 days": 5,
    "Every day": 7,
}

# Map target-days answers → int (used for plan generation)
TARGET_DAYS_MAP = {
    "3 days": 3,
    "4 days": 4,
    "5 days": 5,
    "6 days": 6,
}

ONBOARD_QUESTIONS = [
    {
        "coach_msg": (
            "Hey there! I'm your Hybrix AI coach. "
            "I'm going to ask a few quick questions so I can build "
            "a training program tailored to you.\n\n"
            "First — what should I call you?"
        ),
        "key": "display_name",
        "input_type": "text",
        "placeholder": "Enter your name...",
        "options": [],
    },
    {
        "coach_msg": (
            "Nice to meet you, {display_name}! "
            "How many days per week do you currently train?"
        ),
        "key": "current_days",
        "input_type": "buttons_and_text",
        "options": [
            "I don't really train right now",
            "1–2 days",
            "3–4 days",
            "5–6 days",
            "Every day",
        ],
        "placeholder": "Or type your own answer...",
    },
    {
        "coach_msg": (
            "Got it. How would you describe your "
            "current fitness level?"
        ),
        "key": "fitness_level",
        "input_type": "buttons_and_text",
        "options": [
            "Just getting started",
            "Lightly active",
            "Moderately fit",
            "Well-trained",
            "Competitive athlete",
        ],
        "option_descriptions": [
            "New to exercise or haven't trained regularly",
            "Walk or do light workouts a couple times a week",
            "Train regularly but without a structured program",
            "Follow a structured plan with consistent performance",
            "Professional, collegiate, or competitive sports background",
        ],
        "placeholder": "Or describe it in your own words...",
    },
    {
        "coach_msg": (
            "Now let's talk about your goals. "
            "How many days per week do you want to train on this program?"
        ),
        "key": "target_days",
        "input_type": "buttons_and_text",
        "options": [
            "3 days",
            "4 days",
            "5 days",
            "6 days",
        ],
        "placeholder": "Or type a number...",
    },
    {
        "coach_msg": (
            "What's your main goal for training?"
        ),
        "key": "goal",
        "input_type": "buttons_and_text",
        "options": [
            "Lose weight / get leaner",
            "Build muscle / get stronger",
            "Improve endurance / cardio",
            "Train for a specific event or competition",
            "General health and fitness",
        ],
        "placeholder": "Or describe your goal...",
    },
    {
        "coach_msg": (
            "Last one — how many weeks do you want this program to run? "
            "I can build anything from 1 to 8 weeks."
        ),
        "key": "duration_weeks",
        "input_type": "buttons_and_text",
        "options": [
            "2 weeks",
            "4 weeks",
            "6 weeks",
            "8 weeks",
        ],
        "placeholder": "Or type a number of weeks (1–8)...",
    },
]


def _parse_int_answer(answer, mapping, lo, hi, default):
    """Extract an int from a preset mapping or custom text."""
    if answer in mapping:
        return mapping[answer]
    import re
    nums = re.findall(r'\d+', answer)
    if nums:
        return max(lo, min(hi, int(nums[-1])))
    return default


def _parse_fitness_answer(answer):
    """Map fitness answer to a generator level string."""
    for label, level in FITNESS_LEVEL_MAP.items():
        if label.lower() in answer.lower():
            return level
    low = answer.lower()
    if any(w in low for w in ("couch", "never", "new", "starting", "beginner", "none")):
        return "beginner"
    if any(w in low for w in ("light", "walk", "occasional", "casual")):
        return "beginner"
    if any(w in low for w in ("moderate", "average", "decent", "ok", "okay", "regular")):
        return "intermediate"
    if any(w in low for w in ("advanced", "strong", "experienced", "serious", "well")):
        return "advanced"
    if any(w in low for w in ("elite", "competitive", "professional", "college", "athlete", "peak")):
        return "elite"
    return "intermediate"


def page_onboarding():
    name = st.session_state["username"]
    step = st.session_state["onboard_step"]
    messages = st.session_state["onboard_messages"]
    answers = st.session_state["onboard_answers"]

    st.markdown("## Chat with your Coach")

    # Add the current coach question to messages if needed
    if step < len(ONBOARD_QUESTIONS):
        q = ONBOARD_QUESTIONS[step]
        coach_text = q["coach_msg"].format(
            display_name=answers.get("display_name", ""),
        )
        if not messages or messages[-1].get("content") != coach_text:
            messages.append({"role": "assistant", "content": coach_text})

    # Render conversation so far
    html = "".join(_bubble(m["role"], m["content"]) for m in messages)
    st.markdown(f'<div class="coach-chat-wrap">{html}</div>', unsafe_allow_html=True)

    # Show input for the current step
    if step < len(ONBOARD_QUESTIONS):
        q = ONBOARD_QUESTIONS[step]
        st.write("")

        def _submit_answer(answer_text):
            messages.append({"role": "user", "content": answer_text})
            key = q["key"]
            if key == "current_days":
                answers[key] = _parse_int_answer(
                    answer_text, CURRENT_DAYS_MAP, 0, 7, 3)
            elif key == "target_days":
                val = _parse_int_answer(
                    answer_text, TARGET_DAYS_MAP, 3, 6, 4)
                answers[key] = val
                answers["days"] = val  # used by plan generator
            elif key == "duration_weeks":
                answers[key] = _parse_int_answer(
                    answer_text, {}, 1, 8, 4)
            elif key == "fitness_level":
                answers[key] = answer_text
                answers["level"] = _parse_fitness_answer(answer_text)
            else:
                answers[key] = answer_text
            st.session_state["onboard_step"] = step + 1
            st.rerun()

        if q["input_type"] == "text":
            # Text-only input (name question)
            text_val = st.text_input(
                "Your answer", placeholder=q["placeholder"],
                key=f"onboard_text_{step}", label_visibility="collapsed",
            )
            if st.button("Continue →", key=f"onboard_submit_{step}", type="primary"):
                if text_val.strip():
                    _submit_answer(text_val.strip())
                else:
                    st.error("Please type an answer.")

        else:  # buttons_and_text
            # Option buttons — stacked vertically
            descs = q.get("option_descriptions", [])
            for i, option in enumerate(q["options"]):
                label = option
                if i < len(descs):
                    label = f"{option} — {descs[i]}"
                if st.button(label, key=f"onboard_{step}_{i}"):
                    _submit_answer(option)

            # Custom text input
            st.caption("Or type your own answer:")
            text_val = st.text_input(
                "Custom answer", placeholder=q["placeholder"],
                key=f"onboard_text_{step}", label_visibility="collapsed",
            )
            if st.button("Submit", key=f"onboard_custom_{step}"):
                if text_val.strip():
                    _submit_answer(text_val.strip())
                else:
                    st.error("Please type an answer or pick an option above.")

    # All questions answered — finalize
    if step >= len(ONBOARD_QUESTIONS):
        display_name = answers.get("display_name", name)
        done_msg = (
            f"Awesome, {display_name}! I've got everything I need. "
            "Let me build your personalized training program now..."
        )
        if not messages or messages[-1].get("content") != done_msg:
            messages.append({"role": "assistant", "content": done_msg})

            # Save onboarding
            save_onboarding(name, answers)

            # Generate plan
            level = answers.get("level", "intermediate")
            days = answers.get("days", 5)
            week = build_week(level, days)
            save_plan_to_file(name, week)
            st.session_state["week_plan"] = week
            st.session_state["user_profile"] = {
                "name": display_name, "level": level, "days": days
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
    display_name = (profile or {}).get("display_name", name)
    st.markdown(f"## Welcome back, {display_name} 💪")

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
            st.markdown(f"**Days/week:** {profile.get('days', '—')}")
        with info_cols[1]:
            st.markdown(f"**Fitness Level:** {profile.get('fitness_level', '—')}")
        with info_cols[2]:
            st.markdown(f"**Goal:** {profile.get('goal', '—')}")
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
