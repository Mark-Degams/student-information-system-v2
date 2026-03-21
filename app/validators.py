import app.database as db

# --- College ---------------------------------------------------- 

def validate_college_code(code, edit_mode=False, orig_code=""):
    size = len(code)
    if size == 0:
        return None, None
    if size < 3:
        return "error", "College code must be 3 or more characters."
    if code.isalpha() == False:
        return "error", "College code must only contain letters."
    if not code.strip():
        return "error", "College code is required."
    if db.college_code_exists(code.upper()) and not (edit_mode and code.upper() == orig_code):
        return "error", "College code already exists."
    return "valid", ""

def validate_college_name(name):
    if len(name) == 0:
        return None, None
    if name.replace(" ", "").isalpha() == False:
        return "error", "College name must only contain letters and spaces."
    if not name.strip():
        return "error", "College name is required."
    return "valid", ""


# --- Program ---------------------------------------------------- 

def validate_program_code(code, edit_mode=False, orig_code=""):
    size = len(code)
    if size == 0:
        return None, None
    if size < 3:
        return "error", "Program code must be 3 or more characters."
    if code.replace(" ", "").replace("-", "").isalpha() == False:
        return "error", "Program code must only contain letters, spaces, and hyphens."
    if not code.strip():
        return "error", "Program code is required."
    if db.program_code_exists(code.upper()) and not (edit_mode and code.upper() == orig_code):
        return "error", "Program code already exists."
    return "valid", ""

def validate_program_name(name):
    if len(name) == 0:
        return None, None
    if name.replace(" ", "").replace("-", "").isalpha() == False:
        return "error", "Program name must only contain letters, spaces, and hyphens."
    if not name.strip():
        return "error", "Program name is required."
    return "valid", ""


# --- Student ---------------------------------------------------- 

def validate_student_id(sid, edit_mode=False):
    if edit_mode:
        return "valid", ""
    if len(sid) == 0:
        return None, None
    if not db.validate_student_id(sid):
        return "error", "ID must be in YYYY-NNNN format (e.g. 2024-0001)."
    return "valid", ""

def validate_student_name(name):
    if len(name) == 0:
        return None, None
    if name.replace(" ", "").replace("-", "").replace("'", "").isalpha() == False:
        return "error", "Student name must only contain letters, spaces, hyphens, and apostrophes."
    if not name.strip():
        return "error", "Student name is required."
    return "valid", ""