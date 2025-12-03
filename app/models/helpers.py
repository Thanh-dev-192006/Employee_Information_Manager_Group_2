from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date, time
import re

MONEY_SCALE = 10_000  # DB amount * 10,000 = VNĐ hiển thị (để khớp seed 1500 => 15,000,000)

EMAIL_DOMAIN = "@161Corp.com"

PHONE_RE = re.compile(r"^0\d{9}$")

def ensure_email_domain(email: str) -> str:
    email = (email or "").strip()
    if not email:
        return email
    if "@" not in email:
        return email + EMAIL_DOMAIN
    return email

def parse_display_date(s: str) -> date:
    # DD/MM/YYYY
    return datetime.strptime(s.strip(), "%d/%m/%Y").date()

def format_display_date(d: date | None) -> str:
    return "" if not d else d.strftime("%d/%m/%Y")

def parse_display_time(s: str) -> time:
    # HH:MM or HH:MM:SS
    s = s.strip()
    fmt = "%H:%M:%S" if len(s.split(":")) == 3 else "%H:%M"
    return datetime.strptime(s, fmt).time()

def format_display_time(t: time | None) -> str:
    return "" if not t else t.strftime("%H:%M")

def to_vnd(db_amount: float | int | None) -> int:
    if db_amount is None:
        return 0
    return int(round(float(db_amount) * MONEY_SCALE))

def to_db_money(vnd_amount: int) -> float:
    return float(vnd_amount) / MONEY_SCALE

def format_currency_vnd(vnd: int) -> str:
    return f"{vnd:,} VNĐ"

def parse_currency_input(s: str) -> int:
    s = (s or "").upper().replace("VNĐ", "").replace(",", "").strip()
    if not s:
        return 0
    if not re.fullmatch(r"\d+", s):
        raise ValueError("Tiền phải là số nguyên (VD: 5000000)")
    return int(s)

def validate_phone(phone: str) -> None:
    if not PHONE_RE.match((phone or "").strip()):
        raise ValueError("SĐT phải 10 số và bắt đầu bằng 0 (VD: 0987654321)")

def validate_hire_date(hire_date: date) -> None:
    if hire_date > date.today():
        raise ValueError("Ngày vào làm phải <= hôm nay")

def validate_salary_vnd(vnd: int) -> None:
    if vnd < 5_000_000:
        raise ValueError("Lương phải >= 5,000,000 VNĐ")

@dataclass
class MonthYear:
    month: int
    year: int

    @property
    def display(self) -> str:
        return f"Tháng {self.month}/{self.year}"