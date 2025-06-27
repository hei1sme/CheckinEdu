import json
import os

DATA_FILE_PATH = "data/system_data/courses_and_classes.json"

def _get_default_structure():
    """Returns the default data structure."""
    return {} # The top-level is now just the dictionary of courses

def load_data():
    """
    Loads the course and class data from the JSON file.
    Validates the structure and fixes it if it's corrupted or incorrect.
    """
    if not os.path.exists(DATA_FILE_PATH):
        save_data(_get_default_structure())
        return _get_default_structure()
    
    try:
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # --- STRUCTURE VALIDATION ---
            # The top-level object must be a dictionary.
            if isinstance(data, dict):
                return data
            else:
                print("Warning: Data file is corrupted. Resetting to default.")
                save_data(_get_default_structure())
                return _get_default_structure()
    except (json.JSONDecodeError, FileNotFoundError):
        print("Warning: Could not decode JSON data. Resetting to default.")
        save_data(_get_default_structure())
        return _get_default_structure()

def save_data(data):
    # (This function remains the same)
    os.makedirs(os.path.dirname(DATA_FILE_PATH), exist_ok=True)
    with open(DATA_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_course(course_name: str):
    data = load_data()
    if course_name not in data:
        data[course_name] = []  # Initialize with an empty list of classes
        save_data(data)
        return True
    return False

def add_class_to_course(course_name: str, class_name: str):
    data = load_data()
    if course_name in data:
        if not isinstance(data[course_name], list):
            data[course_name] = [] # Fix if corrupted
            
        if class_name not in data[course_name]:
            data[course_name].append(class_name)
            save_data(data)
            return True
    return False

def get_courses():
    data = load_data()
    return list(data.keys())

def get_classes_for_course(course_name: str):
    data = load_data()
    return data.get(course_name, [])

def remove_course(course_name: str):
    """Removes a course and all its classes."""
    data = load_data()
    if course_name in data:
        del data[course_name]
        save_data(data)
        return True
    return False

def remove_class_from_course(course_name: str, class_name: str):
    """Removes a specific class from a course."""
    data = load_data()
    if course_name in data and class_name in data[course_name]:
        data[course_name].remove(class_name)
        save_data(data)
        return True
    return False