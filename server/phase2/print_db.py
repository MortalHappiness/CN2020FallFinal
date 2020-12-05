import sqlite3

# ========================================

DB_NAME = "cn2020final.db"

# ========================================

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()


def print_table(name):
    print("="*40)
    print("Table:", name)
    print()
    cursor.execute(f"SELECT * FROM {name}")
    data = cursor.fetchall()
    for row in data:
        print(row)
    print()


print_table("accounts")
print_table("sessions")
print_table("messages")

conn.close()
