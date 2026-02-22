import json
import datetime
import hashlib
import os

FILE = "users.json"


def load_users():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users):
    with open(FILE, "w") as f:
        json.dump(users, f, indent=2)


def _hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return salt, h.hex()


def register_user(username, password):
    """Register a new user, wiping any existing users (single-user mode)."""
    salt, pw_hash = _hash_password(password)
    users = {
        username: {
            "password_hash": pw_hash,
            "salt": salt,
        }
    }
    save_users(users)


def authenticate(username, password):
    """Return True if username exists and password matches."""
    users = load_users()
    user = users.get(username)
    if not user:
        return False
    salt = user.get("salt", "")
    _, pw_hash = _hash_password(password, salt)
    return pw_hash == user.get("password_hash", "")


def get_current_user():
    """Return (username, profile) for the single registered user, or (None, None)."""
    users = load_users()
    if not users:
        return None, None
    username = next(iter(users))
    return username, users[username]


def delete_all_users():
    """Wipe the entire userbase (used on logout)."""
    save_users({})


def save_profile(name, level, days):
    users = load_users()
    if name not in users:
        users[name] = {}
    users[name]["level"] = level
    users[name]["days"] = days
    save_users(users)


def get_profile(name):
    users = load_users()
    return users.get(name)


def save_onboarding(name, data):
    """Save onboarding answers and mark onboarding as complete."""
    users = load_users()
    if name not in users:
        users[name] = {}
    users[name]["onboarding_complete"] = True
    users[name]["display_name"] = data.get("display_name", name)
    users[name]["current_days"] = data.get("current_days", 0)
    users[name]["days"] = data.get("days", 5)
    users[name]["fitness_level"] = data.get("fitness_level", "")
    users[name]["level"] = data.get("level", "intermediate")
    users[name]["goal"] = data.get("goal", "General health and fitness")
    users[name]["duration_weeks"] = data.get("duration_weeks", 4)
    users[name]["program_start"] = datetime.date.today().isoformat()

    # Initialize tracking if not present
    if "workouts_completed" not in users[name]:
        users[name]["workouts_completed"] = []
    if "total_workouts" not in users[name]:
        users[name]["total_workouts"] = 0

    save_users(users)


def is_onboarded(name):
    """Check if user has completed onboarding."""
    profile = get_profile(name)
    if not profile:
        return False
    return profile.get("onboarding_complete", False)


def log_workout(name, date_str=None):
    """Log a completed workout for today (or a given date)."""
    if date_str is None:
        date_str = datetime.date.today().isoformat()
    users = load_users()
    if name not in users:
        return
    if "workouts_completed" not in users[name]:
        users[name]["workouts_completed"] = []
    if date_str not in users[name]["workouts_completed"]:
        users[name]["workouts_completed"].append(date_str)
    users[name]["total_workouts"] = len(users[name]["workouts_completed"])
    save_users(users)


def get_streaks(name):
    """Calculate daily streak, weekly streak, and total workouts."""
    profile = get_profile(name)
    if not profile:
        return {"daily_streak": 0, "weekly_streak": 0, "total_workouts": 0}

    completed = sorted(profile.get("workouts_completed", []))
    total = len(completed)

    if not completed:
        return {"daily_streak": 0, "weekly_streak": 0, "total_workouts": 0}

    # Daily streak: consecutive days ending today or yesterday
    today = datetime.date.today()
    daily_streak = 0
    check_date = today
    # Allow streak to count if today hasn't been logged yet (check yesterday)
    if today.isoformat() not in completed:
        check_date = today - datetime.timedelta(days=1)

    while check_date.isoformat() in completed:
        daily_streak += 1
        check_date -= datetime.timedelta(days=1)

    # Weekly streak: consecutive weeks with at least 1 workout
    weekly_streak = 0
    current_week_start = today - datetime.timedelta(days=today.weekday())  # Monday
    completed_dates = set(completed)

    while True:
        week_end = current_week_start + datetime.timedelta(days=6)
        has_workout = any(
            current_week_start <= datetime.date.fromisoformat(d) <= week_end
            for d in completed_dates
        )
        if has_workout:
            weekly_streak += 1
            current_week_start -= datetime.timedelta(days=7)
        else:
            break

    return {
        "daily_streak": daily_streak,
        "weekly_streak": weekly_streak,
        "total_workouts": total,
    }
