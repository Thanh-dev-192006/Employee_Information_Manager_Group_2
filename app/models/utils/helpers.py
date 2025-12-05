from datetime import datetime, date, time, timedelta
from decimal import Decimal
from .exceptions import ValidationError, NotFoundError, DatabaseError
import re

MONEY_SCALE = 10_000   # DB amount * 10,000 = VNĐ hiển thị
EMAIL_DOMAIN = "@161Corp.com"
PHONE_RE = re.compile(r"^0\d{9}$")

def month_number_to_name(month_num: int) -> str:
    """Đổi tháng số qua chữ"""
    months = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    return months.get(month_num, '')

def month_name_to_number(month_name: str) -> int:
    """Đổi tên tháng qua số """
    months = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    return months.get(month_name, 0)

def format_currency_vnd(amount: float) -> str:
    """Format currency in VND. Returns '0.00 VND' if None."""
    if amount is None:
        return "0.00 VND"
    return f"{amount:,.2f} VND"

def parse_stored_procedure_error(error_msg: str) -> Exception:
    """Parse error message from stored procedure"""
    if "Email already exists" in error_msg:
        return ValidationError("Email already exists")
    elif "Phone number already exists" in error_msg:
        return ValidationError("Phone number already exists")
    elif "Department ID does not exist" in error_msg:
        return ValidationError("Department does not exist")
    elif "Employee not found" in error_msg:
        return NotFoundError("Employee not found")
    elif "Department not found" in error_msg:
        return NotFoundError("Department not found")
    elif "Project not found" in error_msg:
        return NotFoundError("Project not found")
    elif "Hire date cannot be in the future" in error_msg:
        return ValidationError("Hire date cannot be in the future")
    elif "Base salary must be greater than 0" in error_msg:
        return ValidationError("Base salary must be greater than 0")
    elif "already assigned to this project" in error_msg:
        return ValidationError("Employee is already assigned to this project")
    elif "already recorded" in error_msg:
        return ValidationError("Salary for this month is already recorded")
    else:
        return DatabaseError(f"Database error: {error_msg}")
    
def parse_display_date(s: str) -> date:
    
    if not s:
        raise ValidationError("Date must not be empty")

    s = s.strip().replace("-", "/")

    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        raise ValidationError("Date must be in DD/MM/YYYY format (e.g. 25/12/2024)")

def format_display_date(d: date) -> str:
    """Format date -> DD/MM/YYYY"""
    if d is None:
        return ""
    return d.strftime("%d/%m/%Y")


def parse_display_time(s: str) -> time:

    if not s:
        raise ValidationError("Time must not be empty")

    s = s.strip()
    formats = ["%H:%M", "%H:%M:%S"]

    for fmt in formats:
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            continue

    raise ValidationError("Giờ phải có dạng HH:MM hoặc HH:MM:SS")
    
    # unreachable

def format_display_time(t) -> str:
    """Format time -> HH:MM hoặc HH:MM:SS. Trả về '' nếu None."""
    if t is None:
        return ""
    
    if isinstance(t, timedelta):
        total_seconds = int(t.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if seconds > 0:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return f"{hours:02}:{minutes:02}"

    if hasattr(t, 'second'):
        if t.second > 0:
            return t.strftime("%H:%M:%S")
        return t.strftime("%H:%M")
    
    return str(t)


def parse_currency_input(value: str) -> float:
    """
    Parse tiền người dùng nhập -> VNĐ.
    Hỗ trợ: '10,000,000', '10tr', '10 triệu'
    """
    if not value:
        return 0.0

    v = value.lower().replace(",", "").strip()

    # dạng 10tr, 10 triệu
    if "tr" in v or "triệu" in v:
        num = float(re.sub(r"[^\d.]", "", v))
        return num * 1_000_000

    # dạng số thuần
    try:
        return float(v)
    except ValueError:
        raise ValidationError("Invalid currency value")

def to_db_money(vnd_amount: float) -> Decimal:
    """
    Convert VNĐ -> DB (chia MONEY_SCALE)
    VD: 15,000,000 -> 1500 nếu MONEY_SCALE = 10,000
    """
    return Decimal(vnd_amount) / Decimal(MONEY_SCALE)

def to_vnd(db_amount) -> float:
    """
    Convert DB -> VNĐ (nhân MONEY_SCALE)
    VD: 1500 -> 15,000,000
    """
    if db_amount is None:
        return 0.0  
    return float(db_amount) * MONEY_SCALE


def validate_phone(phone: str) -> str:
    """Validate số điện thoại VN"""
    if not PHONE_RE.fullmatch(phone):
        raise ValidationError("Phone must be 10 digits and start with 0")
    return phone

def validate_hire_date(hire_date: date) -> None:
    """Ngày tuyển <= hôm nay"""
    if hire_date > date.today():
        raise ValidationError("Hire date cannot be in the future")

def validate_salary_vnd(amount: float) -> float:
    """Validate salary in VND (must be > 0)"""
    if amount is None or amount <= 0:
        raise ValidationError("Salary must be greater than 0")
    return amount

def ensure_email_domain(email: str) -> str:
    """
    Validate email.
    Nếu không có domain -> tự thêm EMAIL_DOMAIN
    """
    if not email or email.strip() == "":
        raise ValidationError("Email must not be empty")

    email = email.strip()

    if "@" not in email:
        return email + EMAIL_DOMAIN

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValidationError("Invalid email")

    return email