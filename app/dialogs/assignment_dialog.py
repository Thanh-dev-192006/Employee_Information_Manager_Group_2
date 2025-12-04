import tkinter as tk
from tkinter import ttk, messagebox

class AssignmentDialog(tk.Toplevel):
    def __init__(self, master, managers: dict, project_id: int):
        super().__init__(master)
        self.title("Phân công nhân viên")
        self.resizable(False, False)

        self.assign_mgr = managers["assignment"]
        self.emp_mgr = managers["employee"]
        self.project_id = project_id

        self.emps = self.emp_mgr.get_all_employees(limit=None, offset=0)
        self.emp_map = {f'{e["employee_id"]} - {e["full_name"]}': e["employee_id"] for e in self.emps}

        self.emp = tk.StringVar(value=(next(iter(self.emp_map.keys())) if self.emp_map else ""))
        self.role = tk.StringVar(value="Member")
        self.hours = tk.StringVar(value="8")

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="Chọn nhân viên").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Combobox(body, textvariable=self.emp, values=list(self.emp_map.keys()), state="readonly", width=36)\
            .grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Vai trò").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.role).grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Giờ làm (hours_worked)").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.hours).grid(row=2, column=1, sticky="ew", pady=4)

        btns = ttk.Frame(body)
        btns.grid(row=3, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Hủy", command=self.destroy).pack(side="right", padx=6)
        ttk.Button(btns, text="Lưu", command=self.on_save).pack(side="right")

        body.columnconfigure(1, weight=1)
        self.grab_set()
        self.transient(master)

    def on_save(self):
        try:
            emp_id = self.emp_map.get(self.emp.get())
            if not emp_id:
                raise ValueError("Nhân viên không hợp lệ")

            role = self.role.get().strip()
            if not role:
                raise ValueError("Vai trò không được trống")

            try:
                hours = float(self.hours.get().strip())
            except ValueError:
                raise ValueError("Giờ làm phải là số")

            if hours < 0 or hours > 24:
                raise ValueError("Giờ làm phải từ 0-24")

            res = self.assign_mgr.create_assignment(emp_id, self.project_id, role, hours)
            messagebox.showinfo("OK", res.get("message","Phân công OK"))
            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))