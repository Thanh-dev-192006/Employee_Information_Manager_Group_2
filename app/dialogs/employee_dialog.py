import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

try:
    from app.models.utils.exceptions import ValidationError
except Exception:
    ValidationError = Exception

from app.models.utils.helpers import (
    ensure_email_domain, parse_display_date, format_display_date,
    parse_currency_input, format_currency_vnd, to_db_money, to_vnd,
    validate_phone, validate_hire_date, validate_salary_vnd
)

class EmployeeDialog(tk.Toplevel):
    def __init__(self, master, managers: dict, mode: str, employee: dict | None = None):
        super().__init__(master)
        self.title("Nhân viên - " + ("Thêm" if mode == "create" else "Sửa"))
        self.resizable(False, False)

        self.managers = managers
        self.mode = mode
        self.employee = employee or {}

        self.emp_mgr = managers["employee"]
        self.dept_mgr = managers["department"]

        self.vars = {
            "full_name": tk.StringVar(value=self.employee.get("full_name", "")),
            "gender": tk.StringVar(value=self.employee.get("gender", "M")),
            "dob": tk.StringVar(
                value=format_display_date(self.employee.get("date_of_birth"))
                if self.employee.get("date_of_birth") else ""
            ),
            "phone": tk.StringVar(value=self.employee.get("phone_number", "")),
            "email": tk.StringVar(value=self.employee.get("email", "")),
            "address": tk.StringVar(value=self.employee.get("address", "")),
            "hire_date": tk.StringVar(
                value=format_display_date(self.employee.get("hire_date"))
                if self.employee.get("hire_date") else ""
            ),
            "position": tk.StringVar(value=self.employee.get("position", "")),
            "salary": tk.StringVar(
                value=str(to_vnd(self.employee.get("base_salary", 0))) if self.employee else ""
            ),
        }

        self.departments = self.dept_mgr.get_all_departments()
        self.dept_map = {d["department_name"]: d["department_id"] for d in self.departments}
        current_dept_name = self.employee.get("department_name")
        self.vars["department"] = tk.StringVar(
            value=current_dept_name
            if current_dept_name
            else (self.departments[0]["department_name"] if self.departments else "")
        )

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        def row(label, widget, r):
            ttk.Label(body, text=label).grid(row=r, column=0, sticky="w", pady=4)
            widget.grid(row=r, column=1, sticky="ew", pady=4)

        # Widgets (giữ reference để disable chuẩn)
        self.full_name_entry = ttk.Entry(body, textvariable=self.vars["full_name"])
        self.gender_cb = ttk.Combobox(body, textvariable=self.vars["gender"], values=["M", "F"], state="readonly")
        self.dob_entry = ttk.Entry(body, textvariable=self.vars["dob"])
        self.phone_entry = ttk.Entry(body, textvariable=self.vars["phone"])
        self.email_entry = ttk.Entry(body, textvariable=self.vars["email"])
        self.address_entry = ttk.Entry(body, textvariable=self.vars["address"])
        self.hire_entry = ttk.Entry(body, textvariable=self.vars["hire_date"])
        self.dept_cb = ttk.Combobox(
            body, textvariable=self.vars["department"], values=list(self.dept_map.keys()), state="readonly"
        )
        self.position_entry = ttk.Entry(body, textvariable=self.vars["position"])
        self.salary_entry = ttk.Entry(body, textvariable=self.vars["salary"])

        row("Họ tên", self.full_name_entry, 0)
        row("Giới tính", self.gender_cb, 1)
        row("Ngày sinh (DD/MM/YYYY)", self.dob_entry, 2)
        row("SĐT", self.phone_entry, 3)
        row("Email", self.email_entry, 4)
        row("Địa chỉ", self.address_entry, 5)
        row("Ngày vào làm (DD/MM/YYYY)", self.hire_entry, 6)
        row("Phòng ban", self.dept_cb, 7)
        row("Chức vụ", self.position_entry, 8)
        row("Lương (VNĐ)", self.salary_entry, 9)

        # NOTE: Backend sp_update_employee không update gender/dob/hire_date/department_id
        if self.mode == "edit":
            self.gender_cb.configure(state="disabled")
            self.dob_entry.configure(state="disabled")
            self.hire_entry.configure(state="disabled")
            self.dept_cb.configure(state="disabled")

        btns = ttk.Frame(body)
        btns.grid(row=10, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Hủy", command=self.destroy).pack(side="right", padx=6)
        ttk.Button(btns, text="Lưu", command=self.on_save).pack(side="right")

        body.columnconfigure(1, weight=1)
        self.grab_set()
        self.transient(master)

    # -------------------- Helper Validation --------------------
    def _collect_common(self):
        full_name = self.vars["full_name"].get().strip()
        if not full_name:
            raise ValueError("Họ tên không được để trống")

        phone = self.vars["phone"].get().strip()
        validate_phone(phone)

        email = self.vars["email"].get().strip()
        ensure_email_domain(email)

        address = self.vars["address"].get().strip()
        position = self.vars["position"].get().strip()
        if not position:
            raise ValueError("Chức vụ không được để trống")

        salary_vnd = parse_currency_input(self.vars["salary"].get())
        validate_salary_vnd(salary_vnd)
        base_salary_db = to_db_money(salary_vnd)

        return full_name, phone, email, address, position, base_salary_db

    # -------------------- Save --------------------
    def on_save(self):
        try:
            full_name, phone, email, address, position, base_salary_db = self._collect_common()

            if self.mode == "create":
                gender = self.vars["gender"].get()
                dob = parse_display_date(self.vars["dob"].get())
                hire_date = parse_display_date(self.vars["hire_date"].get())
                validate_hire_date(hire_date)

                dept_name = self.vars["department"].get()
                dept_id = self.dept_map.get(dept_name)
                if not dept_id:
                    raise ValueError("Phòng ban không hợp lệ")

                res = self.emp_mgr.create_employee(
                    full_name, gender, dob, phone, email, address,
                    hire_date, dept_id, position, base_salary_db
                )
                messagebox.showinfo("Thành công", f"Đã thêm nhân viên ID: {res.get('employee_id')}")
            else:
                emp_id = int(self.employee["employee_id"])
                res = self.emp_mgr.update_employee(
                    emp_id, full_name, phone, email, address, position, base_salary_db
                )
                messagebox.showinfo("Thành công", res.get("message","Cập nhật thành công"))

            self.destroy()

        except (ValidationError, ValueError) as e:
            messagebox.showerror("Lỗi", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không lưu được: {e}")