from typing import List, Dict, Optional
import mysql.connector

from ..config.database import DatabaseConnection
from ..utils.helpers import parse_stored_procedure_error, month_name_to_number
from ..utils.exceptions import *

class SalaryManager:
    """Quản lý lương và tính lương tạm tính"""
    
    @staticmethod
    def record_salary_payment(employee_id: int, month: str, 
                            year: int, total_amount: float) -> Dict:
        """Ghi nhận chi trả lương (Chốt sổ)"""
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
            return {"payment_id": payment_id, "message": "Salary recorded successfully"}
            
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
        """Tính toán lương thử cho 1 nhân viên (Preview)"""
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            month_num = month_name_to_number(month)

            query = """
                SELECT 
                    e.employee_id,
                    e.full_name as employee_name,
                    e.base_salary,
                    COALESCE(bd.total_bonus, 0) as total_bonus,
                    COALESCE(bd.total_deduction, 0) as total_deduction,
                    (e.base_salary + COALESCE(bd.total_bonus, 0) - COALESCE(bd.total_deduction, 0)) as net_amount,
                    'Estimated' as payment_status
                FROM employees e
                LEFT JOIN (
                    SELECT 
                        employee_id, 
                        SUM(CASE WHEN bd_type = 'Bonus' THEN amount ELSE 0 END) as total_bonus,
                        SUM(CASE WHEN bd_type = 'Deduction' THEN amount ELSE 0 END) as total_deduction
                    FROM bonus_deductions
                    WHERE MONTH(effective_date) = %s AND YEAR(effective_date) = %s
                    GROUP BY employee_id
                ) bd ON e.employee_id = bd.employee_id
                WHERE e.employee_id = %s
            """
            cursor.execute(query, (month_num, year, employee_id))
            return cursor.fetchone()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Salary calculation error: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_salary_by_employee(employee_id: int) -> List[Dict]:
        """Lịch sử trả lương của nhân viên"""
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
            raise DatabaseError(f"Query error: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_salary_by_month(month: str, year: int, limit: int = 100, offset: int = 0, sort_by: str = "employee_id", sort_order: str = "ASC") -> List[Dict]:
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            month_num = month_name_to_number(month)

            sort_mapping = {
                "employee_id": "e.employee_id",
                "employee_name": "e.full_name",
                "base_salary_vnd": "e.base_salary",
                "total_bonus_vnd": "total_bonus",
                "total_deduction_vnd": "total_deduction",
                "net_amount_vnd": "net_amount"
            }
            db_sort_col = sort_mapping.get(sort_by, "e.employee_id")
            
            db_sort_order = "DESC" if sort_order.upper() == "DESC" else "ASC"

            query = f"""
                SELECT 
                    e.employee_id,
                    e.full_name as employee_name,
                    e.base_salary,
                    
                    -- Tính tổng thưởng trong tháng
                    COALESCE(bd.total_bonus, 0) as total_bonus,
                    
                    -- Tính tổng phạt trong tháng
                    COALESCE(bd.total_deduction, 0) as total_deduction,
                    
                    -- Công thức: Lương cứng + Thưởng - Phạt = Thực nhận (Tạm tính)
                    (e.base_salary + COALESCE(bd.total_bonus, 0) - COALESCE(bd.total_deduction, 0)) as net_amount,
                    
                    -- Kiểm tra trạng thái: Nếu có trong bảng salary_payments thì là 'Paid', không thì là 'Estimated'
                    CASE 
                        WHEN sp.payment_id IS NOT NULL THEN 'Paid'
                        ELSE 'Estimated'
                    END as status
                    
                FROM employees e
                
                -- JOIN 1: Lấy tổng thưởng/phạt theo tháng/năm đang chọn
                LEFT JOIN (
                    SELECT 
                        employee_id, 
                        SUM(CASE WHEN bd_type = 'Bonus' THEN amount ELSE 0 END) as total_bonus,
                        SUM(CASE WHEN bd_type = 'Deduction' THEN amount ELSE 0 END) as total_deduction
                    FROM bonus_deductions
                    WHERE MONTH(effective_date) = %s AND YEAR(effective_date) = %s
                    GROUP BY employee_id
                ) bd ON e.employee_id = bd.employee_id
                
                -- JOIN 2: Kiểm tra xem tháng này đã chốt lương chưa
                LEFT JOIN salary_payments sp 
                    ON e.employee_id = sp.employee_id 
                    AND sp.salary_month = %s AND sp.year = %s
                    
                ORDER BY {db_sort_col} {db_sort_order}
                LIMIT %s OFFSET %s
            """
            # Truyền tham số: (tháng_số, năm, tên_tháng, năm)
            cursor.execute(query, (month_num, year, month, year, limit, offset))
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            raise DatabaseError(f"Query error: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    @staticmethod
    def count_salary_records() -> int:
        conn = None
        cursor = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM employees")
            return cursor.fetchone()[0]
        except mysql.connector.Error:
            return 0
        finally:
            if cursor: cursor.close()
            if conn: conn.close()