# Employee_Information_Manager_Group_2

Desktop application for managing employees, departments, projects, assignments, attendance, salary, and bonus/deductions.

> **Course**: Introduction to Databases  
> **Institution**: National Economics University  
> **Team**: Group 2 (4 members)

---

## Video Demo

[![Xem Video Demo](https://img.youtube.com/vi/tdJsrvs9UFk/0.jpg)](https://youtu.be/tdJsrvs9UFk?si=rzW-GY8Dfs3rAKNu)

> Click vào ảnh trên để xem video demo dự án.

## Tech Stack

- **Python 3.10+**
- **GUI**: ttkbootstrap (Tkinter-based)
- **Database**: MySQL 8.x (InnoDB engine, utf8mb4 charset)
- **Visualization**: Matplotlib
- **Driver**: mysql-connector-python

---

## Repository Structure
```
Employee_Information_Manager_Group_2/
├── app/
│   ├── db/                          # SQL scripts
│   │   ├── 01_schema.sql           # Tables (7 tables)
│   │   ├── 02_seed.sql             # Sample data (161 employees)
│   │   ├── 03_views.sql            # Views (3 views)
│   │   ├── 04_procedures.sql       # Stored procedures (11 procedures)
│   │   └── 05_trigger.sql          # Triggers (3 triggers)
│   │
│   ├── models/                      # Backend managers
│   │   ├── config/
    │   │   │   └── database.py         # Edit credentials here
│   │   ├── manager/                # 8 Manager classes
│   │   │   ├── employee.py
│   │   │   ├── department.py
│   │   │   ├── project.py
│   │   │   ├── assignment.py
│   │   │   ├── attendance.py
│   │   │   ├── salary.py
│   │   │   ├── bonus_deduction.py
│   │   │   └── query.py
│   │   └── utils/
│   │
│   ├── dialogs/                     # Popup forms
│   └── ui/                          # Main screens
│       ├── dashboard.py            # Dashboard with charts
│       ├── employee_screen.py
│       ├── department_screen.py
│       ├── project_screen.py
│       ├── attendance_screen.py
│       ├── salary_screen.py
│       └── queries_screen.py
│
├── main.py                          # Application entry point
├── requirements.txt
└── README.md
```

---

## Setup & Run

### 1. Clone Repository
```bash
git clone <REPO_URL>
cd Employee_Information_Manager_Group_2
```

### 2. Install Python Dependencies

**Windows**:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS/Linux**:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Database

**Step 1**: Edit `app/models/config/database.py`
```python
config = {
    "host": "localhost",
    "user": "root",           #  YOUR USERNAME
    "password": "YOUR_PASS",  #  YOUR PASSWORD
    "database": "employee_manager",
    "charset": "utf8mb4",
    "use_unicode": True,
}
```

**Step 2**: Import SQL scripts (in order)
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS employee_manager CHARACTER SET utf8mb4;"

mysql -u root -p employee_manager < app/db/01_schema.sql
mysql -u root -p employee_manager < app/db/02_seed.sql
mysql -u root -p employee_manager < app/db/03_views.sql
mysql -u root -p employee_manager < app/db/04_procedures.sql
mysql -u root -p employee_manager < app/db/05_trigger.sql
```

> **Important**: Run scripts **in exact order** (01 → 05)

### 4. Run Application
```bash
python main.py
```

---

## Features

### 7 Main Tabs
1. **Dashboard** - KPIs and charts (Matplotlib)
2. **Employees** - CRUD with search/pagination/sorting
3. **Departments** - Department management
4. **Projects** - Project tracking and assignment
5. **Attendance** - Daily check-in/out tracking
6. **Salary** - Monthly salary calculation
7. **Queries** - 4 complex SQL queries + CSV export

### Key Capabilities
- Full CRUD operations for all entities
- Data validation (phone, email, dates, salary)
- Vietnamese text support (utf8mb4)
- Search and filter
- Pagination (15 records/page)
- Sortable tables (click headers)
- CSV export for queries
- Currency display (VND format)

---

## Database Schema

### 7 Tables
- `departments` (7 departments)
- `employees` (160 employees)
- `projects` (10 projects)
- `assignments` (~600 assignments)
- `attendance` (daily records)
- `salary_payments` (monthly records)
- `bonus_deductions` (bonus/penalties)

### Additional Components
- **3 Views**: Optimized queries for salary, attendance, projects
- **11 Stored Procedures**: Business logic validation
- **3 Triggers**: Audit logging for bonus/deductions

---

## Troubleshooting

### MySQL Connection Error
```
Error: Access denied for user 'root'@'localhost'
```
-> Check credentials in `app/models/config/database.py`

### Table Not Found Error
```
Error: Table 'employees' doesn't exist
```
-> Run SQL scripts in order: `01_schema.sql` first

### Vietnamese Text Shows `???`
```
Error: Character encoding issue
```
-> Ensure database uses `utf8mb4`:
```sql
ALTER DATABASE employee_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
```

### GUI Not Showing (WSL)
```
Error: no display name
```
-> Use native Windows Python (not WSL) for Tkinter apps

---

## Dependencies

See `requirements.txt`:
```
ttkbootstrap==1.10.1
mysql-connector-python==8.0.33
matplotlib==3.7.1
numpy==1.24.3
```

---

## License

Educational project for Database Management course.

---

**Last Updated**: December 2024