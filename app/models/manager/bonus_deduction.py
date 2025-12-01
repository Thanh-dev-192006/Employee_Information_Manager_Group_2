from typing import List, Dict, Optional
from datetime import date
import mysql.connector

from ..config.database import DatabaseConnection
from ..utils.helpers import parse_stored_procedure_error
from ..utils.exceptions import *

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