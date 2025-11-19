-- View 1: Tổng hợp lương tháng (kèm thưởng/phạt)
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
        YEAR(effective_date) AS log_year,
        MONTHNAME(effective_date) AS log_month,
        SUM(CASE WHEN bd_type = 'Bonus' THEN amount ELSE 0 END) AS total_bonus,
        SUM(CASE WHEN bd_type = 'Deduction' THEN amount ELSE 0 END) AS total_deduction
    FROM bonus_deductions
    GROUP BY employee_id, YEAR(effective_date), MONTHNAME(effective_date)
) bd ON e.employee_id = bd.employee_id 
    AND sp.year = bd.log_year 
    AND sp.salary_month = bd.log_month;

-- View 2: Tham gia dự án
CREATE VIEW v_project_participation AS
SELECT 
    p.project_id,
    p.project_name,
    COUNT(DISTINCT a.employee_id) AS total_employees,
    SUM(a.hours_worked) AS total_hours_worked
FROM projects p
JOIN assignments a ON p.project_id = a.project_id
GROUP BY p.project_id, p.project_name;

-- View 3: Lịch sử chấm công
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