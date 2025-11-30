from decimal import Decimal
from .exceptions import ValidationError, NotFoundError, DatabaseError

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
    """Format tiền tệ VNĐ"""
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