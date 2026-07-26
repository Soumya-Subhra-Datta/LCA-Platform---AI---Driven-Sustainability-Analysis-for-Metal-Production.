import re
from typing import Any, Optional


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, "Valid"


def validate_file_extension(filename: str, allowed_extensions: list[str]) -> bool:
    return filename.rsplit('.', 1)[-1].lower() in allowed_extensions


def validate_file_size(file_size: int, max_size_mb: int = 50) -> bool:
    return file_size <= max_size_mb * 1024 * 1024


def sanitize_string(value: str) -> str:
    return re.sub(r'[<>"\'`;]', '', value).strip()


def validate_numeric_range(value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
    try:
        num = float(value)
        if min_val is not None and num < min_val:
            return False
        if max_val is not None and num > max_val:
            return False
        return True
    except (TypeError, ValueError):
        return False
