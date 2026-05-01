import json
import os

SETTINGS_FILE = 'settings.json'
LEADERBOARD_FILE = 'leaderboard.json'

DEFAULT_SETTINGS = {
    "sound": True,
    "color": "RED",
    "difficulty": "NORMAL" # EASY, NORMAL, HARD
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return []

def save_score(name, score, distance):
    board = load_leaderboard()
    board.append({"name": name, "score": score, "distance": int(distance)})
    # Сортируем по очкам (по убыванию) и оставляем топ 10
    board = sorted(board, key=lambda x: x['score'], reverse=True)[:10]
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(board, f, indent=4)