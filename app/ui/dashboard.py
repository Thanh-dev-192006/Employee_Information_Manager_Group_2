import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
from collections import Counter

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyBboxPatch
from matplotlib.figure import Figure
import numpy as np

class Dashboard(ttk.Frame):
    """Dashboard with KPIs on Left Sidebar and Charts in Grid"""

    # Color Palette - Ocean Blue + White Theme
    COLORS = {
        'bg_main': '#f0f4f8',       # Màu nền tổng thể (xám xanh rất nhạt)
        'card_bg': '#ffffff',       # Màu nền card (trắng)
        'primary': '#1565C0',       # Xanh biển đậm (Header/Title)
        'secondary': '#42A5F5',     # Xanh biển sáng (Biểu đồ)
        'accent': '#90CAF9',        # Xanh nhạt (Điểm nhấn)
        'text_dark': '#1e293b',     # Chữ đen
        'text_light': '#64748b',    # Chữ xám
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#ef4444',
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
        """Build main UI structure"""
        # Top bar with refresh button
        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=15, pady=(10, 5))

        ttk.Label(top_bar, text="DASHBOARD OVERVIEW", font=("Segoe UI", 16, "bold"), foreground=self.COLORS['primary']).pack(side="left")

        refresh_btn = ttk.Button(top_bar, text="↻ Refresh Data", command=self.refresh_dashboard)
        refresh_btn.pack(side="right")

        # Container for matplotlib figure
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Initial render
        self.refresh_dashboard()

    def fetch_data_from_db(self) -> dict:
        """Fetch all data needed for dashboard from database"""
        data = {
            'total_employees': 0,
            'total_departments': 0,
            'total_projects': 0,
            'active_assignments': 0,
            'avg_salary': 0,
            'employees_by_dept': {},
            'salary_list': [],
            'top_employees': [],
            'role_distribution': {},
            'active_projects': 0,
        }

        try:
            # Get employees
            employees = self.emp_mgr.get_all_employees(limit=1000, offset=0) if self.emp_mgr else []
            data['total_employees'] = len(employees)

            # Calculate salary stats
            salaries = [float(e.get('base_salary', 0)) for e in employees if e.get('base_salary')]
            data['salary_list'] = salaries
            data['avg_salary'] = sum(salaries) / len(salaries) if salaries else 0

            # Employees by department
            dept_counts = Counter(e.get('department_name', 'Unknown') for e in employees)
            data['employees_by_dept'] = dict(dept_counts)

            # Top employees by salary
            emp_with_salary = [(e.get('full_name', 'N/A'), float(e.get('base_salary', 0))) 
                               for e in employees if e.get('base_salary')]
            emp_with_salary.sort(key=lambda x: x[1], reverse=True)
            data['top_employees'] = emp_with_salary[:8] # Top 8

            # Get departments
            departments = self.dept_mgr.get_all_departments() if self.dept_mgr else []
            data['total_departments'] = len(departments)

            # Get projects
            projects = self.proj_mgr.get_all_projects() if self.proj_mgr else []
            data['total_projects'] = len(projects)

            # Count active projects
            today = date.today()
            active = sum(1 for p in projects 
                        if p.get('end_date') is None or p.get('end_date') >= today)
            data['active_projects'] = active

            # Count active assignments and role distribution
            total_assignments = 0
            role_counts = Counter()
            
            for p in projects:
                try:
                    assignments = self.assign_mgr.get_assignments_by_project(p['project_id']) if self.assign_mgr else []
                    total_assignments += len(assignments)
                    for a in assignments:
                        role = a.get('role', 'Unknown')
                        role_counts[role] += 1
                except:
                    pass

            data['active_assignments'] = total_assignments
            data['role_distribution'] = dict(role_counts)

        except Exception as e:
            print(f"Error fetching dashboard data: {e}")

        return data

    def refresh_dashboard(self):
        """Refresh dashboard with new data"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        if self.fig:
            plt.close(self.fig)

        data = self.fetch_data_from_db()

        # Create new figure with specific background color
        self.fig = Figure(figsize=(14, 9), dpi=100, facecolor=self.COLORS['bg_main'])
        self._draw_dashboard(data)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _draw_dashboard(self, data: dict):
        """Draw layout: Left Sidebar (KPIs) + 4 Main Charts"""
        fig = self.fig

        # --- LAYOUT CONFIGURATION ---
        # Left Sidebar for KPIs: x=0.02 to 0.22
        kpi_x, kpi_w = 0.02, 0.20
        
        # Main Area for Charts: x=0.24 to 0.98
        # Grid 2x2
        c_x, c_y = 0.24, 0.05
        c_w, c_h = 0.74, 0.90
        
        col_gap = 0.02
        row_gap = 0.04
        
        chart_w = (c_w - col_gap) / 2
        chart_h = (c_h - row_gap) / 2

        # --- 1. DRAW KPI SIDEBAR (Left) ---
        self._draw_kpi_sidebar(fig, data, kpi_x, 0.05, kpi_w, 0.90)

        # --- 2. DRAW CHARTS (2x2 Grid) ---
        
        # Top-Left: Employees by Department
        ax1 = fig.add_axes([c_x, c_y + chart_h + row_gap, chart_w, chart_h])
        self._draw_card_background(fig, ax1)
        self._draw_employees_by_dept(ax1, data)

        # Top-Right: Role Distribution
        ax2 = fig.add_axes([c_x + chart_w + col_gap, c_y + chart_h + row_gap, chart_w, chart_h])
        self._draw_card_background(fig, ax2)
        self._draw_role_distribution(ax2, data)

        # Bottom-Left: Salary Histogram
        ax3 = fig.add_axes([c_x, c_y, chart_w, chart_h])
        self._draw_card_background(fig, ax3)
        self._draw_salary_histogram(ax3, data)

        # Bottom-Right: Top Earners
        ax4 = fig.add_axes([c_x + chart_w + col_gap, c_y, chart_w, chart_h])
        self._draw_card_background(fig, ax4)
        self._draw_top_employees(ax4, data)

    def _draw_card_background(self, fig, ax):
        """Draw a rounded white card behind an axis"""
        # Turn off axis background so we can draw a custom patch behind it
        ax.patch.set_alpha(0)
        
        # Get position in figure coordinates
        pos = ax.get_position()
        x0, y0, width, height = pos.x0, pos.y0, pos.width, pos.height
        
        # Draw rounded rectangle on the Figure
        # Note: Using a slightly larger box for padding
        pad = 0.00
        bbox = FancyBboxPatch(
            (x0 - pad, y0 - pad), width + 2*pad, height + 2*pad,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            fc=self.COLORS['card_bg'],
            ec="#d1d5db", # Light border
            alpha=1.0,
            zorder=0,
            transform=fig.transFigure
        )
        fig.patches.append(bbox)

    def _draw_kpi_sidebar(self, fig, data: dict, x, y, w, h):
        """Draw vertical stack of KPI cards"""
        
        # 5 KPIs
        kpis = [
            ("TOTAL EMPLOYEES", str(data['total_employees']), "👥"),
            ("DEPARTMENTS", str(data['total_departments']), "🏢"),
            ("PROJECTS", str(data['total_projects']), "🚀"),
            ("ASSIGNMENTS", str(data['active_assignments']), "📌"),
            ("AVG SALARY", self._format_salary(data['avg_salary']), "💰"),
        ]

        count = len(kpis)
        card_h = (h - (count - 1) * 0.02) / count  # Calculate height per card
        
        for i, (label, value, icon) in enumerate(kpis):
            card_y = y + (count - 1 - i) * (card_h + 0.02) # Stack from top
            
            # Draw Card Background
            bbox = FancyBboxPatch(
                (x, card_y), w, card_h,
                boxstyle="round,pad=0,rounding_size=0.02",
                fc=self.COLORS['card_bg'],
                ec="#d1d5db",
                transform=fig.transFigure,
                zorder=1
            )
            fig.patches.append(bbox)
            
            # Add blue accent bar on left
            accent = FancyBboxPatch(
                (x, card_y + 0.01), 0.005, card_h - 0.02,
                boxstyle="round,pad=0,rounding_size=0.002",
                fc=self.COLORS['primary'],
                transform=fig.transFigure,
                zorder=2
            )
            fig.patches.append(accent)

            # Text
            cx = x + w/2
            cy = card_y + card_h/2
            
            # Icon (Top)
            fig.text(cx, cy + 0.05, icon, ha='center', va='center', fontsize=20, color=self.COLORS['secondary'])
            
            # Value (Middle)
            fig.text(cx, cy, value, ha='center', va='center', fontsize=16, fontweight='bold', color=self.COLORS['text_dark'])
            
            # Label (Bottom)
            fig.text(cx, cy - 0.05, label, ha='center', va='center', fontsize=9, color=self.COLORS['text_light'])

    def _format_ax(self, ax, title):
        """Standard styling for charts"""
        ax.set_title(title, fontsize=11, fontweight='bold', color=self.COLORS['primary'], pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cbd5e1')
        ax.spines['bottom'].set_color('#cbd5e1')
        ax.tick_params(colors=self.COLORS['text_light'], labelsize=8)
        ax.grid(axis='x', linestyle='--', alpha=0.3)

    # --- CHART 1: EMPLOYEES BY DEPARTMENT ---
    def _draw_employees_by_dept(self, ax, data):
        dept_data = data.get('employees_by_dept', {})
        if not dept_data:
            self._draw_no_data(ax, "Employees by Department")
            return

        sorted_items = sorted(dept_data.items(), key=lambda x: x[1], reverse=True)[:6]
        depts = [item[0][:15] for item in sorted_items]
        counts = [item[1] for item in sorted_items]
        y_pos = np.arange(len(depts))

        bars = ax.barh(y_pos, counts, color=self.COLORS['secondary'], height=0.6)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(depts)
        ax.invert_yaxis()
        
        # Add Data Labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center', fontsize=9, fontweight='bold', color=self.COLORS['text_dark'])

        self._format_ax(ax, "Employees by Department")

    # --- CHART 2: SALARY HISTOGRAM ---
    def _draw_salary_histogram(self, ax, data):
        salaries = data.get('salary_list', [])
        if not salaries:
            self._draw_no_data(ax, "Salary Distribution")
            return

        MONEY_SCALE = 10_000
        salaries_vnd = [s * MONEY_SCALE / 1_000_000 for s in salaries] # Million VND

        n, bins, patches = ax.hist(salaries_vnd, bins=10, color=self.COLORS['accent'], edgecolor='white', alpha=0.9)
        
        # Add Data Labels
        for i in range(len(patches)):
            if n[i] > 0:
                ax.text(patches[i].get_x() + patches[i].get_width()/2, n[i], 
                        str(int(n[i])), ha='center', va='bottom', fontsize=8)

        avg = data['avg_salary'] * MONEY_SCALE / 1_000_000
        ax.axvline(avg, color=self.COLORS['danger'], linestyle='--', linewidth=1.5, label=f'Avg: {avg:.1f}M')
        ax.legend(fontsize=8, frameon=False)
        ax.set_xlabel('Million VND', fontsize=8, color=self.COLORS['text_light'])
        
        self._format_ax(ax, "Salary Distribution")

    # --- CHART 3: TOP EMPLOYEES ---
    def _draw_top_employees(self, ax, data):
        top_emps = data.get('top_employees', [])
        if not top_emps:
            self._draw_no_data(ax, "Top Earners")
            return

        MONEY_SCALE = 10_000
        names = [emp[0][:15] for emp in top_emps]
        salaries = [emp[1] * MONEY_SCALE / 1_000_000 for emp in top_emps] # Million VND
        y_pos = np.arange(len(names))

        # Gradient colors
        colors = plt.cm.Blues(np.linspace(0.8, 0.4, len(names)))
        
        bars = ax.barh(y_pos, salaries, color=colors, height=0.6)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names)
        ax.invert_yaxis()

        # Add Data Labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.2, bar.get_y() + bar.get_height()/2, 
                    f'{width:.1f}M', ha='left', va='center', fontsize=8)

        self._format_ax(ax, "Top Highest Salaries")

    # --- CHART 4: ROLE DISTRIBUTION ---
    def _draw_role_distribution(self, ax, data):
        role_data = data.get('role_distribution', {})
        if not role_data:
            self._draw_no_data(ax, "Role Distribution")
            return

        sorted_roles = sorted(role_data.items(), key=lambda x: x[1], reverse=True)[:6]
        roles = [r[0] for r in sorted_roles]
        counts = [r[1] for r in sorted_roles]

        colors = plt.cm.Paired(np.arange(len(roles)))

        wedges, texts, autotexts = ax.pie(
            counts, labels=roles, autopct='%1.1f%%',
            colors=colors, startangle=90, pctdistance=0.85,
            wedgeprops=dict(width=0.4, edgecolor='white'),
            textprops={'fontsize': 8}
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        # Center Text
        total = sum(counts)
        ax.text(0, 0, f'{total}\nRoles', ha='center', va='center', fontsize=10, fontweight='bold', color=self.COLORS['text_dark'])
        
        ax.set_title("Project Roles", fontsize=11, fontweight='bold', color=self.COLORS['primary'], pad=15)

    def _draw_no_data(self, ax, title):
        ax.text(0.5, 0.5, "No Data Available", ha='center', va='center', color=self.COLORS['text_light'])
        ax.set_title(title, fontsize=11, fontweight='bold', color=self.COLORS['primary'])
        ax.axis('off')

    def _format_salary(self, amount: float) -> str:
        if amount == 0: return "0"
        MONEY_SCALE = 10_000
        vnd = amount * MONEY_SCALE
        if vnd >= 1_000_000:
            return f"{vnd/1_000_000:.1f}M"
        return f"{vnd:,.0f}"