import mysql.connector
from typing import List, Dict

from .database import DatabaseConnection
from .helpers import parse_stored_procedure_error
from .exceptions import *

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
