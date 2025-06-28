import csv
import os
import re # Import the regex module
from datetime import datetime

LOGS_DIR = "data/attendance_logs"

def _format_name_with_spaces(name_nospace):
    """Converts 'LeNguyenGiaHung' back to 'Le Nguyen Gia Hung'."""
    if not name_nospace:
        return ""
    # Use regex to find capital letters and insert a space before them
    # then strip any leading space.
    return re.sub(r"(\B[A-Z])", r" \1", name_nospace).strip()

def log_attendance(student_info: str, course_name: str, class_name: str):
    """
    Logs student attendance to a daily, course-specific CSV file.
    Returns True if logged successfully, False otherwise.
    
    student_info is expected to be in "StudentID_FullName" format.
    """
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    timestamp_str = datetime.now().strftime('%H:%M:%S')
    
    # Filename format: COURSE_CLASS_DATE.csv
    filename = os.path.join(LOGS_DIR, f"{course_name}_{class_name}_{today_str}.csv")
    
    file_exists = os.path.isfile(filename)
    
    try:
        # student_info is now "StudentID_FullNameNoSpace_Class"
        student_id, name_nospace, student_class = student_info.split('_', 2)
    except ValueError:
        return False

    # --- NEW: Format the name for logging ---
    full_name_with_spaces = _format_name_with_spaces(name_nospace)

    # Check for duplicates before writing
    if file_exists:
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] == student_id:
                    # Student already logged today
                    return False # Indicate not logged this time
    
    # Log the new entry
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['StudentID', 'FullName', 'Course', 'Class', 'Date', 'Time'])
        
        # --- USE THE FORMATTED NAME ---
        writer.writerow([student_id, full_name_with_spaces, course_name, class_name, today_str, timestamp_str])
    
    return True # Indicate successful logging