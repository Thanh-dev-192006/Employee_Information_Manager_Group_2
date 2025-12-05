from datetime import date
from typing import List, Dict, Optional
import mysql.connector

from ..config.database import DatabaseConnection
from ..utils.helpers import parse_stored_procedure_error
from ..utils.exceptions import *

class ProjectManager:
    """Manage projects with CRUD operations"""
    
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
            return {"project_id": project_id, "message": "Project created successfully"}
            
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
            
            return {"message": "Project updated successfully"}
            
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
                raise NotFoundError("Project not found")
            
            conn.commit()
            return {"message": "Project deleted successfully"}
            
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            if "foreign key constraint" in str(err).lower():
                raise DeleteConstraintError("Cannot delete project because related data exists")
            raise DatabaseError(f"Delete project error: {err}")
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
            raise DatabaseError(f"Query error: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()