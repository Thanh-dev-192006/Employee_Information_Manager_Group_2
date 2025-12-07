import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import unicodedata  # Thư viện xử lý tiếng Việt

from app.models.utils.helpers import parse_display_date, parse_currency_input, to_db_money, format_display_date

def remove_accents(input_str):
    """
    Chuyển đổi chuỗi có dấu thành không dấu
    """
    if not input_str:
        return ""
    s = str(input_str)
    # Xử lý chữ Đ/đ
    s = s.replace("đ", "d").replace("Đ", "D")
    # Chuẩn hóa unicode
    s = unicodedata.normalize('NFKD', s)
    # Lọc bỏ dấu
    return "".join(c for c in s if not unicodedata.combining(c))

class BonusDeductionDialog(tk.Toplevel):
    def __init__(self, master, managers: dict):
        super().__init__(master)
        self.title("Bonus / Deduction")
        self.resizable(False, False)

        self.emp_mgr = managers["employee"]
        self.bd_mgr = managers["bonus_deduction"]

        self.emps = self.emp_mgr.get_all_employees(limit=10000, offset=0)
        self.emp_map = {f'{e["employee_id"]} - {e["full_name"]}': e["employee_id"] for e in self.emps}
        self.search_list = list(self.emp_map.keys())

        self.emp_var = tk.StringVar(value="")
        
        self.typ = tk.StringVar(value="")
        self.amount = tk.StringVar(value="")
        self.reason = tk.StringVar(value="")
        self.eff = tk.StringVar(value=format_display_date(date.today()))

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="Employee (Type & Enter to search)").grid(row=0, column=0, sticky="w", pady=4)
        
        self.cb_emp = ttk.Combobox(
            body, 
            textvariable=self.emp_var, 
            values=self.search_list, 
            state="normal",
            width=36,
            height=15
        )
        self.cb_emp.grid(row=0, column=1, sticky="ew", pady=4)
        
        self.cb_emp.bind('<KeyRelease>', self.on_key_release)
        
        self.cb_emp.bind('<Return>', self.on_enter)
        # -------------------------------------

        ttk.Label(body, text="Type").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Combobox(body, textvariable=self.typ, values=["Bonus","Deduction"], state="readonly")\
            .grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Amount (VND)").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.amount).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Reason").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.reason).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Effective Date (DD/MM/YYYY)").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.eff).grid(row=4, column=1, sticky="ew", pady=4)

        btns = ttk.Frame(body)
        btns.grid(row=5, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right", padx=6)
        ttk.Button(btns, text="Save", command=self.on_save).pack(side="right")

        body.columnconfigure(1, weight=1)
        self.grab_set()
        self.transient(master)

    def on_key_release(self, event):
        """Lọc danh sách khi gõ (hỗ trợ không dấu)"""
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Return', 'Tab', 'Escape']:
            return

        typed = self.cb_emp.get()
        
        if typed == '':
            data = self.search_list
        else:
            kw = remove_accents(typed).lower()
            
            data = []
            for item in self.search_list:
                item_norm = remove_accents(item).lower()
                
                if kw in item_norm:
                    data.append(item)

        self.cb_emp['values'] = data

    def on_enter(self, event):
        """Khi ấn Enter: Mở danh sách ra để chọn"""
        try:
            self.cb_emp.tk.call('ttk::combobox::Post', self.cb_emp._w)
        except:
            pass

    def on_save(self):
        try:
            emp_name = self.emp_var.get()
            emp_id = self.emp_map.get(emp_name)
            
            if not emp_id:
                raise ValueError("Invalid employee. Please select from the list.")

            vnd = parse_currency_input(self.amount.get())
            if vnd <= 0:
                raise ValueError("Amount must be > 0")
            amt_db = to_db_money(vnd)

            desc = self.reason.get().strip() or "N/A"
            eff_date = parse_display_date(self.eff.get())

            res = self.bd_mgr.create_bonus_deduction(emp_id, self.typ.get(), amt_db, desc, eff_date)
            messagebox.showinfo("Success", res.get("message","OK"))
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))