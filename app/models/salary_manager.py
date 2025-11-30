from typing import List, Dict, Optional
import mysql.connector

from .database import DatabaseConnection
from .helpers import parse_stored_procedure_error
from .exceptions import *

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