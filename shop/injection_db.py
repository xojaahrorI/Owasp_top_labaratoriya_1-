"""
A05 - Injection: mahsulot qidiruv funksiyasi tezlik uchun alohida,
denormalizatsiya qilingan "search index" bazasidan foydalanadi degan
bahona bilan xom SQL orqali ishlaydi (ORM'dan chetga chiqilgan real holat).
Bu bazada, tasodifan, xodimlar jadvali ham bor - bu ilovaning boshqa
qismidan butunlay ajratilgan bo'lishi kerak edi, lekin bitta bazaga
joylashtirilgan (real loyihalarda tez-tez uchraydigan xato).
"""
import sqlite3
from django.conf import settings

from .flags import CHALLENGES

FLAG_A05 = CHALLENGES["a05"]["flag"]


def get_connection():
    return sqlite3.connect(settings.LAB_SEARCH_DB)


def ensure_seeded(products):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS search_products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            price REAL,
            category TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            full_name TEXT,
            department TEXT,
            note TEXT
        )
    """)
    cur.execute("SELECT COUNT(*) FROM search_products")
    if cur.fetchone()[0] == 0:
        rows = [
            (p.id, p.name, p.description[:200], float(p.price), p.category.name)
            for p in products
        ]
        cur.executemany(
            "INSERT INTO search_products (id, name, description, price, category) VALUES (?, ?, ?, ?, ?)",
            rows,
        )
    cur.execute("SELECT COUNT(*) FROM employees")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO employees (id, full_name, department, note) VALUES (?, ?, ?, ?)",
            [
                (1, "Dilnoza Karimova", "Customer Support", "Onboarded 2024-02-01"),
                (2, "Javlon Tursunov", "Warehouse", "Forklift certified"),
                (3, "System Ops", "Engineering", f"internal-flag={FLAG_A05}"),
                (4, "Malika Yusupova", "Marketing", "Runs social campaigns"),
            ],
        )
    conn.commit()
    conn.close()


def run_vulnerable_search(user_query: str):
    """
    ATAYLAB ZAIF: kirim to'g'ridan-to'g'ri SQL matniga qo'shiladi -
    klassik SQL Injection.
    """
    conn = get_connection()
    cur = conn.cursor()
    sql = (
        "SELECT name, description, price, category FROM search_products "
        f"WHERE name LIKE '%{user_query}%' OR description LIKE '%{user_query}%'"
    )
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        error = None
    except sqlite3.Error as e:
        rows = []
        error = str(e)
    conn.close()
    return rows, error
