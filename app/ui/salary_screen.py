import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import math
import unicodedata

from app.ui.widgets import SortableTreeview, PaginationBar
from app.dialogs.bonus_deduction_dialog import BonusDeductionDialog
from app.models.utils.helpers import to_vnd, format_currency_vnd
from app.models.utils.helpers import month_number_to_name

def remove_accents(input_str):
    """Chuyển đổi chuỗi có dấu thành không dấu (Hải Đăng -> Hai Dang)"""
    if not input_str:
        return ""
    s = str(input_str)
    s = s.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize('NFKD', s)
    return "".join(c for c in s if not unicodedata.combining(c))

class SalaryScreen(ttk.Frame):
    PAGE_SIZE = 15
    def __init__(self, master, managers: dict):
        super().__init__(master, padding=10)
        style = ttk.Style()
        style.configure("BigRow.Treeview", font=("Segoe UI", 12), rowheight=50)
        style.configure("BigRow.Treeview.Heading", font=("Segoe UI", 13, "bold"))

        self.managers = managers
        self.sal_mgr = managers["salary"]
        self.emp_mgr = managers["employee"]

        self.page = 0
        self.search_keyword = ""
        self.search_exact_id = None

        self.sort_col = "employee_id"
        self.sort_desc = False

        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="SALARY", font=("Segoe UI", 14, "bold")).pack(side="left")

        now = datetime.now()
        self.month = tk.IntVar(value=now.month)
        self.year = tk.IntVar(value=now.year)

        ttk.Label(top, text="Month:").pack(side="left", padx=(12,4))
        cb_month = ttk.Combobox(top, textvariable=self.month, values=list(range(1,13)), state="readonly", width=5)
        cb_month.pack(side="left")
        cb_month.bind("<<ComboboxSelected>>", lambda e: self.reset_paging())

        ttk.Label(top, text="Year:").pack(side="left", padx=(12,4))
        cb_year = ttk.Combobox(top, textvariable=self.year, values=list(range(now.year-2, now.year+3)), state="readonly", width=7)
        cb_year.pack(side="left")
        cb_year.bind("<<ComboboxSelected>>", lambda e: self.reset_paging())

        ttk.Button(top, text="Load", command=self.refresh).pack(side="left", padx=8)

        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", pady=(8, 0))

        self.emps = self.emp_mgr.get_all_employees(limit=1000, offset=0)
        self.emp_map = {f'{e["employee_id"]} - {e["full_name"]}': e["employee_id"] for e in self.emps}

        ttk.Label(action_bar, text="Employee (Enter to search):").pack(side="left")
        self.employee_id = tk.StringVar(value="")
        
        self.cb_emp = ttk.Combobox(
            action_bar,
            textvariable=self.employee_id,
            values=list(self.emp_map.keys()),
            state="normal", 
            width=30
        )
        self.cb_emp.pack(side="left", padx=(4, 5))
        self.cb_emp.bind('<Return>', self.on_find_employee)
        
        ttk.Button(
            action_bar, 
            text="Refresh", 
            command=self.on_reset_search
        ).pack(side="left", padx=(0, 12))
        # -------------------------------------

        ttk.Button(top, text="Add Bonus/Deduction", command=self.on_add_bd).pack(side="right", padx=6)

        cols = ("employee_id","employee_name","base_salary_vnd","total_bonus_vnd","total_deduction_vnd","net_amount_vnd")
        self.tree = SortableTreeview(self, columns=cols, show="headings", height=15, style="BigRow.Treeview")
        self.tree.pack(fill="both", expand=True, pady=(10,0))
        heads = {
            "employee_id":"ID","employee_name":"Full Name",
            "base_salary_vnd":"Base Salary","total_bonus_vnd":"Bonus",
            "total_deduction_vnd":"Deduction","net_amount_vnd":"Net Amount"
        }
        widths = {
            "employee_id": 60,
            "employee_name": 220,
            "base_salary_vnd": 180,      
            "total_bonus_vnd": 160,      
            "total_deduction_vnd": 160,  
            "net_amount_vnd": 180       
        }
        
        for c in cols:
            self.tree.heading(c, text=heads[c], command=lambda _col=c: self.on_sort(_col))
            if "id" in c:          
                anchor = "center"
            else:                        
                anchor = "w"
            self.tree.column(c, width=widths[c], anchor=anchor)

        self.pager = PaginationBar(self, self.prev_page, self.next_page)
        self.pager.pack(fill="x", pady=(6,0))

        self.refresh()

    def reset_paging(self):
        self.page = 0
        self.refresh()

    def on_sort(self, col):
        if self.sort_col == col:
            self.sort_desc = not self.sort_desc 
        else:
            self.sort_col = col
            self.sort_desc = False 
        
        self.page = 0 
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        month_name = month_number_to_name(int(self.month.get()))  
        sort_order = "DESC" if self.sort_desc else "ASC"

        try:
            if not self.search_keyword and self.search_exact_id is None:
                rows = self.sal_mgr.get_salary_by_month(
                    month_name,
                    int(self.year.get()),
                    limit=self.PAGE_SIZE,
                    offset=self.page * self.PAGE_SIZE,
                    sort_by=self.sort_col,    
                    sort_order=sort_order
                )
                total_records = self.sal_mgr.count_salary_records()
            
            else:
                all_rows = self.sal_mgr.get_salary_by_month(
                    month_name,
                    int(self.year.get()),
                    limit=100000, 
                    offset=0,
                    sort_by=self.sort_col,
                    sort_order=sort_order
                )
                
                filtered_rows = []
                kw_normalized = remove_accents(self.search_keyword).lower()

                for r in all_rows:
                    if self.search_exact_id is not None:
                        if r.get("employee_id") == self.search_exact_id:
                            filtered_rows.append(r)
                    
                    elif self.search_keyword:
                        emp_id_str = str(r.get("employee_id", ""))
                        raw_name = r.get("employee_name", "")
                        name_normalized = remove_accents(raw_name).lower()
                        
                        if (kw_normalized in emp_id_str) or (kw_normalized in name_normalized):
                            filtered_rows.append(r)
                
                total_records = len(filtered_rows)
                start_idx = self.page * self.PAGE_SIZE
                end_idx = start_idx + self.PAGE_SIZE
                rows = filtered_rows[start_idx:end_idx]

            self.pager.set_page(self.page)
            
            max_page = math.ceil(total_records / self.PAGE_SIZE) - 1
            if max_page < 0: max_page = 0
            
            if self.page > max_page and total_records > 0:
                self.page = max_page
                self.refresh()
                return

            can_prev = (self.page > 0)
            can_next = (self.page < max_page)
            self.pager.update_state(can_prev, can_next)
            
            for r in rows:
                self.tree.insert("", "end", values=(
                    r.get("employee_id"),
                    r.get("employee_name"),
                    format_currency_vnd(to_vnd(r.get("base_salary"))),
                    format_currency_vnd(to_vnd(r.get("total_bonus"))),
                    format_currency_vnd(to_vnd(r.get("total_deduction"))),
                    format_currency_vnd(to_vnd(r.get("net_amount"))),
                ))
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.refresh()

    def next_page(self):
        self.page += 1
        self.refresh()

    def on_find_employee(self, event=None):
        raw_text = self.employee_id.get().strip()
        
        self.search_keyword = ""
        self.search_exact_id = None
        
        if not raw_text:
            self.page = 0
            self.refresh()
            return

        if " - " in raw_text:
            try:
                part0 = raw_text.split(" - ")[0]
                if part0.isdigit():
                    self.search_exact_id = int(part0)
            except:
                pass
        
        if self.search_exact_id is None:
            self.search_keyword = raw_text
            
        self.page = 0
        self.refresh()

    def on_reset_search(self):
        """Xóa tìm kiếm và quay về danh sách đầy đủ"""
        self.employee_id.set("")  
        self.search_keyword = ""  
        self.search_exact_id = None
        self.page = 0
        self.refresh()  

    def _get_selected_emp_id(self):
        txt = self.employee_id.get()
        if not txt: return None
        return self.emp_map.get(txt)

    def on_add_bd(self):
        dlg = BonusDeductionDialog(self, self.managers)
        self.wait_window(dlg)
        self.refresh()