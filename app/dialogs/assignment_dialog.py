import tkinter as tk
from tkinter import ttk, messagebox

class AssignmentDialog(tk.Toplevel):
    def __init__(self, master, managers: dict, project_id: int):
        super().__init__(master)
        self.title("Employee Assignment")
        self.resizable(False, False)

        self.assign_mgr = managers["assignment"]
        self.emp_mgr = managers["employee"]
        self.project_id = project_id

        self.emps = self.emp_mgr.get_all_employees(limit=10000, offset=0)
        self.emp_map = {f'{e["employee_id"]} - {e["full_name"]}': e["employee_id"] for e in self.emps}
        self.search_list = list(self.emp_map.keys())

        self.emp_var = tk.StringVar(value="")
        
        self.role = tk.StringVar(value="")
        self.hours = tk.StringVar(value="")

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="Select Employee (Type to search)").grid(row=0, column=0, sticky="w", pady=4)
        
        self.cb_emp = ttk.Combobox(
            body, 
            textvariable=self.emp_var, 
            values=self.search_list, 
            width=36,
            height=15  
        )
        self.cb_emp.grid(row=0, column=1, sticky="ew", pady=4)
        
        self.cb_emp.bind('<KeyRelease>', self.on_key_release)
        
        self.cb_emp.bind('<Return>', self.on_enter)

        ttk.Label(body, text="Role").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.role).grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Hours Worked (hours_worked)").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.hours).grid(row=2, column=1, sticky="ew", pady=4)

        btns = ttk.Frame(body)
        btns.grid(row=3, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right", padx=6)
        ttk.Button(btns, text="Save", command=self.on_save).pack(side="right")

        body.columnconfigure(1, weight=1)
        self.grab_set()
        self.transient(master)

    def on_key_release(self, event):
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Return', 'Tab', 'Escape']:
            return

        typed = self.cb_emp.get()
        
        if typed == '':
            data = self.search_list
        else:
            data = [item for item in self.search_list if typed.lower() in item.lower()]

        self.cb_emp['values'] = data

    def on_enter(self, event):
        try:
            self.cb_emp.tk.call('ttk::combobox::Post', self.cb_emp._w)
        except:
            pass

    def on_save(self):
        try:
            selected_text = self.emp_var.get()
            emp_id = self.emp_map.get(selected_text)
            
            if not emp_id:
                raise ValueError("Nhân viên không hợp lệ. Vui lòng chọn từ danh sách.")

            role = self.role.get().strip()
            if not role:
                raise ValueError("Role cannot be empty")

            try:
                hours = float(self.hours.get().strip())
            except ValueError:
                raise ValueError("Hours worked must be a number")

            if hours < 0:
                raise ValueError("Hours worked cannot be negative")

            res = self.assign_mgr.create_assignment(emp_id, self.project_id, role, hours)
            messagebox.showinfo("Success", res.get("message","Assignment OK"))
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))