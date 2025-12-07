import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.models.manager.employee import EmployeeManager
from app.models.manager.department import DepartmentManager
from app.models.manager.project import ProjectManager
from app.models.manager.assignment import AssignmentManager
from app.models.manager.attendance import AttendanceManager
from app.models.manager.salary import SalaryManager
from app.models.manager.bonus_deduction import BonusDeductionManager
from app.models.manager.query import QueryManager
 

from app.ui.employee_screen import EmployeeScreen
from app.ui.department_screen import DepartmentScreen
from app.ui.project_screen import ProjectScreen
from app.ui.attendance_screen import AttendanceScreen
from app.ui.salary_screen import SalaryScreen
from app.ui.queries_screen import QueriesScreen
from app.ui.dashboard import Dashboard 

import mysql.connector
import random

# --- CONNECTION CONFIGURATION ---
config = {
    "host": "localhost",
    "user": "root",           # Your username
    "password": "T&t121106",  # Update your password before running
    "database": "employee_manager"
}

def seed_assignments_v2():
    conn = None
    try:
        print("Connecting database...")
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT employee_id FROM employees")
        emp_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT project_id FROM projects")
        proj_ids = [row[0] for row in cursor.fetchall()]
        
        if not emp_ids or not proj_ids:
            print("ERROR: Not found employees or projects.")
            return

        cursor.execute("DELETE FROM assignments")
        conn.commit()

        roles = ['Developer', 'Tester', 'Project Manager', 'Designer', 'Business Analyst', 'DevOps', 'Consultant', 'Architect']
        target_count = 450
        current_count = 0
        
        print(f"Generating {target_count} assignment records...")
        
        while current_count < target_count:
            emp = random.choice(emp_ids)
            proj = random.choice(proj_ids)
            role = random.choice(roles)
            hours = random.randint(10, 300)
            
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
                if current_count % 50 == 0:
                    print(f"-> Created {current_count}/{target_count}...")
            except mysql.connector.Error as err:
                if err.errno == 1062: # Duplicate entry
                    continue
                else:
                    print(f"Other error: {err}")

        conn.commit()
        print(f"=== Success ===")
        print(f"Total number of assignment records: {current_count}")
        
    except mysql.connector.Error as err:
        print(f"Connection error: {err}")
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    seed_assignments_v2()

class App(ttk.Window):
    def __init__(self):
        # Chọn theme ở đây ("litera", "cosmo", "flatly", "journal")
        super().__init__(themename="litera")

        style = ttk.Style()
        style.configure("Treeview", 
                        font=("Segoe UI", 11), 
                        rowheight=53)
        
        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 12, "bold"))

        self.title("Employee Information Manager - 161Corp")
        self.geometry("1280x800")

        

        # 7 managers
        self.managers = {
            "employee": EmployeeManager(),
            "department": DepartmentManager(),
            "project": ProjectManager(),
            "assignment": AssignmentManager(),
            "attendance": AttendanceManager(),
            "salary": SalaryManager(),
            "bonus_deduction": BonusDeductionManager(),
            "query": QueryManager(),
        }

        self._build_menu()
        self.container = ttk.Frame(self, padding=0)
        self.container.pack(fill="both", expand=True)

        self.screens = {}
        self._init_screens()

        self.show("dashboard")

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        def add(label, key):
            menubar.add_command(label=label, command=lambda: self.show(key))

        add("Dashboard", "dashboard")
        add("Employee", "employee")
        add("Department", "department")
        add("Project", "project")
        add("Attendance", "attendance")
        add("Salary", "salary")
        add("Queries", "queries")

    def _init_screens(self):
        
        
        self.screens["dashboard"] = Dashboard(self.container, self.managers) 


        self.screens["employee"] = EmployeeScreen(self.container, self.managers)
        self.screens["department"] = DepartmentScreen(self.container, self.managers)
        self.screens["project"] = ProjectScreen(self.container, self.managers)
        self.screens["attendance"] = AttendanceScreen(self.container, self.managers)
        self.screens["salary"] = SalaryScreen(self.container, self.managers)
        self.screens["queries"] = QueriesScreen(self.container, self.managers)

        for f in self.screens.values():
            f.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show(self, key: str):
        screen = self.screens.get(key)
        if screen:
            screen.tkraise()
            if key == "dashboard" and hasattr(screen, "refresh_dashboard"):
                screen.refresh_dashboard()

if __name__ == "__main__":
    App().mainloop()