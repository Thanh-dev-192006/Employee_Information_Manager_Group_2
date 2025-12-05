import tkinter as tk
from tkinter import ttk, messagebox
from app.models.utils.helpers import parse_display_date, format_display_date, parse_currency_input, validate_salary_vnd, to_db_money, to_vnd, format_currency_vnd

class ProjectDialog(tk.Toplevel):
    def __init__(self, master, managers: dict, mode: str, project: dict | None = None):
        super().__init__(master)
        self.title("Project - " + ("Create" if mode=="create" else "Edit"))
        self.resizable(False, False)

        self.managers = managers
        self.proj_mgr = managers["project"]
        self.dept_mgr = managers["department"]
        self.mode = mode
        self.project = project or {}

        self.departments = self.dept_mgr.get_all_departments()
        self.dept_map = {d["department_name"]: d["department_id"] for d in self.departments}

        self.name = tk.StringVar(value=self.project.get("project_name",""))
        self.start = tk.StringVar(value=format_display_date(self.project.get("start_date")) if self.project.get("start_date") else "")
        self.end = tk.StringVar(value=format_display_date(self.project.get("end_date")) if self.project.get("end_date") else "")
        self.budget = tk.StringVar(value=str(to_vnd(self.project.get("budget",0))) if self.project else "")
        self.dept = tk.StringVar(value=self.project.get("department_name") or (self.departments[0]["department_name"] if self.departments else ""))

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        def row(label, widget, r):
            ttk.Label(body, text=label).grid(row=r, column=0, sticky="w", pady=4)
            widget.grid(row=r, column=1, sticky="ew", pady=4)
        body.columnconfigure(1, weight=1)

        row("Project Name", ttk.Entry(body, textvariable=self.name, width=36), 0)
        row("Start Date (DD/MM/YYYY)", ttk.Entry(body, textvariable=self.start), 1)
        row("End Date (DD/MM/YYYY, optional)", ttk.Entry(body, textvariable=self.end), 2)
        row("Budget (VND)", ttk.Entry(body, textvariable=self.budget), 3)
        row("Department", ttk.Combobox(body, textvariable=self.dept, values=list(self.dept_map.keys()), state="readonly"), 4)

        if self.mode == "edit":
            # backend update_project chỉ cho đổi name + end_date, nên disable start/budget/dept
            for child in body.winfo_children():
                if isinstance(child, ttk.Entry):
                    tv = child.cget("textvariable")
                    if tv in (str(self.start), str(self.budget)):
                        child.state(["disabled"])
                if isinstance(child, ttk.Combobox):
                    child.state(["disabled"])

        btns = ttk.Frame(body)
        btns.grid(row=5, column=0, columnspan=2, sticky="e", pady=(10,0))
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right", padx=6)
        ttk.Button(btns, text="Save", command=self.on_save).pack(side="right")

        self.grab_set()
        self.transient(master)

    def on_save(self):
        try:
            name = self.name.get().strip()
            if not name:
                raise ValueError("Project name cannot be empty")

            if self.mode == "create":
                start_date = parse_display_date(self.start.get())
                end_raw = self.end.get().strip()
                end_date = parse_display_date(end_raw) if end_raw else None

                budget_vnd = parse_currency_input(self.budget.get())
                # dùng validate_salary_vnd làm threshold kiểu “>= 5,000,000” cho budget cũng hợp lý tối thiểu
                validate_salary_vnd(budget_vnd)
                budget_db = to_db_money(budget_vnd)

                dept_id = self.dept_map.get(self.dept.get())
                if not dept_id:
                    raise ValueError("Phòng ban không hợp lệ")

                res = self.proj_mgr.create_project(name, start_date, end_date, budget_db, dept_id)
                messagebox.showinfo("Success", f"Successfully added project ID: {res.get('project_id')}")
            else:
                project_id = int(self.project["project_id"])
                end_raw = self.end.get().strip()
                end_date = parse_display_date(end_raw) if end_raw else None
                res = self.proj_mgr.update_project(project_id, name, end_date)
                messagebox.showinfo("Success", res.get("message","Update OK"))

            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))