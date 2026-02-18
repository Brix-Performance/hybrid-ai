import json

FILE = "users.json"

def load_users():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(FILE, "w") as f:
        json.dump(users, f, indent=2)

def save_profile(name, level, days):
    users = load_users()
    users[name] = {
        "level": level,
        "days": days
    }
    save_users(users)

def get_profile(name):
    users = load_users()
    return users.get(name)
