USE employee_manager;

-- Departments
INSERT INTO departments (department_name, location, manager_id) VALUES
('Human Resources', 'Hanoi HQ', NULL),
('Finance', 'Hanoi HQ', NULL),
('IT', 'Hanoi HQ', NULL),
('Sales', 'Ho Chi Minh City', NULL),
('Research and Development', 'Hanoi HQ', NULL);

-- Employees (20 người)
INSERT INTO employees 
(full_name, gender, date_of_birth, phone_number, email, address, hire_date, department_id, position, base_salary) 
VALUES
('Trinh Duc Thanh', 'M', '1985-02-15', '0905123456', 'ducthanh@161Corp.com', 'Hanoi', '2010-06-01', 1, 'HR Manager', 1500.00),
('Do Quang Trung', 'M', '1990-07-30', '0905234567', 'quangtrung@161Corp.com', 'Hanoi', '2015-09-15', 1, 'HR Specialist', 1000.00),
('Vu Ngoc Hai', 'F', '1992-11-20', '0905345678', 'ngochai@161Corp.com', 'Hanoi', '2018-01-20', 1, 'Recruiter', 900.00),
('Nguyen Thanh Lan', 'F', '1980-01-10', '0905456789', 'thanhlan@161Corp.com', 'Hanoi', '2008-04-10', 2, 'Finance Manager', 2000.00),
('Nguyen Trong Dai', 'F', '1995-03-12', '0905567890', 'trongdai@161Corp.com', 'Hanoi', '2019-07-01', 2, 'Accountant', 1200.00),
('Vu Quoc Huy', 'M', '1988-05-05', '0905678901', 'quochuy@161Corp.com', 'Hanoi', '2012-10-05', 2, 'Financial Analyst', 1300.00),
('Duong Dinh Anh', 'M', '1983-12-02', '0912345678', 'dinhanh@161Corp.com', 'Hanoi', '2009-08-17', 3, 'IT Manager', 1800.00),
('Bui Dang Duong', 'F', '1996-04-18', '0912456789', 'dangduong@161Corp.com', 'Hanoi', '2020-03-10', 3, 'Software Engineer', 1500.00),
('Nguyen Tuan Anh', 'M', '1994-09-09', '0912567890', 'tuananh@161Corp.com', 'Hanoi', '2017-11-30', 3, 'System Administrator', 1400.00),
('Tran Van Anh Tuan', 'M', '1998-02-22', '0912678901', 'anhtuan@161Corp.com', 'Hanoi', '2021-06-01', 3, 'Developer', 1300.00),
('Pham Huu Gia An', 'F', '1993-07-07', '0923456789', 'giaan@161Corp.com', 'Ho Chi Minh City', '2016-05-20', 4, 'Sales Manager', 1700.00),
('Hoang Thi Ngoc Han', 'F', '1997-08-15', '0923567890', 'ngochan@161Corp.com', 'Ho Chi Minh City', '2021-09-01', 4, 'Sales Executive', 1100.00),
('Nguyen Quang Huy', 'F', '1991-11-11', '0923678901', 'quanghuy@161Corp.com', 'Ho Chi Minh City', '2014-12-01', 4, 'Sales Representative', 1000.00),
('Phan Dang Vu', 'M', '1985-06-24', '0934567890', 'dangvu@161Corp.com', 'Hanoi', '2010-07-07', 5, 'R&D Manager', 2200.00),
('To Hien Hai Dang', 'F', '1990-10-10', '0934678901', 'haidang@161Corp.com', 'Hanoi', '2016-03-03', 5, 'Research Scientist', 1500.00),
('Nguyen Bao Tai', 'F', '1992-01-19', '0934789012', 'baotai@161Corp.com', 'Hanoi', '2018-07-15', 5, 'Research Analyst', 1400.00),
('Le Duc Minh', 'M', '1987-09-01', '0945678901', 'ducminh@161Corp.com', 'Hanoi', '2013-05-05', 5, 'Product Manager', 2000.00),
('Nguyen Thuy Quynh', 'M', '1996-12-12', '0945789012', 'thuyquynh@161Corp.com', 'Hanoi', '2020-01-20', 5, 'Researcher', 1300.00),
('Nguyen Thi Nhien', 'F', '1999-03-03', '0945890123', 'thinhien@161Corp.com', 'Hanoi', '2022-02-02', 5, 'Research Intern', 800.00),
('Tran Tue Khang', 'M', '1994-05-05', '0945901234', 'tuekhang@161Corp.com', 'Hanoi', '2018-11-11', 3, 'QA Engineer', 1200.00);

-- Gán manager cho phòng ban
UPDATE departments SET manager_id = 1  WHERE department_name = 'Human Resources';
UPDATE departments SET manager_id = 4  WHERE department_name = 'Finance';
UPDATE departments SET manager_id = 7  WHERE department_name = 'IT';
UPDATE departments SET manager_id = 11 WHERE department_name = 'Sales';
UPDATE departments SET manager_id = 14 WHERE department_name = 'Research and Development';

-- Projects (8 dự án)
INSERT INTO projects (project_name, start_date, end_date, budget, department_id) VALUES
('HR System Upgrade',           '2024-01-01', '2024-06-30', 50000.00, 1),
('Employee Onboarding Program', '2025-01-01', NULL,         20000.00, 1),
('Year-End Financial Audit',    '2024-12-01', '2025-01-31', 30000.00, 2),
('IT Infrastructure Upgrade',   '2024-05-15', NULL,        100000.00, 3),
('Website Overhaul',            '2025-02-01', NULL,         25000.00, 3),
('Market Expansion Q1',         '2025-01-15', '2025-03-31', 40000.00, 4),
('AI Research Initiative',      '2024-07-01', NULL,         80000.00, 5),
('Product Prototype Development','2025-03-01', NULL,        60000.00, 5);

-- Assignments (~30 bản ghi)
-- HR projects
INSERT INTO assignments (employee_id, project_id, role, assigned_date, hours_worked) VALUES
(1, 1, 'Project Lead', '2024-01-01', 200),
(2, 1, 'HR Specialist', '2024-01-01', 180),
(3, 1, 'Recruiter', '2024-02-01', 160),
(2, 2, 'Coordinator', '2025-01-05', 20),
(3, 2, 'Coordinator', '2025-01-05', 15);
-- Finance
INSERT INTO assignments (employee_id, project_id, role, assigned_date, hours_worked) VALUES
(4, 3, 'Project Lead', '2024-12-01', 50),
(5, 3, 'Accountant', '2024-12-05', 45),
(6, 3, 'Financial Analyst', '2024-12-10', 40);
-- IT
INSERT INTO assignments (employee_id, project_id, role, assigned_date, hours_worked) VALUES
(7, 4, 'Project Manager', '2024-05-15', 100),
(8, 4, 'Engineer', '2024-05-15', 90),
(9, 4, 'Engineer', '2024-06-01', 80),
(10,4, 'Developer', '2024-06-01', 75),
(20,4, 'QA Engineer', '2024-06-15', 60),
(7, 5, 'Project Manager', '2025-02-01', 20),
(8, 5, 'Developer', '2025-02-01', 18),
(9, 5, 'SysAdmin', '2025-02-01', 15),
(10,5, 'Developer', '2025-02-01', 15),
(20,5, 'QA Engineer', '2025-02-01', 12);
-- Sales
INSERT INTO assignments (employee_id, project_id, role, assigned_date, hours_worked) VALUES
(11,6, 'Project Lead', '2025-01-15', 30),
(12,6, 'Sales Rep', '2025-01-20', 25),
(13,6, 'Sales Rep', '2025-01-20', 20);
-- R&D
INSERT INTO assignments (employee_id, project_id, role, assigned_date, hours_worked) VALUES
(14,7, 'Project Lead', '2024-07-01', 150),
(15,7, 'Researcher', '2024-07-15', 140),
(16,7, 'Researcher', '2024-08-01', 130),
(17,7, 'Product Manager', '2024-09-01', 100),
(18,7, 'Researcher', '2024-09-15', 90),
(14,8, 'Project Lead', '2025-03-01', 20),
(15,8, 'Researcher', '2025-03-01', 18),
(16,8, 'Researcher', '2025-03-01', 15),
(17,8, 'Product Manager', '2025-03-01', 12),
(18,8, 'Researcher', '2025-03-01', 10);

-- Attendance (3 ngày x 20 NV ~ 60 bản ghi)
-- 2025-01-10
INSERT INTO attendance (employee_id, work_date, check_in, check_out, status) VALUES
(1,'2025-01-10','08:30:00','17:30:00','Present'),
(2,'2025-01-10','08:45:00','17:15:00','Present'),
(3,'2025-01-10','08:40:00','17:20:00','Present'),
(4,'2025-01-10','09:00:00','18:00:00','Present'),
(5,'2025-01-10','09:15:00','18:00:00','Present'),
(6,'2025-01-10','08:50:00','17:45:00','Present'),
(7,'2025-01-10','08:30:00','17:30:00','Present'),
(8,'2025-01-10','08:35:00','17:30:00','Present'),
(9,'2025-01-10','08:30:00','17:00:00','Present'),
(10,'2025-01-10','08:30:00','17:30:00','Present'),
(11,'2025-01-10',NULL,NULL,'Absent'),
(12,'2025-01-10','09:00:00','16:00:00','Present'),
(13,'2025-01-10','09:10:00','17:00:00','Present'),
(14,'2025-01-10','08:20:00','17:00:00','Present'),
(15,'2025-01-10','08:25:00','17:10:00','Present'),
(16,'2025-01-10','08:30:00','17:30:00','Present'),
(17,'2025-01-10','08:45:00','17:45:00','Present'),
(18,'2025-01-10','09:00:00','17:00:00','Present'),
(19,'2025-01-10','08:30:00','17:15:00','Present'),
(20,'2025-01-10','08:55:00','17:00:00','Present');

-- 2025-01-11
INSERT INTO attendance (employee_id, work_date, check_in, check_out, status) VALUES
(1,'2025-01-11','08:30:00','17:30:00','Present'),
(2,'2025-01-11','08:45:00','17:15:00','Present'),
(3,'2025-01-11','08:40:00','17:20:00','Present'),
(4,'2025-01-11','09:00:00','18:00:00','Present'),
(5,'2025-01-11','09:15:00','18:00:00','Present'),
(6,'2025-01-11','08:50:00','17:45:00','Present'),
(7,'2025-01-11','08:30:00','17:30:00','Present'),
(8,'2025-01-11','08:35:00','17:30:00','Present'),
(9,'2025-01-11','08:30:00','17:00:00','Present'),
(10,'2025-01-11','08:30:00','17:30:00','Present'),
(11,'2025-01-11','08:25:00','17:00:00','Present'),
(12,'2025-01-11','09:00:00','17:30:00','Present'),
(13,'2025-01-11','09:10:00','17:00:00','Present'),
(14,'2025-01-11',NULL,NULL,'On Leave'),
(15,'2025-01-11','08:25:00','17:10:00','Present'),
(16,'2025-01-11','08:30:00','17:30:00','Present'),
(17,'2025-01-11','08:45:00','17:45:00','Present'),
(18,'2025-01-11','09:00:00','17:00:00','Present'),
(19,'2025-01-11','08:30:00','17:15:00','Present'),
(20,'2025-01-11','08:55:00','17:00:00','Present');

-- 2025-01-12
INSERT INTO attendance (employee_id, work_date, check_in, check_out, status) VALUES
(1,'2025-01-12','08:30:00','12:00:00','Present'),
(2,'2025-01-12','08:45:00','12:00:00','Present'),
(3,'2025-01-12','08:40:00','12:00:00','Present'),
(4,'2025-01-12','09:00:00','12:00:00','Present'),
(5,'2025-01-12','09:15:00','12:00:00','Present'),
(6,'2025-01-12','08:50:00','12:00:00','Present'),
(7,'2025-01-12',NULL,NULL,'Absent'),
(8,'2025-01-12','08:35:00','12:00:00','Present'),
(9,'2025-01-12','08:30:00','12:00:00','Present'),
(10,'2025-01-12','08:30:00','12:00:00','Present'),
(11,'2025-01-12','08:25:00','12:00:00','Present'),
(12,'2025-01-12','09:00:00','12:00:00','Present'),
(13,'2025-01-12','09:10:00','12:00:00','Present'),
(14,'2025-01-12','08:20:00','12:00:00','Present'),
(15,'2025-01-12','08:25:00','12:00:00','Present'),
(16,'2025-01-12','08:30:00','12:00:00','Present'),
(17,'2025-01-12','08:45:00','12:00:00','Present'),
(18,'2025-01-12','09:00:00','12:00:00','Present'),
(19,'2025-01-12',NULL,NULL,'On Leave'),
(20,'2025-01-12','08:55:00','12:00:00','Present');

-- Salary payments (2 tháng x 20 NV)
INSERT INTO salary_payments (employee_id, payment_date, salary_month, year, total_amount, payment_status) VALUES
(1,'2025-01-31','January',2025,1500.00,'Paid'),
(2,'2025-01-31','January',2025,1000.00,'Paid'),
(3,'2025-01-31','January',2025,900.00,'Paid'),
(4,'2025-01-31','January',2025,2000.00,'Paid'),
(5,'2025-01-31','January',2025,1200.00,'Paid'),
(6,'2025-01-31','January',2025,1300.00,'Paid'),
(7,'2025-01-31','January',2025,1800.00,'Paid'),
(8,'2025-01-31','January',2025,1500.00,'Paid'),
(9,'2025-01-31','January',2025,1400.00,'Paid'),
(10,'2025-01-31','January',2025,1300.00,'Paid'),
(11,'2025-01-31','January',2025,1700.00,'Paid'),
(12,'2025-01-31','January',2025,1100.00,'Paid'),
(13,'2025-01-31','January',2025,1000.00,'Paid'),
(14,'2025-01-31','January',2025,2200.00,'Paid'),
(15,'2025-01-31','January',2025,1500.00,'Paid'),
(16,'2025-01-31','January',2025,1400.00,'Paid'),
(17,'2025-01-31','January',2025,2000.00,'Paid'),
(18,'2025-01-31','January',2025,1300.00,'Paid'),
(19,'2025-01-31','January',2025,800.00,'Paid'),
(20,'2025-01-31','January',2025,1200.00,'Paid');

INSERT INTO salary_payments (employee_id, payment_date, salary_month, year, total_amount, payment_status) VALUES
(1,'2025-02-28','February',2025,1500.00,'Paid'),
(2,'2025-02-28','February',2025,1000.00,'Paid'),
(3,'2025-02-28','February',2025,900.00,'Paid'),
(4,'2025-02-28','February',2025,2000.00,'Paid'),
(5,'2025-02-28','February',2025,1200.00,'Paid'),
(6,'2025-02-28','February',2025,1300.00,'Paid'),
(7,'2025-02-28','February',2025,1800.00,'Paid'),
(8,'2025-02-28','February',2025,1500.00,'Paid'),
(9,'2025-02-28','February',2025,1400.00,'Paid'),
(10,'2025-02-28','February',2025,1300.00,'Paid'),
(11,'2025-02-28','February',2025,1700.00,'Pending'),
(12,'2025-02-28','February',2025,1100.00,'Pending'),
(13,'2025-02-28','February',2025,1000.00,'Pending'),
(14,'2025-02-28','February',2025,2200.00,'Pending'),
(15,'2025-02-28','February',2025,1500.00,'Pending'),
(16,'2025-02-28','February',2025,1400.00,'Pending'),
(17,'2025-02-28','February',2025,2000.00,'Unpaid'),
(18,'2025-02-28','February',2025,1300.00,'Pending'),
(19,'2025-02-28','February',2025,800.00,'Pending'),
(20,'2025-02-28','February',2025,1200.00,'Pending');

-- Bonus / Deductions (20 bản ghi)
INSERT INTO bonus_deductions (employee_id, description, bd_type, amount, effective_date) VALUES
(1,'Year-end performance bonus','Bonus',200.00,'2025-01-15'),
(4,'Late submission penalty','Deduction',50.00,'2025-01-10'),
(4,'Overtime bonus','Bonus',100.00,'2025-01-20'),
(5,'Excellent report bonus','Bonus',150.00,'2025-02-05'),
(7,'Project success bonus','Bonus',300.00,'2025-02-10'),
(8,'Security policy violation','Deduction',100.00,'2025-01-05'),
(8,'Overtime bonus','Bonus',100.00,'2025-01-25'),
(10,'Project delay penalty','Deduction',80.00,'2025-02-01'),
(11,'Exceeded sales target','Bonus',250.00,'2025-02-15'),
(12,'Client complaint penalty','Deduction',40.00,'2025-01-18'),
(14,'Patent award bonus','Bonus',500.00,'2025-01-30'),
(15,'Research grant bonus','Bonus',300.00,'2025-02-20'),
(15,'Missed deadline penalty','Deduction',60.00,'2025-02-10'),
(16,'Conference presentation bonus','Bonus',200.00,'2025-02-25'),
(17,'Prototype delay penalty','Deduction',100.00,'2025-03-10'),
(17,'Innovation bonus','Bonus',400.00,'2025-03-05'),
(18,'Exceeded research goals','Bonus',250.00,'2025-02-28'),
(19,'Internship completion bonus','Bonus',50.00,'2025-01-31'),
(20,'QA bug miss penalty','Deduction',30.00,'2025-01-20'),
(20,'Quality improvement bonus','Bonus',120.00,'2025-02-15');