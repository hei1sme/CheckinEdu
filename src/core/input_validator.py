import re
from datetime import datetime

def is_valid_student_id(student_id: str) -> bool:
    """
    Validates the Student ID format: SE<2-digit khóa><4-digit id>.
    Example: SE191234. The khóa must be between 15 and the current khóa.
    """
    if not student_id or not isinstance(student_id, str):
        return False
    
    pattern = re.compile(r"^SE(\d{2})(\d{4})$")
    match = pattern.match(student_id)
    
    if not match:
        return False
    
    khoa_str = match.group(1)
    khoa = int(khoa_str)
    
    current_year_short = datetime.now().year % 100
    
    # Assuming khóa starts from 15 (2015)
    if not (15 <= khoa <= current_year_short):
        return False
        
    return True

def is_valid_full_name(full_name: str) -> bool:
    """
    Validates the Full Name format. Must contain at least two words,
    with each word starting with a capital letter.
    Allows for Unicode characters (Vietnamese names).
    """
    if not full_name or not isinstance(full_name, str):
        return False
        
    # Regex to match Vietnamese name format
    # Each word starts with an uppercase letter followed by lowercase letters.
    # Words are separated by a single space.
    pattern = re.compile(r"^[A-ZÀ-Ỹ][a-zà-ỹ]+(\s[A-ZÀ-Ỹ][a-zà-ỹ]+)+$")
    
    return bool(pattern.fullmatch(full_name.strip()))