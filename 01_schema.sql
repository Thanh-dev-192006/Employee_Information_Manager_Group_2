-- Tạo cơ sở dữ liệu và sử dụng
CREATE DATABASE IF NOT EXISTS employee_manager;
USE employee_manager;

-- Bảng DEPARTMENTS: Phòng ban
CREATE TABLE departments (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    location        VARCHAR(100),
    manager_id      INT DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng EMPLOYEES: Nhân viên
CREATE TABLE employees (
    employee_id    INT AUTO_INCREMENT PRIMARY KEY,
    full_name      VARCHAR(100) NOT NULL,
    gender         ENUM('M','F') NOT NULL,
    date_of_birth  DATE,
    phone_number   VARCHAR(20) UNIQUE,
    email          VARCHAR(100) NOT NULL UNIQUE,
    address        VARCHAR(255),
    hire_date      DATE NOT NULL,
    department_id  INT NOT NULL,
    position       VARCHAR(100),
    base_salary    DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_employee_dept 
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng PROJECTS: Dự án
CREATE TABLE projects (
    project_id    INT AUTO_INCREMENT PRIMARY KEY,
    project_name  VARCHAR(100) NOT NULL,
    start_date    DATE,
    end_date      DATE,
    budget        DECIMAL(15,2),
    department_id INT NOT NULL,
    CONSTRAINT fk_project_dept 
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng ASSIGNMENTS: Phân công nhân viên vào dự án
CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id   INT NOT NULL,
    project_id    INT NOT NULL,
    role          VARCHAR(100),
    assigned_date DATE,
    hours_worked  INT DEFAULT 0,
    CONSTRAINT fk_assign_emp 
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    CONSTRAINT fk_assign_proj 
        FOREIGN KEY (project_id) REFERENCES projects(project_id),
    CONSTRAINT u_emp_proj UNIQUE (employee_id, project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng ATTENDANCE: Chấm công theo ngày
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id   INT NOT NULL,
    work_date     DATE NOT NULL,
    check_in      TIME,
    check_out     TIME,
    status        ENUM('Present','Absent','On Leave') NOT NULL,
    CONSTRAINT fk_attendance_emp 
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    CONSTRAINT u_emp_date UNIQUE (employee_id, work_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng SALARY_PAYMENTS: Thanh toán lương hàng tháng
CREATE TABLE salary_payments (
    payment_id     INT AUTO_INCREMENT PRIMARY KEY,
    employee_id    INT NOT NULL,
    payment_date   DATE NOT NULL,
    salary_month   VARCHAR(20) NOT NULL,      -- VD: 'January', 'February'
    year           INT NOT NULL,
    total_amount   DECIMAL(10,2) NOT NULL,
    payment_status ENUM('Unpaid','Paid','Pending') DEFAULT 'Pending',
    CONSTRAINT fk_salary_emp 
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
	CONSTRAINT u_emp_month_year UNIQUE (employee_id, salary_month, year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng BONUS_DEDUCTIONS: Thưởng / Phạt
CREATE TABLE bonus_deductions (
    bd_id         INT AUTO_INCREMENT PRIMARY KEY,
    employee_id   INT NOT NULL,
    description   VARCHAR(255),
    bd_type       ENUM('Bonus','Deduction') NOT NULL,
    amount        DECIMAL(10,2) NOT NULL,
    effective_date DATE NOT NULL,
    CONSTRAINT fk_bd_emp 
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng BONUS_DEDUCTION_LOG: Log thưởng/phạt
CREATE TABLE bonus_deduction_log (
    log_id        	INT AUTO_INCREMENT PRIMARY KEY,
    bd_id         	INT,
    employee_id   	INT,
    description   	VARCHAR(255),
    bd_type       	ENUM('Bonus','Deduction'),
    action        	VARCHAR(20) DEFAULT 'INSERT',
    amount        	DECIMAL(10,2),
    old_amount    	DECIMAL(10,2) NULL,
    effective_date 	DATE,
    log_time      	DATETIME,
    INDEX idx_bd_id (bd_id),
    INDEX idx_employee_id (employee_id),
    INDEX idx_log_time (log_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Khóa ngoại manager_id cho departments (sau khi đã có employees)
ALTER TABLE departments 
    ADD CONSTRAINT fk_dept_manager 
        FOREIGN KEY (manager_id) REFERENCES employees(employee_id);