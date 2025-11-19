DELIMITER $$

DROP PROCEDURE IF EXISTS sp_add_employee $$
CREATE PROCEDURE sp_add_employee (
    IN p_full_name VARCHAR(100),
    IN p_gender ENUM('M','F'),
    IN p_date_of_birth DATE,
    IN p_phone VARCHAR(20),
    IN p_email VARCHAR(100),
    IN p_address VARCHAR(255),
    IN p_hire_date DATE,
    IN p_department_id INT,
    IN p_position VARCHAR(100),
    IN p_base_salary DECIMAL(10,2)
)
BEGIN
    -- 1. Validate Email trùng
    IF EXISTS (SELECT 1 FROM employees WHERE email = p_email) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Email already exists!';
    END IF;

    -- 2. Validate Phone trùng
    IF EXISTS (SELECT 1 FROM employees WHERE phone_number = p_phone) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Phone number already exists!';
    END IF;

    -- 3. Validate Department tồn tại
    IF NOT EXISTS (SELECT 1 FROM departments WHERE department_id = p_department_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Department ID does not exist!';
    END IF;

    -- 4. Validate Hire date (không được ở tương lai)
    IF p_hire_date > CURDATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Hire date cannot be in the future!';
    END IF;

    -- 5. Validate Base salary (> 0)
    IF p_base_salary <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Base salary must be greater than 0!';
    END IF;

    -- Insert sau khi qua tất cả validation
    INSERT INTO employees(full_name, gender, date_of_birth, phone_number, email, address, hire_date, department_id, position, base_salary)
    VALUES(p_full_name, p_gender, p_date_of_birth, p_phone, p_email, p_address, p_hire_date, p_department_id, p_position, p_base_salary);
    
    SELECT LAST_INSERT_ID() AS new_employee_id;
END $$

DROP PROCEDURE IF EXISTS sp_update_employee $$
CREATE PROCEDURE sp_update_employee (
    IN p_emp_id INT,
    IN p_full_name VARCHAR(100),
    IN p_phone VARCHAR(20),
    IN p_email VARCHAR(100),
    IN p_address VARCHAR(255),
    IN p_position VARCHAR(100),
    IN p_base_salary DECIMAL(10,2)
)
BEGIN
    -- Kiểm tra nhân viên tồn tại
    IF NOT EXISTS (SELECT 1 FROM employees WHERE employee_id = p_emp_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Employee not found!';
    END IF;

    -- Validate Email trùng với người KHÁC
    IF EXISTS (SELECT 1 FROM employees WHERE email = p_email AND employee_id != p_emp_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Email already used by another employee!';
    END IF;

    -- Validate Phone trùng với người KHÁC
    IF EXISTS (SELECT 1 FROM employees WHERE phone_number = p_phone AND employee_id != p_emp_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Phone already used by another employee!';
    END IF;

    UPDATE employees
    SET full_name = p_full_name, phone_number = p_phone, email = p_email, 
        address = p_address, position = p_position, base_salary = p_base_salary
    WHERE employee_id = p_emp_id;
END $$

DROP PROCEDURE IF EXISTS sp_delete_employee $$
CREATE PROCEDURE sp_delete_employee (IN p_emp_id INT)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM employees WHERE employee_id = p_emp_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Employee not found!';
    END IF;
    
    DELETE FROM employees WHERE employee_id = p_emp_id;
END $$

DROP PROCEDURE IF EXISTS sp_mark_attendance $$
CREATE PROCEDURE sp_mark_attendance (
    IN p_emp_id INT,
    IN p_work_date DATE,
    IN p_check_in TIME,
    IN p_check_out TIME,
    IN p_status VARCHAR(10)
)
BEGIN
    DECLARE rec_count INT;

    -- 1. Validate Employee tồn tại
    IF NOT EXISTS (SELECT 1 FROM employees WHERE employee_id = p_emp_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Employee does not exist!';
    END IF;

    -- 2. Validate Work date (không được ở tương lai)
    IF p_work_date > CURDATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Cannot mark attendance for future date!';
    END IF;

    -- 3. Validate Logic Check-out > Check-in
    IF p_check_out IS NOT NULL AND p_check_in IS NOT NULL AND p_check_out <= p_check_in THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Check-out time must be after Check-in time!';
    END IF;

    -- Logic Upsert (Update nếu có, Insert nếu chưa)
    SELECT COUNT(*) INTO rec_count 
    FROM attendance 
    WHERE employee_id = p_emp_id AND work_date = p_work_date;

    IF rec_count > 0 THEN
        UPDATE attendance
        SET check_in = p_check_in, check_out = p_check_out, status = p_status
        WHERE employee_id = p_emp_id AND work_date = p_work_date;
        SELECT CONCAT('Attendance record updated for ', p_work_date) AS message;
    ELSE
        INSERT INTO attendance(employee_id, work_date, check_in, check_out, status)
        VALUES(p_emp_id, p_work_date, p_check_in, p_check_out, p_status);
        SELECT CONCAT('Attendance record added for ', p_work_date) AS message;
    END IF;
END $$

DROP PROCEDURE IF EXISTS sp_add_department $$
CREATE PROCEDURE sp_add_department (IN p_dept_name VARCHAR(100), IN p_location VARCHAR(255))
BEGIN
    IF EXISTS (SELECT 1 FROM departments WHERE department_name = p_dept_name) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Department name already exists!';
    END IF;
    
    INSERT INTO departments(department_name, location) VALUES(p_dept_name, p_location);
    SELECT LAST_INSERT_ID() AS new_dept_id;
END $$

DROP PROCEDURE IF EXISTS sp_update_department $$
CREATE PROCEDURE sp_update_department (IN p_dept_id INT, IN p_dept_name VARCHAR(100), IN p_location VARCHAR(255))
BEGIN
    IF NOT EXISTS (SELECT 1 FROM departments WHERE department_id = p_dept_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Department not found!';
    END IF;
    
    UPDATE departments SET department_name = p_dept_name, location = p_location WHERE department_id = p_dept_id;
END $$

DROP PROCEDURE IF EXISTS sp_add_project $$
CREATE PROCEDURE sp_add_project (
    IN p_name VARCHAR(100), 
    IN p_start_date DATE, 
    IN p_end_date DATE, 
    IN p_budget DECIMAL(15,2)
)
BEGIN
    -- Validate End Date >= Start Date
    IF p_end_date < p_start_date THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: End date must be after or equal to Start date!';
    END IF;
    
    INSERT INTO projects(project_name, start_date, end_date, budget) 
    VALUES(p_name, p_start_date, p_end_date, p_budget);
    SELECT LAST_INSERT_ID() AS new_project_id;
END $$

DROP PROCEDURE IF EXISTS sp_update_project $$
CREATE PROCEDURE sp_update_project (
    IN p_proj_id INT, 
    IN p_name VARCHAR(100), 
    IN p_end_date DATE, 
    IN p_status VARCHAR(50)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM projects WHERE project_id = p_proj_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Project not found!';
    END IF;
    
    UPDATE projects SET project_name = p_name, end_date = p_end_date, status = p_status 
    WHERE project_id = p_proj_id;
END $$

DROP PROCEDURE IF EXISTS sp_assign_project $$
CREATE PROCEDURE sp_assign_project (
    IN p_emp_id INT, 
    IN p_proj_id INT, 
    IN p_role VARCHAR(50), 
    IN p_hours DECIMAL(5,2)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM employees WHERE employee_id = p_emp_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Employee not found!';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM projects WHERE project_id = p_proj_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Project not found!';
    END IF;
    
    -- Kiểm tra đã phân công chưa
    IF EXISTS (SELECT 1 FROM assignments WHERE employee_id = p_emp_id AND project_id = p_proj_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Employee already assigned to this project!';
    END IF;
    
    INSERT INTO assignments(employee_id, project_id, role, hours_worked, assigned_date)
    VALUES(p_emp_id, p_proj_id, p_role, p_hours, CURDATE());
END $$

DROP PROCEDURE IF EXISTS sp_add_bonus_deduction $$
CREATE PROCEDURE sp_add_bonus_deduction (
    IN p_emp_id INT,
    IN p_bd_type ENUM('Bonus', 'Deduction'),
    IN p_amount DECIMAL(10,2),
    IN p_desc VARCHAR(255),
    IN p_effective_date DATE
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM employees WHERE employee_id = p_emp_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Employee not found!';
    END IF;
    
    IF p_amount <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Amount must be greater than 0!';
    END IF;
    
    INSERT INTO bonus_deductions(employee_id, bd_type, amount, description, effective_date)
    VALUES(p_emp_id, p_bd_type, p_amount, p_desc, p_effective_date);
END $$

DROP PROCEDURE IF EXISTS sp_record_salary_payment $$
CREATE PROCEDURE sp_record_salary_payment (
    IN p_emp_id INT,
    IN p_month VARCHAR(20),
    IN p_year INT,
    IN p_total DECIMAL(10,2)
)
BEGIN
    -- Kiểm tra trùng lương tháng/năm
    IF EXISTS (SELECT 1 FROM salary_payments WHERE employee_id = p_emp_id AND salary_month = p_month AND year = p_year) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Salary for this month/year already recorded!';
    END IF;
    
    INSERT INTO salary_payments(employee_id, salary_month, year, total_amount, payment_date, payment_status)
    VALUES(p_emp_id, p_month, p_year, p_total, CURDATE(), 'Paid');
END $$

DELIMITER ;