from datetime import datetime
from constants import *
import json


def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"specialties": {}}
    except json.JSONDecodeError:
        return {"specialties": {}}


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


RESULTS_FILE = "test_results.json"


def load_results():
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
        except json.JSONDecodeError:
            return []


def save_results(data):
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_result(fio, specialty, correct, total, username="—", user_id="—"):
    result_file = "test_results.json"
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    new_result = {
        "fio": fio,
        "username": username,
        "user_id": user_id,
        "specialty": specialty,
        "correct": correct,
        "total": total,
        "timestamp": timestamp
    }

    if os.path.exists(result_file):
        with open(result_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(new_result)

    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

