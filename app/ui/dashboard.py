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
    """Dashboard with KPIs and Charts"""

    # Color Palette - Ocean Blue + White
    COLORS = {
        'dark_blue': '#1a3a8a',
        'primary_blue': '#2952a3',
        'light_blue': '#4169c4',
        'accent_blue': '#3b82f6',
        'sky_blue': '#60a5fa',
        'white': '#ffffff',
        'off_white': '#f8fafc',
        'light_gray': '#e2e8f0',
        'text_dark': '#1e293b',
        'text_gray': '#64748b',
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
        top_bar.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(top_bar, text="📊 DASHBOARD", font=("Segoe UI", 16, "bold")).pack(side="left")

        refresh_btn = ttk.Button(top_bar, text="🔄 Refresh", command=self.refresh_dashboard)
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
            data['top_employees'] = emp_with_salary[:10]

            # Get departments
            departments = self.dept_mgr.get_all_departments() if self.dept_mgr else []
            data['total_departments'] = len(departments)

            # Get projects
            projects = self.proj_mgr.get_all_projects() if self.proj_mgr else []
            data['total_projects'] = len(projects)

            # Count active projects (no end_date or end_date >= today)
            today = date.today()
            active = sum(1 for p in projects 
                        if p.get('end_date') is None or p.get('end_date') >= today)
            data['active_projects'] = active

            # Count active assignments and role distribution
            # We need to get assignments - iterate through projects
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
        # Clear old canvas
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        if self.fig:
            plt.close(self.fig)

        # Fetch fresh data
        data = self.fetch_data_from_db()

        # Create new figure
        self.fig = Figure(figsize=(14, 10), dpi=100, facecolor=self.COLORS['off_white'])
        self._draw_dashboard(data)

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _draw_dashboard(self, data: dict):
        """Draw all dashboard components"""
        fig = self.fig

        # 1. Header
        self._draw_header(fig)

        # 2. KPI Cards (5 cards now)
        self._draw_kpi_cards(fig, data)

        # 3. Charts Grid (2x2)
        # Chart 1: Employees by Department (top-left)
        ax1 = fig.add_axes([0.03, 0.38, 0.45, 0.28])
        self._draw_employees_by_dept(ax1, data)

        # Chart 2: Salary Histogram (top-right)
        ax2 = fig.add_axes([0.52, 0.38, 0.45, 0.28])
        self._draw_salary_histogram(ax2, data)

        # Chart 3: Top-N Employees by Salary (bottom-left)
        ax3 = fig.add_axes([0.03, 0.04, 0.45, 0.30])
        self._draw_top_employees(ax3, data)

        # Chart 4: Role Distribution (bottom-right)
        ax4 = fig.add_axes([0.52, 0.04, 0.45, 0.30])
        self._draw_role_distribution(ax4, data)

    def _draw_header(self, fig):
        """Draw gradient header"""
        header = fig.add_axes([0, 0.92, 1, 0.08])
        header.set_xlim(0, 1)
        header.set_ylim(0, 1)

        # Gradient background
        gradient = np.linspace(0, 1, 100).reshape(1, -1)
        header.imshow(gradient, aspect='auto', cmap='Blues', extent=[0, 1, 0, 1], alpha=0.9)

        # Title
        header.text(0.02, 0.5, "Employee Information Dashboard",
                   fontsize=18, fontweight='bold', color='white',
                   va='center', ha='left')

        # Timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        header.text(0.98, 0.5, f"Last updated: {timestamp}",
                   fontsize=10, color='white', va='center', ha='right')

        header.axis('off')

    def _draw_kpi_cards(self, fig, data: dict):
        """Draw 5 KPI cards"""
        card_area = fig.add_axes([0.02, 0.68, 0.96, 0.22])
        card_area.set_xlim(0, 1)
        card_area.set_ylim(0, 1)
        card_area.set_facecolor(self.COLORS['off_white'])
        card_area.axis('off')

        # 5 KPI definitions - matching project requirements
        kpis = [
            ("👥", "Total Employees", str(data['total_employees']), self.COLORS['primary_blue']),
            ("🏢", "Departments", str(data['total_departments']), self.COLORS['light_blue']),
            ("📁", "Projects", str(data['total_projects']), self.COLORS['accent_blue']),
            ("📋", "Active Assignments", str(data['active_assignments']), self.COLORS['success']),
            ("💰", "Average Salary", self._format_salary(data['avg_salary']), self.COLORS['warning']),
        ]

        card_width = 0.18
        gap = 0.02
        start_x = 0.01

        for i, (icon, label, value, color) in enumerate(kpis):
            x = start_x + i * (card_width + gap)
            self._draw_single_kpi_card(card_area, x, 0.1, card_width, 0.8, icon, label, value, color)

    def _draw_single_kpi_card(self, ax, x, y, w, h, icon, label, value, accent_color):
        """Draw a single rounded KPI card"""
        # Card background
        card = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor='white',
            edgecolor=self.COLORS['light_gray'],
            linewidth=1.5
        )
        ax.add_patch(card)

        # Accent bar on left
        accent = FancyBboxPatch(
            (x, y), 0.008, h,
            boxstyle="round,pad=0,rounding_size=0.02",
            facecolor=accent_color,
            edgecolor='none'
        )
        ax.add_patch(accent)

        # Icon
        ax.text(x + w/2, y + h*0.75, icon, fontsize=24, ha='center', va='center')

        # Value
        ax.text(x + w/2, y + h*0.45, value, fontsize=16, fontweight='bold',
               ha='center', va='center', color=self.COLORS['text_dark'])

        # Label
        ax.text(x + w/2, y + h*0.18, label, fontsize=9,
               ha='center', va='center', color=self.COLORS['text_gray'])

    def _draw_employees_by_dept(self, ax, data: dict):
        """Draw horizontal bar chart - Employees by Department"""
        dept_data = data.get('employees_by_dept', {})

        if not dept_data:
            self._draw_no_data(ax, "Employees by Department")
            return

        # Sort by count
        sorted_items = sorted(dept_data.items(), key=lambda x: x[1], reverse=True)[:8]
        depts = [item[0][:15] for item in sorted_items]  # Truncate long names
        counts = [item[1] for item in sorted_items]

        y_pos = np.arange(len(depts))
        colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(depts)))

        ax.barh(y_pos, counts, color=colors, edgecolor='white', height=0.6)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(depts, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel('Number of Employees', fontsize=9)
        ax.set_title('Employees by Department', fontsize=11, fontweight='bold', pad=10)

        # Add value labels
        for i, v in enumerate(counts):
            ax.text(v + 0.5, i, str(v), va='center', fontsize=9, fontweight='bold')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def _draw_salary_histogram(self, ax, data: dict):
        """Draw salary histogram - Required by project spec"""
        salaries = data.get('salary_list', [])

        if not salaries:
            self._draw_no_data(ax, "Salary Distribution")
            return

        # Convert to VND (multiply by scale factor) for display
        MONEY_SCALE = 10_000
        salaries_vnd = [s * MONEY_SCALE / 1_000_000 for s in salaries]  # In millions

        ax.hist(salaries_vnd, bins=15, color=self.COLORS['accent_blue'], 
               edgecolor='white', alpha=0.8)

        avg_vnd = data['avg_salary'] * MONEY_SCALE / 1_000_000
        ax.axvline(avg_vnd, color=self.COLORS['danger'], linestyle='--', linewidth=2,
                  label=f'Average: {avg_vnd:.1f}M VND')

        ax.set_xlabel('Salary (Million VND)', fontsize=9)
        ax.set_ylabel('Number of Employees', fontsize=9)
        ax.set_title('Salary Histogram', fontsize=11, fontweight='bold', pad=10)
        ax.legend(fontsize=8)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def _draw_top_employees(self, ax, data: dict):
        """Draw Top-N Employees by Salary bar chart - Required by project spec"""
        top_emps = data.get('top_employees', [])

        if not top_emps:
            self._draw_no_data(ax, "Top Employees by Salary")
            return

        MONEY_SCALE = 10_000
        names = [emp[0][:20] for emp in top_emps]  # Truncate long names
        salaries = [emp[1] * MONEY_SCALE / 1_000_000 for emp in top_emps]  # In millions

        y_pos = np.arange(len(names))
        colors = plt.cm.Greens(np.linspace(0.4, 0.8, len(names)))[::-1]

        ax.barh(y_pos, salaries, color=colors, edgecolor='white', height=0.6)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=8)
        ax.invert_yaxis()
        ax.set_xlabel('Salary (Million VND)', fontsize=9)
        ax.set_title('Top-N Employees by Salary', fontsize=11, fontweight='bold', pad=10)

        # Add value labels
        for i, v in enumerate(salaries):
            ax.text(v + 0.3, i, f'{v:.1f}M', va='center', fontsize=8)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def _draw_role_distribution(self, ax, data: dict):
        """Draw Role Distribution pie/donut chart - Required by project spec"""
        role_data = data.get('role_distribution', {})

        if not role_data:
            self._draw_no_data(ax, "Role Distribution")
            return

        # Sort and limit to top 8 roles
        sorted_roles = sorted(role_data.items(), key=lambda x: x[1], reverse=True)[:8]
        roles = [r[0] for r in sorted_roles]
        counts = [r[1] for r in sorted_roles]

        colors = plt.cm.Set3(np.linspace(0, 1, len(roles)))

        wedges, texts, autotexts = ax.pie(
            counts, labels=roles, autopct='%1.1f%%',
            colors=colors, startangle=90,
            wedgeprops=dict(width=0.6, edgecolor='white'),
            textprops={'fontsize': 8}
        )

        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_fontweight('bold')

        ax.set_title('Role Distribution', fontsize=11, fontweight='bold', pad=10)

        # Add center text
        total = sum(counts)
        ax.text(0, 0, f'{total}\nAssignments', ha='center', va='center',
               fontsize=11, fontweight='bold', color=self.COLORS['text_dark'])

    def _draw_no_data(self, ax, title: str):
        """Draw placeholder when no data available"""
        ax.text(0.5, 0.5, "No Data Available", ha='center', va='center',
               fontsize=12, color=self.COLORS['text_gray'])
        ax.set_title(title, fontsize=11, fontweight='bold', pad=10)
        ax.axis('off')

    def _format_salary(self, amount: float) -> str:
        """Format salary for display (convert from DB to VND millions)"""
        if amount == 0:
            return "0"
        MONEY_SCALE = 10_000
        vnd = amount * MONEY_SCALE
        if vnd >= 1_000_000:
            return f"{vnd/1_000_000:.1f}M"
        return f"{vnd:,.0f}"