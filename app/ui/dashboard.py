import tkinter as tk
from tkinter import ttk
import os

# Import Matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyBboxPatch
from matplotlib.figure import Figure
import numpy as np
from collections import Counter

class Dashboard(ttk.Frame):
    """Dashboard with KPIs and Charts (Simplified Rendering)"""

    # Bộ màu sắc
    COLORS = {
        'bg_main': '#F3F4F6',       # Nền tổng thể
        'card_bg': '#FFFFFF',       # Nền trắng cho biểu đồ
        'primary': '#2563EB',       # Xanh đậm
        'secondary': '#3B82F6',     # Xanh nhạt
        'accent': '#8B5CF6',        # Tím
        'text_dark': '#111827',     # Chữ đen
        'text_light': '#6B7280',    # Chữ xám
        'danger': '#EF4444',        # Đỏ
        'chart_colors': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
    }

    def __init__(self, parent, managers: dict):
        super().__init__(parent)
        self.managers = managers
        self.emp_mgr = managers.get("employee")
        self.dept_mgr = managers.get("department")
        self.proj_mgr = managers.get("project")
        self.assign_mgr = managers.get("assignment")

        self.canvas = None
        self.fig = None

        self._build_ui()

    def _build_ui(self):
        # Header
        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=20, pady=10)
        ttk.Label(top_bar, text="DASHBOARD OVERVIEW", font=("Segoe UI", 16, "bold"), 
                  bootstyle="primary").pack(side="left")
        ttk.Button(top_bar, text="↻ Refresh Data", command=self.refresh_dashboard, 
                   bootstyle="outline-primary").pack(side="right")

        # Chart Container
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Load data first time
        self.refresh_dashboard()

    def fetch_data(self) -> dict:
        """Lấy dữ liệu từ DB (An toàn)"""
        data = {
            'total_employees': 0, 'total_departments': 0, 'total_projects': 0,
            'active_assignments': 0, 'avg_salary': 0, 
            'employees_by_dept': {}, 'salary_list': [], 'top_employees': [], 'role_distribution': {}
        }
        try:
            # 1. Employees & Salary
            emps = self.emp_mgr.get_all_employees(limit=2000, offset=0) if self.emp_mgr else []
            data['total_employees'] = len(emps)
            
            salaries = [float(e.get('base_salary', 0)) for e in emps if e.get('base_salary')]
            if salaries:
                data['salary_list'] = salaries
                data['avg_salary'] = sum(salaries) / len(salaries)
                
            # Top Employees
            emp_sal = [(e.get('full_name','N/A'), float(e.get('base_salary',0))) for e in emps]
            emp_sal.sort(key=lambda x: x[1], reverse=True)
            data['top_employees'] = emp_sal[:8]

            # Depts
            dept_counts = Counter(e.get('department_name', 'Unknown') for e in emps)
            data['employees_by_dept'] = dict(dept_counts)
            
            depts = self.dept_mgr.get_all_departments() if self.dept_mgr else []
            data['total_departments'] = len(depts)

            # Projects & Roles
            projs = self.proj_mgr.get_all_projects() if self.proj_mgr else []
            data['total_projects'] = len(projs)
            
            total_assign = 0
            roles = Counter()
            for p in projs:
                try:
                    assigns = self.assign_mgr.get_assignments_by_project(p['project_id'])
                    total_assign += len(assigns)
                    for a in assigns: roles[a.get('role','Unknown')] += 1
                except: pass
            data['active_assignments'] = total_assign
            data['role_distribution'] = dict(roles)

        except Exception as e:
            print(f"Data Fetch Error: {e}")
        return data

    def refresh_dashboard(self):
        # 1. Lấy dữ liệu mới nhất
        data = self.fetch_data()

        # 2. Kiểm tra nếu biểu đồ chưa từng được tạo (Lần đầu tiên chạy)
        if self.fig is None:
            self.fig = Figure(figsize=(11, 6), dpi=100, facecolor=self.COLORS['bg_main'])
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            self.fig.clear()

        # 3. Vẽ lại nội dung lên khung có sẵn
        self._draw_kpi_sidebar(self.fig, data)
        self._draw_charts(self.fig, data)

        # 4. Cập nhật hiển thị
        self.canvas.draw()

    def _draw_kpi_sidebar(self, fig, data):
        """Vẽ thanh KPI bên trái"""
        # Cấu hình Font Icon
        font_path = os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts', 'seguiemj.ttf')
        prop = fm.FontProperties(fname=font_path, size=24) if os.path.exists(font_path) else fm.FontProperties(size=20)

        metrics = [
            ("TOTAL EMPLOYEES", str(data['total_employees']), "👥"),
            ("DEPARTMENTS", str(data['total_departments']), "🏢"),
            ("PROJECTS", str(data['total_projects']), "🚀"),
            ("ASSIGNMENTS", str(data['active_assignments']), "📌"),
            ("AVG SALARY", self._fmt_money(data['avg_salary']), "💰")
        ]

        # Vị trí Sidebar
        x, y_start, w, h = 0.02, 0.90, 0.20, 0.16
        gap = 0.02

        for i, (title, val, icon) in enumerate(metrics):
            y = y_start - i * (h + gap)
            
            # Vẽ nền thẻ (Dùng Patch)
            bbox = FancyBboxPatch((x, y - h + 0.02), w, h, boxstyle="round,pad=0.01", 
                                  fc='white', ec='#d1d5db', transform=fig.transFigure, zorder=1)
            fig.patches.append(bbox)
            
            # Vẽ thanh màu bên trái
            bar = FancyBboxPatch((x, y - h + 0.03), 0.005, h - 0.02, 
                                 boxstyle="round,pad=0", fc=self.COLORS['primary'], transform=fig.transFigure, zorder=2)
            fig.patches.append(bar)

            # Vẽ chữ & Icon
            cx = x + w/2
            cy = y - h/2 + 0.01
            
            fig.text(cx, cy + 0.04, icon, ha='center', va='center', color=self.COLORS['secondary'], fontproperties=prop)
            fig.text(cx, cy - 0.01, val, ha='center', va='center', fontsize=16, fontweight='bold', color='#111827')
            fig.text(cx, cy - 0.05, title, ha='center', va='center', fontsize=9, color='#6B7280')

    def _draw_charts(self, fig, data):
        """Vẽ 4 biểu đồ lưới 2x2"""
        # Layout: [x, y, width, height]
        grid = [
            ([0.38, 0.53, 0.24, 0.35], "Employees by Department"), 
            ([0.70, 0.53, 0.25, 0.35], "Project Roles"),           
            ([0.38, 0.08, 0.24, 0.35], "Salary Distribution"), 
            ([0.73, 0.08, 0.22, 0.35], "Top Earners")            
        ]

        # 1. Employees by Dept
        ax1 = fig.add_axes(grid[0][0])
        self._style_ax(ax1, grid[0][1])
        d = data['employees_by_dept']
        if d:
            items = sorted(d.items(), key=lambda x: x[1], reverse=True)[:6]
            names, vals = [x[0] for x in items], [x[1] for x in items]
            y = np.arange(len(names))
            ax1.barh(y, vals, color=self.COLORS['secondary'], height=0.6)
            ax1.set_yticks(y); ax1.set_yticklabels(names); ax1.invert_yaxis()
            for i, v in enumerate(vals): ax1.text(v + 0.1, i, str(v), va='center', fontsize=9)
        else: self._no_data(ax1)

        # 2. Roles (Pie)
        ax2 = fig.add_axes(grid[1][0])
        self._style_ax(ax2, grid[1][1], grid=False) # Tắt lưới cho Pie chart
        ax2.axis('off') # Tắt trục
        d = data['role_distribution']
        if d:
            items = sorted(d.items(), key=lambda x: x[1], reverse=True)[:5]
            names, vals = [x[0] for x in items], [x[1] for x in items]
            ax2.pie(vals, labels=names, autopct='%1.0f%%', colors=self.COLORS['chart_colors'], 
                    startangle=90, pctdistance=0.8, wedgeprops=dict(width=0.4, edgecolor='white'))
            ax2.text(0, 0, f"{sum(vals)}\nRoles", ha='center', va='center', fontweight='bold')
        else: self._no_data(ax2)

        # 3. Salary Hist
        ax3 = fig.add_axes(grid[2][0])
        self._style_ax(ax3, grid[2][1])
        sal = [s * 10000 / 1000000 for s in data['salary_list']] # Triệu VND
        if sal:
            ax3.hist(sal, bins=8, color=self.COLORS['accent'], edgecolor='white', alpha=0.8)
            ax3.set_xlabel("Million VND", fontsize=8, color='#6B7280')
        else: self._no_data(ax3)

        # 4. Top Earners
        ax4 = fig.add_axes(grid[3][0])
        self._style_ax(ax4, grid[3][1])
        d = data['top_employees']
        if d:
            names = [x[0] for x in d]
            vals = [x[1] * 10000 / 1000000 for x in d]
            y = np.arange(len(names))
            ax4.barh(y, vals, color=self.COLORS['chart_colors'][0], height=0.6)
            ax4.set_yticks(y); ax4.set_yticklabels(names); ax4.invert_yaxis()
            for i, v in enumerate(vals): ax4.text(v + 0.1, i, f"{v:.1f}M", va='center', fontsize=8)
        else: self._no_data(ax4)

    def _style_ax(self, ax, title, grid=True):
        """Style chuẩn cho biểu đồ - Nền trắng trực tiếp"""
        ax.set_facecolor('white')  # [QUAN TRỌNG] Đặt nền trắng trực tiếp cho trục
        ax.set_title(title, fontsize=11, fontweight='bold', color='#111827', pad=10)
        
        # Xóa viền
        for s in ax.spines.values(): s.set_visible(False)
        
        # Grid mờ
        if grid:
            ax.grid(axis='x', visible=False)
            ax.grid(axis='y', linestyle=':', alpha=0.5)
            ax.tick_params(axis='both', colors='#6B7280', labelsize=8, length=0)

    def _no_data(self, ax):
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', color='#9CA3AF')
        ax.set_xticks([]); ax.set_yticks([])

    def _fmt_money(self, val):
        if not val: return "0"
        vnd = val * 10000
        return f"{vnd/1000000:.1f}M" if vnd >= 1000000 else f"{vnd:,.0f}"