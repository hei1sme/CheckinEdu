import json
import os

SETTINGS_FILE_PATH = "data/system_data/app_settings.json"

DEFAULT_SETTINGS = {
    "confirmation_threshold": 3,
    "camera_index": 0
}

def load_settings():
    """
    Loads application settings from the JSON file.
    If the file doesn't exist or is invalid, it creates one with default settings.
    """
    if not os.path.exists(SETTINGS_FILE_PATH):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    try:
        with open(SETTINGS_FILE_PATH, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            # Ensure all default keys are present
            settings = {**DEFAULT_SETTINGS, **settings}
            return settings
    except (json.JSONDecodeError, FileNotFoundError):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

def save_settings(settings_dict):
    os.makedirs(os.path.dirname(SETTINGS_FILE_PATH), exist_ok=True)
    with open(SETTINGS_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(settings_dict, f, indent=4)