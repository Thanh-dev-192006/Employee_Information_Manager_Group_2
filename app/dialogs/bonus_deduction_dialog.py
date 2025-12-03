import tkinter as tk
from tkinter import ttk, messagebox
from app.models.utils.helpers import parse_display_date, parse_currency_input, to_db_money

class BonusDeductionDialog(tk.Toplevel):
    def __init__(self, master, managers: dict):
        super().__init__(master)
        self.title("Thưởng / Phạt")
        self.resizable(False, False)

        self.emp_mgr = managers["employee"]
        self.bd_mgr = managers["bonus_deduction"]

        self.emps = self.emp_mgr.get_all_employees(limit=1000, offset=0)
        self.emp_map = {f'{e["employee_id"]} - {e["full_name"]}': e["employee_id"] for e in self.emps}

        self.emp = tk.StringVar(value=(next(iter(self.emp_map.keys())) if self.emp_map else ""))
        self.typ = tk.StringVar(value="Bonus")
        self.amount = tk.StringVar(value="1000000")
        self.reason = tk.StringVar(value="")
        self.eff = tk.StringVar(value="")

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="Nhân viên").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Combobox(body, textvariable=self.emp, values=list(self.emp_map.keys()), state="readonly", width=36)\
            .grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Loại").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Combobox(body, textvariable=self.typ, values=["Bonus","Deduction"], state="readonly").grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Số tiền (VNĐ)").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.amount).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Lý do").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.reason).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Ngày hiệu lực (DD/MM/YYYY)").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.eff).grid(row=4, column=1, sticky="ew", pady=4)

        btns = ttk.Frame(body)
        btns.grid(row=5, column=0, columnspan=2, sticky="e", pady=(10,0))
        ttk.Button(btns, text="Hủy", command=self.destroy).pack(side="right", padx=6)
        ttk.Button(btns, text="Lưu", command=self.on_save).pack(side="right")

        self.grab_set()
        self.transient(master)

    def on_save(self):
        try:
            emp_id = self.emp_map.get(self.emp.get())
            if not emp_id:
                raise ValueError("Nhân viên không hợp lệ")

            vnd = parse_currency_input(self.amount.get())
            # không bắt >=5tr cho thưởng/phạt, nên chỉ check >0 theo business
            if vnd <= 0:
                raise ValueError("Số tiền phải > 0")
            amt_db = to_db_money(vnd)

            desc = self.reason.get().strip() or "N/A"
            eff_date = parse_display_date(self.eff.get())

            res = self.bd_mgr.create_bonus_deduction(emp_id, self.typ.get(), amt_db, desc, eff_date)
            messagebox.showinfo("OK", res.get("message","OK"))
            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))