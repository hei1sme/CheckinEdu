import json
import os

DATA_FILE_PATH = "data/system_data/courses_and_classes.json"

def _get_default_structure():
    """Returns the default data structure."""
    return {"courses": {}}

def load_data():
    """
    Loads the course and class data from the JSON file.
    Validates the structure and fixes it if it's corrupted or incorrect.
    """
    if not os.path.exists(DATA_FILE_PATH):
        # If the file doesn't exist, create it with a valid empty structure
        save_data(_get_default_structure())
        return _get_default_structure()
    
    try:
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # --- STRUCTURE VALIDATION ---
            # Check if data is a dictionary and has the 'courses' key
            if isinstance(data, dict) and 'courses' in data and isinstance(data['courses'], dict):
                return data
            else:
                # Data is corrupted or has wrong format, reset it.
                print("Warning: Data file is corrupted. Resetting to default.")
                save_data(_get_default_structure())
                return _get_default_structure()
    except (json.JSONDecodeError, FileNotFoundError):
        # In case of corruption or race condition, reset to default.
        print("Warning: Could not decode JSON data. Resetting to default.")
        save_data(_get_default_structure())
        return _get_default_structure()

def save_data(data):
    """Saves the provided data structure to the JSON file."""
    os.makedirs(os.path.dirname(DATA_FILE_PATH), exist_ok=True)
    with open(DATA_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_course(course_name: str):
    """Adds a new course if it doesn't already exist."""
    data = load_data()
    # Now we are sure data['courses'] is a dictionary
    if course_name not in data["courses"]:
        data["courses"][course_name] = []  # Initialize with an empty list of classes
        save_data(data)
        return True
    return False

def add_class_to_course(course_name: str, class_name: str):
    """Adds a new class to a specified course."""
    data = load_data()
    if course_name in data["courses"]:
        # Ensure the value is a list before appending
        if not isinstance(data["courses"][course_name], list):
            data["courses"][course_name] = [] # Fix if corrupted
            
        if class_name not in data["courses"][course_name]:
            data["courses"][course_name].append(class_name)
            save_data(data)
            return True
    return False

def get_courses():
    """Returns a list of all course names."""
    data = load_data()
    return list(data["courses"].keys())

def get_classes_for_course(course_name: str):
    """Returns a list of classes for a given course."""
    data = load_data()
    return data["courses"].get(course_name, [])