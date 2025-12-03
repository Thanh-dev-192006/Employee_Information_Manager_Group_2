import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from app.ui.widgets import SortableTreeview
from app.dialogs.bonus_deduction_dialog import BonusDeductionDialog
from app.utils.ui_helpers import to_vnd, format_currency_vnd

class SalaryScreen(ttk.Frame):
    def __init__(self, master, managers: dict):
        super().__init__(master, padding=10)
        self.managers = managers
        self.sal_mgr = managers["salary"]

        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="LƯƠNG", font=("Segoe UI", 14, "bold")).pack(side="left")

        now = datetime.now()
        self.month = tk.IntVar(value=now.month)
        self.year = tk.IntVar(value=now.year)

        ttk.Label(top, text="Tháng:").pack(side="left", padx=(12,4))
        ttk.Combobox(top, textvariable=self.month, values=list(range(1,13)), state="readonly", width=5).pack(side="left")
        ttk.Label(top, text="Năm:").pack(side="left", padx=(12,4))
        ttk.Combobox(top, textvariable=self.year, values=list(range(now.year-2, now.year+3)), state="readonly", width=7).pack(side="left")

        ttk.Button(top, text="Tải", command=self.refresh).pack(side="left", padx=8)
        ttk.Button(top, text="Tính lương tự động", command=self.on_calc).pack(side="right")
        ttk.Button(top, text="Thêm thưởng/phạt", command=self.on_add_bd).pack(side="right", padx=6)

        cols = ("employee_id","employee_name","base_salary_vnd","total_bonus_vnd","total_deduction_vnd","net_salary_vnd")
        self.tree = SortableTreeview(self, columns=cols, show="headings", height=16)
        self.tree.pack(fill="both", expand=True, pady=(10,0))
        heads = {
            "employee_id":"ID","employee_name":"Họ tên",
            "base_salary_vnd":"Lương CB","total_bonus_vnd":"Thưởng",
            "total_deduction_vnd":"Phạt","net_salary_vnd":"Thực lĩnh"
        }
        widths = {"employee_id":60,"employee_name":220,"base_salary_vnd":140,"total_bonus_vnd":120,"total_deduction_vnd":120,"net_salary_vnd":140}
        for c in cols:
            self.tree.heading(c, text=heads[c])
            self.tree.column(c, width=widths[c], anchor="w")
        self.tree.enable_sorting()

        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            rows = self.sal_mgr.get_salary_by_month(int(self.month.get()), int(self.year.get()))
            for r in rows:
                self.tree.insert("", "end", values=(
                    r.get("employee_id"),
                    r.get("employee_name"),
                    format_currency_vnd(to_vnd(r.get("base_salary"))),
                    format_currency_vnd(to_vnd(r.get("total_bonus"))),
                    format_currency_vnd(to_vnd(r.get("total_deductions"))),
                    format_currency_vnd(to_vnd(r.get("net_salary"))),
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_calc(self):
        try:
            res = self.sal_mgr.calculate_monthly_salary(int(self.month.get()), int(self.year.get()))
            messagebox.showinfo("OK", res.get("message","Đã tính lương"))
            self.refresh()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_add_bd(self):
        dlg = BonusDeductionDialog(self, self.managers)
        self.wait_window(dlg)
        self.refresh()