from datetime import date
from typing import List, Dict, Optional
import mysql.connector

from ..config.database import DatabaseConnection
from ..utils.helpers import parse_stored_procedure_error
from ..utils.exceptions import *

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
