# Employee_Information_Manager_Group_2
A desktop application (Python / Tkinter + **ttkbootstrap**) to manage **Employees, Departments, Projects, Assignments, Attendance, and Bonus/Deduction**.  
Includes an **Analytics / Queries** tab with **CSV Export** for data analysis and reporting.

> This README is for the **code repository** (how to build/run/demo). The academic report (Overleaf) is a separate document.

---

## 1) Features (aligned with current code)
- CRUD for **Employees / Departments / Projects / Assignments / Attendance / Bonus–Deduction**
- Validations (e.g., **hours 0–24**, required fields)
- UX niceties: default date = **today** in dialogs
- **Queries** tab with four predefined queries:
  1) INNER JOIN — Employee–Project (role, salary)
  2) LEFT JOIN — All employees (including those without projects)
  3) Multi-table — Employee–Project–**Manager**
  4) Analytic — Employees whose **average assignment salary** is above the **global assignment average**
- **Export to CSV** from the Queries tab

---

## 2) Tech Stack
- **Python 3.10+**
- GUI: **Tkinter** (stdlib) + **ttkbootstrap**
- Database: **MySQL 8.x**
- MySQL driver: **mysql-connector-python**

---

## 3) Repository Layout (key files in this project)
```
main.py                      # Application entry point
queries_screen.py            # GUI for Queries + CSV Export
employee.py / department.py / project.py / assignment.py / attendance.py / bonus_deduction.py / salary.py
query.py                     # QueryManager (4 queries + CSV export)
database.py / connection.py  # MySQL connection (edit credentials here)
helpers.py / exceptions.py   # Utilities & custom exceptions

01_schema.sql                # CREATE DATABASE + tables (USE employee_manager)
02_seed.sql                  # Sample data
03_views.sql                 # Database views
04_procedures.sql            # Stored procedures
05_trigger.sql               # Triggers
```

> Note: `database.py` currently contains **hard-coded** credentials. Update them to match your local MySQL setup.

---

## 4) Setup

### 4.1 Clone
```bash
git clone <REPO_URL>
cd <repo-folder>
```

### 4.2 Python virtual environment
**Windows (PowerShell):**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**macOS/Linux (Terminal):**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3 Configure MySQL
1) **Edit credentials** in `database.py` (host, user, password, database). Default DB name in scripts: `employee_manager`.
2) Create DB and import scripts **in order**:
```bash
mysql -u <user> -p -e "CREATE DATABASE IF NOT EXISTS employee_manager CHARACTER SET utf8mb4;"
mysql -u <user> -p employee_manager < 01_schema.sql
mysql -u <user> -p employee_manager < 02_seed.sql
mysql -u <user> -p employee_manager < 03_views.sql
mysql -u <user> -p employee_manager < 04_procedures.sql
mysql -u <user> -p employee_manager < 05_trigger.sql
```
> Ensure your MySQL server is running (default host `localhost`, port `3306`).

---

## 5) Run
From the repository root (with venv activated):
```bash
python main.py
```

If you use a different entrypoint path in your repo layout, adjust accordingly.

---

## 6) Queries Tab & CSV Export (for demo / Slide 7)
Open the **Queries** tab in the app, choose one of the predefined options, click **Run**, then **Export CSV** to save results.

**Analytic query (#4) per assignment (average *assignment* salary > global average):**
```sql
WITH emp_avg AS (
  SELECT a.employee_id, AVG(a.salary) AS avg_salary
  FROM assignments a
  GROUP BY a.employee_id
),
global_avg AS (
  SELECT AVG(salary) AS g_avg FROM assignments
)
SELECT e.employee_id, e.full_name, d.department_name, emp_avg.avg_salary
FROM emp_avg
CROSS JOIN global_avg
JOIN employees e ON e.employee_id = emp_avg.employee_id
LEFT JOIN departments d ON d.department_id = e.department_id
WHERE emp_avg.avg_salary > global_avg.g_avg
ORDER BY emp_avg.avg_salary DESC;
```

> The other three queries (INNER JOIN, LEFT JOIN, Multi-table with Manager) are implemented in `query.py` and invoked by `queries_screen.py`.

**Screenshot tip:** resize columns to show **Name / Department / Salary** clearly and capture ~10–15 rows.

---

## 7) Troubleshooting
- **MySQL connection error** → re-check credentials in `database.py`; test with `mysql -u <user> -p`; ensure DB exists.
- **GUI doesn’t appear on WSL** → use native Windows Python instead of WSL for Tkinter.
- **CSV encoding** → use UTF‑8; in Excel, import via *Data → From Text/CSV* if needed.

---

## 8) License
Coursework project for educational purposes.