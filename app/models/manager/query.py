from typing import List, Dict
import mysql.connector
from decimal import Decimal
import csv

from ..config.database import DatabaseConnection
from ..utils.helpers import parse_stored_procedure_error
from ..utils.exceptions import *

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
