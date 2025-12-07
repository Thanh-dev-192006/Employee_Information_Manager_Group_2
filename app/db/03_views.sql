USE employee_manager;

-- ============================================================
-- 1. SỬA LỖI PROJECT (v_project_participation)
-- Lỗi hiển thị ở ảnh 1 và 2
-- ============================================================
DROP VIEW IF EXISTS v_project_participation;

CREATE VIEW v_project_participation AS
SELECT 
    p.project_id,
    p.project_name,
    COUNT(DISTINCT a.employee_id) AS total_employees,
    -- Dùng COALESCE để tránh lỗi NULL khi cộng
    COALESCE(SUM(a.hours_worked), 0) AS total_hours_worked 
FROM projects p
-- Quan trọng: Dùng LEFT JOIN để hiển thị cả dự án chưa có nhân viên (Sửa lỗi mất data)
LEFT JOIN assignments a ON p.project_id = a.project_id 
GROUP BY p.project_id, p.project_name;


-- ============================================================
-- 2. SỬA LỖI CHẤM CÔNG (v_employee_attendance)
-- Lỗi hiển thị ở ảnh 3 (mới nhất)
-- ============================================================
DROP VIEW IF EXISTS v_employee_attendance;

CREATE VIEW v_employee_attendance AS
SELECT 
    a.work_date,
    e.employee_id,
    e.full_name AS employee_name,
    d.department_name,
    a.status,
    a.check_in,
    a.check_out
FROM attendance a
JOIN employees e ON a.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id;


-- ============================================================
-- 3. TẠO VIEW LƯƠNG (v_monthly_salary_summary)
-- Tạo trước để tránh lỗi tiếp theo khi bạn bấm vào tab "Lương"
-- ============================================================
DROP VIEW IF EXISTS v_monthly_salary_summary;

CREATE VIEW v_monthly_salary_summary AS
SELECT 
    e.employee_id,
    e.full_name AS employee_name,
    sp.salary_month,
    sp.year,
    e.base_salary,
    COALESCE(bd.total_bonus, 0) AS total_bonus,
    COALESCE(bd.total_deduction, 0) AS total_deduction,
    (e.base_salary + COALESCE(bd.total_bonus, 0) - COALESCE(bd.total_deduction, 0)) AS net_amount,
    sp.total_amount AS recorded_payment,
    sp.payment_status
FROM employees e
JOIN salary_payments sp ON e.employee_id = sp.employee_id
LEFT JOIN (
    SELECT 
        employee_id, 
        YEAR(effective_date) AS bd_year,
        MONTH(effective_date) AS bd_month,  
        SUM(CASE WHEN bd_type = 'Bonus' THEN amount ELSE 0 END) AS total_bonus,
        SUM(CASE WHEN bd_type = 'Deduction' THEN amount ELSE 0 END) AS total_deduction
    FROM bonus_deductions
    GROUP BY employee_id, YEAR(effective_date), MONTH(effective_date)
) bd ON e.employee_id = bd.employee_id 
    AND sp.year = bd.bd_year 
    AND (CASE sp.salary_month  
            WHEN 'January' THEN 1 WHEN 'February' THEN 2 WHEN 'March' THEN 3
            WHEN 'April' THEN 4 WHEN 'May' THEN 5 WHEN 'June' THEN 6
            WHEN 'July' THEN 7 WHEN 'August' THEN 8 WHEN 'September' THEN 9
            WHEN 'October' THEN 10 WHEN 'November' THEN 11 WHEN 'December' THEN 12
        END) = bd.bd_month;