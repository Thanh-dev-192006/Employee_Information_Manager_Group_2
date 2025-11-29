# -*- coding: utf-8 -*-
"""
Employee Management System - Manager Classes
Handles CRUD operations with stored procedures integration
"""

import mysql.connector
from typing import List, Dict, Optional, Any
from datetime import date, time
import csv
from decimal import Decimal



# CUSTOM EXCEPTIONS

class ValidationError(Exception):
    """Raised when validation fails"""
    pass

class NotFoundError(Exception):
    """Raised when record not found"""
    pass

class DatabaseError(Exception):
    """Raised when database operation fails"""
    pass

class DeleteConstraintError(Exception):
    """Raised when delete violates foreign key constraint"""
    pass


# DATABASE CONNECTION

class DatabaseConnection:
    """ Quản lý Database connection """
    
    @staticmethod
    def get_connection():
        """Get database connection"""
        config = {
            "host": "localhost",
            "user": "root",
            "password": "Thanh@123",
            "database": "employee_manager",
            "charset": "utf8mb4",
            "use_unicode": True,
        }
        conn = mysql.connector.connect(**config)
        # Set collation to match database
        cursor = conn.cursor()
        cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci")
        cursor.close()
        return conn



# HELPER FUNCTIONS

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


# 1. EMPLOYEE MANAGER

class EmployeeManager:
    """Quản lý nhân viên bằng CRUD operations"""
    
    @staticmethod
    def create_employee(full_name: str, gender: str, date_of_birth: date,
                        phone: str, email: str, address: str, hire_date: date,
                        department_id: int, position: str, base_salary: float) -> Dict:
        """Tạo nhân viên mới bằng sp_add_employee"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.callproc('sp_add_employee', [
                full_name, gender, date_of_birth, phone, email,
                address, hire_date, department_id, position, base_salary
            ])
            
            for result in cursor.stored_results():
                row = result.fetchone()
                employee_id = row['new_employee_id']
            
            conn.commit()
            return {"employee_id": employee_id, "message": "Thêm nhân viên thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise parse_stored_procedure_error(str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def update_employee(employee_id: int, full_name: str, phone: str,
                        email: str, address: str, position: str, base_salary: float) -> Dict:
        """Cập nhật thông tin nhân viên bằng sp_update_employee"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            cursor.callproc('sp_update_employee', [
                employee_id, full_name, phone, email, address, position, base_salary
            ])
            
            conn.commit()
            return {"message": "Cập nhật nhân viên thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise parse_stored_procedure_error(str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def delete_employee(employee_id: int) -> Dict:
        """Xóa nhân viên bằng sp_delete_employee"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            cursor.callproc('sp_delete_employee', [employee_id])
            conn.commit()
            
            return {"message": "Xóa nhân viên thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            if "foreign key constraint" in str(err).lower():
                raise DeleteConstraintError("Không thể xóa nhân viên vì có dữ liệu liên quan")
            raise parse_stored_procedure_error(str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_all_employees(limit: int = 100, offset: int = 0) -> List[Dict]:
        """Lấy thông tin tất cả nhân viên và departments"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT e.*, d.department_name, d.location
                FROM employees e
                JOIN departments d ON e.department_id = d.department_id
                ORDER BY e.employee_id
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_employee_by_id(employee_id: int) -> Optional[Dict]:
        """Lấy nhân viên bằng ID"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT e.*, d.department_name, d.location
                FROM employees e
                JOIN departments d ON e.department_id = d.department_id
                WHERE e.employee_id = %s
            """
            cursor.execute(query, (employee_id,))
            return cursor.fetchone()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def search_employees(keyword: str) -> List[Dict]:
        """Tìm nhân viên bằng tên, email, số đth"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT e.*, d.department_name
                FROM employees e
                JOIN departments d ON e.department_id = d.department_id
                WHERE e.full_name LIKE %s 
                OR e.email LIKE %s 
                OR e.phone_number LIKE %s
                ORDER BY e.full_name
            """
            search_pattern = f"%{keyword}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi tìm kiếm: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# 2. DEPARTMENT MANAGER

class DepartmentManager:
    """Quản lý department với CRUD operations"""
    
    @staticmethod
    def create_department(department_name: str, location: str) -> Dict:
        """Create new department using sp_add_department"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.callproc('sp_add_department', [department_name, location])
            
            for result in cursor.stored_results():
                row = result.fetchone()
                dept_id = row['new_dept_id']
            
            conn.commit()
            return {"department_id": dept_id, "message": "Thêm phòng ban thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise parse_stored_procedure_error(str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def update_department(department_id: int, department_name: str, location: str) -> Dict:
        """Cập nhật department bằng sp_update_department"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            cursor.callproc('sp_update_department', [department_id, department_name, location])
            conn.commit()
            
            return {"message": "Cập nhật phòng ban thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise parse_stored_procedure_error(str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def delete_department(department_id: int) -> Dict:
        """Xóa department với constraint check"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            # Check for employees in department
            cursor.execute("SELECT COUNT(*) as count FROM employees WHERE department_id = %s", (department_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                raise DeleteConstraintError(f"Không thể xóa phòng ban vì còn {count} nhân viên")
            
            cursor.execute("DELETE FROM departments WHERE department_id = %s", (department_id,))
            
            if cursor.rowcount == 0:
                raise NotFoundError("Không tìm thấy phòng ban")
            
            conn.commit()
            return {"message": "Xóa phòng ban thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Lỗi xóa phòng ban: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_all_departments() -> List[Dict]:
        """Có department bằng cách đếm nhân viên"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT d.*, 
                COUNT(e.employee_id) as employee_count,
                m.full_name as manager_name
                FROM departments d
                LEFT JOIN employees e ON d.department_id = e.department_id
                LEFT JOIN employees m ON d.manager_id = m.employee_id
                GROUP BY d.department_id
                ORDER BY d.department_id
            """
            cursor.execute(query)
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# 3. PROJECT MANAGER

class ProjectManager:
    """Quản lý dự án bằng CRUD operations"""
    
    @staticmethod
    def create_project(project_name: str, start_date: date, end_date: Optional[date],
                        budget: float, department_id: int) -> Dict:
        """Tạo dự án mới bằng sp_add_project"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.callproc('sp_add_project', [
                project_name, start_date, end_date, budget, department_id
            ])
            
            for result in cursor.stored_results():
                row = result.fetchone()
                project_id = row['new_project_id']
            
            conn.commit()
            return {"project_id": project_id, "message": "Thêm dự án thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise parse_stored_procedure_error(str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def update_project(project_id: int, project_name: str, end_date: Optional[date]) -> Dict:
        """Cập nhật dự án bằng sp_update_project"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            cursor.callproc('sp_update_project', [project_id, project_name, end_date])
            conn.commit()
            
            return {"message": "Cập nhật dự án thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise parse_stored_procedure_error(str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def delete_project(project_id: int) -> Dict:
        """Xóa dự án"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM projects WHERE project_id = %s", (project_id,))
            
            if cursor.rowcount == 0:
                raise NotFoundError("Không tìm thấy dự án")
            
            conn.commit()
            return {"message": "Xóa dự án thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            if "foreign key constraint" in str(err).lower():
                raise DeleteConstraintError("Không thể xóa dự án vì có dữ liệu liên quan")
            raise DatabaseError(f"Lỗi xóa dự án: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_all_projects(status: Optional[str] = None) -> List[Dict]:
        """Có tất cả dự án bằng v_project_participation view
        
        Args:
            status: 'ongoing', 'completed', or None for all
        """
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT p.*, v.total_employees, v.total_hours_worked, d.department_name
                FROM projects p
                LEFT JOIN v_project_participation v ON p.project_id = v.project_id
                JOIN departments d ON p.department_id = d.department_id
            """
            
            if status == 'ongoing':
                query += " WHERE p.end_date IS NULL OR p.end_date >= CURDATE()"
            elif status == 'completed':
                query += " WHERE p.end_date < CURDATE()"
            
            query += " ORDER BY p.start_date DESC"
            
            cursor.execute(query)
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# 4. ASSIGNMENT MANAGER

class AssignmentManager:
    """Quản lý phân công dự án"""
    
    @staticmethod
    def create_assignment(employee_id: int, project_id: int, 
                            role: str, hours_worked: float = 0) -> Dict:
        """Phân công bằng sp_assign_project"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.callproc('sp_assign_project', [
                employee_id, project_id, role, hours_worked
            ])
            
            for result in cursor.stored_results():
                row = result.fetchone()
                assignment_id = row['new_assignment_id']
            
            conn.commit()
            return {"assignment_id": assignment_id, "message": "Phân công thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise parse_stored_procedure_error(str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def update_assignment(assignment_id: int, role: str, hours_worked: float) -> Dict:
        """Cập nhật việc phân công"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            query = """
                UPDATE assignments 
                SET role = %s, hours_worked = %s
                WHERE assignment_id = %s
            """
            cursor.execute(query, (role, hours_worked, assignment_id))
            
            if cursor.rowcount == 0:
                raise NotFoundError("Không tìm thấy việc phân công")
            
            conn.commit()
            return {"message": "Cập nhật phân công thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Lỗi cập nhật: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def delete_assignment(assignment_id: int) -> Dict:
        """Xóa phân công"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM assignments WHERE assignment_id = %s", (assignment_id,))
            
            if cursor.rowcount == 0:
                raise NotFoundError("Không tìm thấy việc phân công")
            
            conn.commit()
            return {"message": "Xóa phân công thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Lỗi xóa: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_assignments_by_employee(employee_id: int) -> List[Dict]:
        """Có tất cả phân công của 1 nhân viên"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT a.*, p.project_name, p.start_date, p.end_date
                FROM assignments a
                JOIN projects p ON a.project_id = p.project_id
                WHERE a.employee_id = %s
                ORDER BY a.assigned_date DESC
            """
            cursor.execute(query, (employee_id,))
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_assignments_by_project(project_id: int) -> List[Dict]:
        """Có tất cả phân công của 1 dự án"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT a.*, e.full_name, e.position, e.email
                FROM assignments a
                JOIN employees e ON a.employee_id = e.employee_id
                WHERE a.project_id = %s
                ORDER BY a.assigned_date
            """
            cursor.execute(query, (project_id,))
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# 5. ATTENDANCE MANAGER 

class AttendanceManager:
    """Quản lý chấm công của nhân viên"""
    
    @staticmethod
    def mark_attendance(employee_id: int, work_date: date, 
                        check_in: Optional[time], check_out: Optional[time],
                        status: str) -> Dict:
        """Đánh dấu chấm công bằng sp_mark_attendance"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.callproc('sp_mark_attendance', [
                employee_id, work_date, check_in, check_out, status
            ])
            
            for result in cursor.stored_results():
                row = result.fetchone()
                message = row['message']
            
            conn.commit()
            return {"message": message}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise parse_stored_procedure_error(str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_attendance_by_employee(employee_id: int, month: int, year: int) -> List[Dict]:
        """Get attendance for employee using v_employee_attendance view"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT *
                FROM v_employee_attendance
                WHERE employee_id = %s 
                AND MONTH(work_date) = %s 
                AND YEAR(work_date) = %s
                ORDER BY work_date
            """
            cursor.execute(query, (employee_id, month, year))
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_monthly_attendance_summary(month: int, year: int) -> List[Dict]:
        """Có tổng kết chấm công hàng tháng của các department"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    d.department_name,
                    COUNT(DISTINCT a.employee_id) as total_employees,
                    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present_count,
                    SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) as absent_count,
                    SUM(CASE WHEN a.status = 'On Leave' THEN 1 ELSE 0 END) as leave_count
                FROM attendance a
                JOIN employees e ON a.employee_id = e.employee_id
                JOIN departments d ON e.department_id = d.department_id
                WHERE MONTH(a.work_date) = %s AND YEAR(a.work_date) = %s
                GROUP BY d.department_id, d.department_name
            """
            cursor.execute(query, (month, year))
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# 6. SALARY MANAGER

class SalaryManager:
    """Quản lý chi trả lương"""
    
    @staticmethod
    def record_salary_payment(employee_id: int, month: str, 
                            year: int, total_amount: float) -> Dict:
        """Ghi nhận chi trả lương bằng sp_record_salary_payment"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.callproc('sp_record_salary_payment', [
                employee_id, month, year, total_amount
            ])
            
            for result in cursor.stored_results():
                row = result.fetchone()
                payment_id = row['new_payment_id']
            
            conn.commit()
            return {"payment_id": payment_id, "message": "Ghi nhận lương thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise parse_stored_procedure_error(str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def calculate_salary(employee_id: int, month: str, year: int) -> Optional[Dict]:
        """Tính lương bằng v_monthly_salary_summary view"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT *
                FROM v_monthly_salary_summary
                WHERE employee_id = %s 
                AND salary_month = %s 
                AND year = %s
            """
            cursor.execute(query, (employee_id, month, year))
            return cursor.fetchone()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi tính lương: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_salary_by_employee(employee_id: int) -> List[Dict]:
        """Có lịch sử trả lương cho nhân viên"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT *
                FROM v_monthly_salary_summary
                WHERE employee_id = %s
                ORDER BY year DESC, 
                    CASE salary_month
                        WHEN 'January' THEN 1 WHEN 'February' THEN 2
                        WHEN 'March' THEN 3 WHEN 'April' THEN 4
                        WHEN 'May' THEN 5 WHEN 'June' THEN 6
                        WHEN 'July' THEN 7 WHEN 'August' THEN 8
                        WHEN 'September' THEN 9 WHEN 'October' THEN 10
                        WHEN 'November' THEN 11 WHEN 'December' THEN 12
                    END DESC
            """
            cursor.execute(query, (employee_id,))
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_salary_by_month(month: str, year: int) -> List[Dict]:
        """Có tất cả ghi nhận chi trả lương 1 tháng"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT *
                FROM v_monthly_salary_summary
                WHERE salary_month = %s AND year = %s
                ORDER BY employee_name
            """
            cursor.execute(query, (month, year))
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()



# 7. BONUS DEDUCTION MANAGER

class BonusDeductionManager:
    """Quản lý bonus và phạt"""
    
    @staticmethod
    def create_bonus_deduction(employee_id: int, bd_type: str, amount: float,
                                description: str, effective_date: date) -> Dict:
        """Tạo thêm bonus/phạt bằng sp_add_bonus_deduction"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.callproc('sp_add_bonus_deduction', [
                employee_id, bd_type, amount, description, effective_date
            ])
            
            for result in cursor.stored_results():
                row = result.fetchone()
                bd_id = row['new_bd_id']
            
            conn.commit()
            return {"bd_id": bd_id, "message": "Thêm thưởng/phạt thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise parse_stored_procedure_error(str(err))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def update_bonus_deduction(bd_id: int, description: str, amount: float) -> Dict:
        """Cập nhật bonus/phạt """
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            query = """
                UPDATE bonus_deductions
                SET description = %s, amount = %s
                WHERE bd_id = %s
            """
            cursor.execute(query, (description, amount, bd_id))
            
            if cursor.rowcount == 0:
                raise NotFoundError("Không tìm thấy bản ghi thưởng/phạt")
            
            conn.commit()
            return {"message": "Cập nhật thưởng/phạt thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Lỗi cập nhật: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def delete_bonus_deduction(bd_id: int) -> Dict:
        """Xóa bonus/phạt"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM bonus_deductions WHERE bd_id = %s", (bd_id,))
            
            if cursor.rowcount == 0:
                raise NotFoundError("Không tìm thấy bản ghi thưởng/phạt")
            
            conn.commit()
            return {"message": "Xóa thưởng/phạt thành công"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Lỗi xóa: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_bonus_deduction_by_employee(employee_id: int, 
                                        month: Optional[int] = None,
                                        year: Optional[int] = None) -> List[Dict]:
        """Có ghi nhận bonus/phạt của nhân viên"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT bd.*, e.full_name as employee_name
                FROM bonus_deductions bd
                JOIN employees e ON bd.employee_id = e.employee_id
                WHERE bd.employee_id = %s
            """
            params = [employee_id]
            
            if month and year:
                query += " AND MONTH(bd.effective_date) = %s AND YEAR(bd.effective_date) = %s"
                params.extend([month, year])
            
            query += " ORDER BY bd.effective_date DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_bonus_deduction_log(bd_id: Optional[int] = None,
                                employee_id: Optional[int] = None,
                                limit: int = 100) -> List[Dict]:
        """Get bonus/deduction audit log"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM bonus_deduction_log WHERE 1=1"
            params = []
            
            if bd_id:
                query += " AND bd_id = %s"
                params.append(bd_id)
            
            if employee_id:
                query += " AND employee_id = %s"
                params.append(employee_id)
            
            query += " ORDER BY log_time DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn log: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# 8. QUERY MANAGER (Advanced Queries + Export)

class QueryManager:
    """Manages complex queries and exports"""
    
    @staticmethod
    def query_employee_project_roles() -> List[Dict]:
        """INNER JOIN: Employee, Project, Role, Salary"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    e.employee_id,
                    e.full_name,
                    e.position,
                    e.base_salary,
                    p.project_name,
                    a.role as project_role,
                    a.hours_worked,
                    d.department_name
                FROM employees e
                INNER JOIN assignments a ON e.employee_id = a.employee_id
                INNER JOIN projects p ON a.project_id = p.project_id
                INNER JOIN departments d ON e.department_id = d.department_id
                ORDER BY e.full_name, p.project_name
            """
            cursor.execute(query)
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def query_all_employees_with_roles() -> List[Dict]:
        """LEFT JOIN: All employees (with/without projects)"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    e.employee_id,
                    e.full_name,
                    e.position,
                    e.base_salary,
                    d.department_name,
                    p.project_name,
                    a.role as project_role,
                    a.hours_worked,
                    CASE 
                        WHEN a.assignment_id IS NULL THEN 'Chưa có dự án'
                        ELSE 'Đang tham gia dự án'
                    END as assignment_status
                FROM employees e
                LEFT JOIN assignments a ON e.employee_id = a.employee_id
                LEFT JOIN projects p ON a.project_id = p.project_id
                JOIN departments d ON e.department_id = d.department_id
                ORDER BY e.full_name, p.project_name
            """
            cursor.execute(query)
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def query_employee_project_manager() -> List[Dict]:
        """Multi-table JOIN (3+ tables): Employee, Project, Department Manager"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    e.employee_id,
                    e.full_name as employee_name,
                    e.position,
                    p.project_name,
                    a.role as project_role,
                    a.hours_worked,
                    d.department_name,
                    m.full_name as manager_name,
                    m.email as manager_email
                FROM employees e
                INNER JOIN assignments a ON e.employee_id = a.employee_id
                INNER JOIN projects p ON a.project_id = p.project_id
                INNER JOIN departments d ON e.department_id = d.department_id
                LEFT JOIN employees m ON d.manager_id = m.employee_id
                ORDER BY d.department_name, p.project_name, e.full_name
            """
            cursor.execute(query)
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def query_above_average_salary() -> List[Dict]:
        """Employees with salary above global average"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    e.employee_id,
                    e.full_name,
                    e.position,
                    e.base_salary,
                    d.department_name,
                    (SELECT AVG(base_salary) FROM employees) as avg_salary,
                    (e.base_salary - (SELECT AVG(base_salary) FROM employees)) as difference
                FROM employees e
                JOIN departments d ON e.department_id = d.department_id
                WHERE e.base_salary > (SELECT AVG(base_salary) FROM employees)
                ORDER BY e.base_salary DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Lỗi truy vấn: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def export_to_csv(data: List[Dict], filename: str) -> Dict:
        """Export query results to CSV file"""
        try:
            if not data:
                raise ValueError("Không có dữ liệu để export")
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                # Get column names from first row
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for row in data:
                    # Convert Decimal to float for CSV
                    processed_row = {}
                    for key, value in row.items():
                        if isinstance(value, Decimal):
                            processed_row[key] = float(value)
                        elif value is None:
                            processed_row[key] = ''
                        else:
                            processed_row[key] = value
                    writer.writerow(processed_row)
            
            return {
                "message": f"Đã export {len(data)} dòng vào {filename}",
                "rows": len(data),
                "filename": filename
            }
            
        except Exception as e:
            raise DatabaseError(f"Lỗi export CSV: {e}")


