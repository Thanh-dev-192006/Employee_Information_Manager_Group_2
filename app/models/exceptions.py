# app/utils/exceptions.py

class AppError(Exception):
    """Lỗi chung của app"""


class ValidationError(AppError):
    """Sai dữ liệu đầu vào"""


class NotFoundError(AppError):
    """Không tìm thấy dữ liệu"""


class DeleteConstraintError(AppError):
    """Không xóa được do ràng buộc FK / dữ liệu liên quan"""


class DatabaseError(AppError):
    """Lỗi DB / truy vấn"""
