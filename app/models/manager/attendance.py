from typing import List, Dict, Optional
from datetime import date, time
import mysql.connector

from ..config.database import DatabaseConnection
from ..utils.helpers import parse_stored_procedure_error
from ..utils.exceptions import *

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