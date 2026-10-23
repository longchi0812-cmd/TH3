import sqlite3
import os
import sys

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products.db")

def show_database():
    if not os.path.exists(DB_PATH):
        print(f"[!] Không tìm thấy file database tại: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print(" DANH SÁCH BẢNG TRONG CƠ SỞ DỮ LIỆU (products.db)")
    print("=" * 80)

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        if table_name.startswith("sqlite_"):
            continue
        print(f"\n>> Bảng: [{table_name}]")
        
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cursor.fetchall()]
        print("  Cột:", " | ".join(columns))
        print("  " + "-" * 75)

        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        if not rows:
            print("  (Bảng chưa có bản ghi nào)")
        else:
            for row in rows:
                print(f"  ID: {row[0]} | Tên: {row[1]} | Giá: {float(row[3]):,.0f} đ | Kho: {row[4]}")
                print(f"       Mô tả: {row[2]}")
                print(f"       Ngày tạo: {row[5]} | Ngày cập nhật: {row[6]}")
                print("  " + "." * 70)

    conn.close()
    print("\n" + "=" * 80)

if __name__ == "__main__":
    show_database()
