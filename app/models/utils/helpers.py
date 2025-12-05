from datetime import datetime, date, time
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
    """Format tiền tệ VNĐ. Trả về '0.00 VNĐ' nếu None."""
    if amount is None:
        return "0.00 VNĐ"
    return f"{amount:,.2f} VNĐ"

def parse_stored_procedure_error(error_msg: str) -> Exception:
    """Parse error message from stored procedure"""
    if "Email already exists" in error_msg:
        return ValidationError("Email đã tồn tại trong hệ thống")
    elif "Phone number already exists" in error_msg:
        return ValidationError("Số điện thoại đã tồn tại trong hệ thống")
    elif "Department ID does not exist" in error_msg:
        return ValidationError("Phòng ban không tồn tại")
    elif "Employee not found" in error_msg:
        return NotFoundError("Không tìm thấy nhân viên")
    elif "Department not found" in error_msg:
        return NotFoundError("Không tìm thấy phòng ban")
    elif "Project not found" in error_msg:
        return NotFoundError("Không tìm thấy dự án")
    elif "Hire date cannot be in the future" in error_msg:
        return ValidationError("Ngày tuyển dụng không thể ở tương lai")
    elif "Base salary must be greater than 0" in error_msg:
        return ValidationError("Lương cơ bản phải lớn hơn 0")
    elif "already assigned to this project" in error_msg:
        return ValidationError("Nhân viên đã được phân công vào dự án này")
    elif "already recorded" in error_msg:
        return ValidationError("Lương tháng này đã được ghi nhận")
    else:
        return DatabaseError(f"Lỗi database: {error_msg}")
    
def parse_display_date(s: str) -> date:
    
    if not s:
        raise ValidationError("Ngày không được để trống")

    s = s.strip().replace("-", "/")

    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        raise ValidationError("Ngày phải có dạng DD/MM/YYYY (vd: 25/12/2024)")

def format_display_date(d: date) -> str:
    """Format date -> DD/MM/YYYY"""
    return d.strftime("%d/%m/%Y")


def parse_display_time(s: str) -> time:

    if not s:
        raise ValidationError("Giờ không được để trống")

    s = s.strip()
    formats = ["%H:%M", "%H:%M:%S"]

    for fmt in formats:
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            continue

    raise ValidationError("Giờ phải có dạng HH:MM hoặc HH:MM:SS")

def format_display_time(t: time) -> str:
    """Format time -> HH:MM hoặc HH:MM:SS. Trả về '' nếu None."""
    if t is None:
        return ""
    if t.second > 0:
        return t.strftime("%H:%M:%S")
    return t.strftime("%H:%M")


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
        raise ValidationError("Giá trị tiền không hợp lệ")

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
    return float(db_amount) * MONEY_SCALE


def validate_phone(phone: str) -> str:
    """Validate số điện thoại VN"""
    if not PHONE_RE.fullmatch(phone):
        raise ValidationError("Số điện thoại phải gồm 10 số và bắt đầu bằng 0")
    return phone

def validate_hire_date(hire_date: date) -> None:
    """Ngày tuyển <= hôm nay"""
    if hire_date > date.today():
        raise ValidationError("Ngày tuyển dụng không thể lớn hơn hôm nay")

def validate_salary_vnd(amount: float) -> float:
    """Kiểm tra tiền lương hợp lệ (phải > 0)"""
    if amount is None or amount <= 0:
        raise ValidationError("Tiền lương phải lớn hơn 0")
    return amount

def ensure_email_domain(email: str) -> str:
    """
    Validate email.
    Nếu không có domain -> tự thêm EMAIL_DOMAIN
    """
    if not email or email.strip() == "":
        raise ValidationError("Email không được để trống")

    email = email.strip()

    if "@" not in email:
        return email + EMAIL_DOMAIN

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValidationError("Email không hợp lệ")

    return email