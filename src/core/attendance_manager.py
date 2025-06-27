import csv
import os
from datetime import datetime

LOGS_DIR = "data/attendance_logs"

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
    
    # Split student_info to get ID and Name
    try:
        student_id, full_name = student_info.split('_', 1)
    except ValueError:
        print(f"Error: Invalid student_info format: {student_info}")
        return False

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
        # Write header if the file is new
        if not file_exists:
            writer.writerow(['StudentID', 'FullName', 'Course', 'Class', 'Date', 'Time'])
        
        writer.writerow([student_id, full_name, course_name, class_name, today_str, timestamp_str])
    
    return True # Indicate successful logging