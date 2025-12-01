from typing import List, Dict
import mysql.connector

from ..config.database import DatabaseConnection
from ..utils.helpers import parse_stored_procedure_error
from ..utils.exceptions import *

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