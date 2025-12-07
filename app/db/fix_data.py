import mysql.connector
import random

# --- CẤU HÌNH KẾT NỐI ---
config = {
    "host": "localhost",
    "user": "root",
    "password": "T&t121106",  # Nhớ kiểm tra lại mật khẩu của bạn
    "database": "employee_manager"
}

def seed_assignments_v2():
    conn = None
    try:
        print("Đang kết nối database...")
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # 1. Lấy danh sách ID
        cursor.execute("SELECT employee_id FROM employees")
        emp_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT project_id FROM projects")
        proj_ids = [row[0] for row in cursor.fetchall()]
        
        if not emp_ids or not proj_ids:
            print("LỖI: Không tìm thấy dữ liệu Nhân viên hoặc Dự án.")
            return

        # 2. Xóa dữ liệu cũ để tránh lỗi trùng lặp
        print("Đang làm sạch bảng assignments...")
        cursor.execute("DELETE FROM assignments")
        conn.commit()

        # 3. Sinh dữ liệu: MỤC TIÊU 450 BẢN GHI
        roles = ['Developer', 'Tester', 'Project Manager', 'Designer', 'Business Analyst', 'DevOps', 'Consultant', 'Architect']
        target_count = 450
        current_count = 0
        
        print(f"Đang sinh {target_count} bản ghi phân công...")
        
        while current_count < target_count:
            # Chọn ngẫu nhiên
            emp = random.choice(emp_ids)
            proj = random.choice(proj_ids)
            role = random.choice(roles)
            hours = random.randint(10, 300) # Giờ làm việc phong phú hơn
            
            # Ngày ngẫu nhiên trong năm 2024-2025
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            year = random.choice([2024, 2025])
            date_str = f"{year}-{month:02d}-{day:02d}"

            query = """
                INSERT INTO assignments (employee_id, project_id, role, assigned_date, hours_worked) 
                VALUES (%s, %s, %s, %s, %s)
            """
            try:
                cursor.execute(query, (emp, proj, role, date_str, hours))
                current_count += 1
                # In tiến độ mỗi 50 dòng
                if current_count % 50 == 0:
                    print(f"-> Đã tạo {current_count}/{target_count}...")
            except mysql.connector.Error as err:
                # Nếu gặp lỗi trùng lặp (1 nhân viên đã ở trong dự án đó rồi) -> Bỏ qua và thử lại
                if err.errno == 1062: # Duplicate entry
                    continue
                else:
                    print(f"Lỗi khác: {err}")

        conn.commit()
        print(f"=== THÀNH CÔNG ===")
        print(f"Tổng số bản ghi assignments hiện tại: {current_count}")
        
    except mysql.connector.Error as err:
        print(f"Lỗi kết nối: {err}")
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    seed_assignments_v2()