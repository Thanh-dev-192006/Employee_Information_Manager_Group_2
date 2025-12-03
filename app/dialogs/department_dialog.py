import tkinter as tk
from tkinter import ttk, messagebox

class DepartmentDialog(tk.Toplevel):
    def __init__(self, master, dept_mgr, mode: str, dept: dict | None = None):
        super().__init__(master)
        self.title("Phòng ban - " + ("Thêm" if mode == "create" else "Sửa"))
        self.resizable(False, False)

        self.dept_mgr = dept_mgr
        self.mode = mode
        self.dept = dept or {}

        self.name = tk.StringVar(value=self.dept.get("department_name",""))
        self.loc = tk.StringVar(value=self.dept.get("location",""))

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="Tên phòng ban").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.name, width=35).grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Label(body, text="Địa điểm").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.loc, width=35).grid(row=1, column=1, sticky="ew", pady=4)

        btns = ttk.Frame(body)
        btns.grid(row=2, column=0, columnspan=2, sticky="e", pady=(10,0))
        ttk.Button(btns, text="Hủy", command=self.destroy).pack(side="right", padx=6)
        ttk.Button(btns, text="Lưu", command=self.on_save).pack(side="right")

        self.grab_set()
        self.transient(master)

    def on_save(self):
        try:
            name = self.name.get().strip()
            loc = self.loc.get().strip()
            if not name:
                raise ValueError("Tên phòng ban không được trống")

            if self.mode == "create":
                res = self.dept_mgr.create_department(name, loc)
                messagebox.showinfo("OK", f"Đã thêm phòng ban ID: {res.get('department_id')}")
            else:
                dept_id = int(self.dept["department_id"])
                res = self.dept_mgr.update_department(dept_id, name, loc)
                messagebox.showinfo("OK", res.get("message","Cập nhật OK"))

            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))