import mysql.connector

class DatabaseConnection:
    @staticmethod
    def get_connection():
        config = {
            "host": "localhost",
            "user": "root",  # Tên user MySQL của bạn
            "password": "T&t121106",   # Sửa lại mật khẩu trước khi chạy
            "database": "employee_manager",
            "charset": "utf8mb4",
            "use_unicode": True,
        }
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci")
        cursor.close()
        return conn
