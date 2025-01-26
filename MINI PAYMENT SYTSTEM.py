import sqlite3
from sqlite3 import Error
from datetime import datetime

def create_connestion(database):
    conn = None
    try:
        conn = sqlite3.connect(database)
        return conn
    except Error as e:
        print(e)
    return conn


def create_tables(conn):
    user_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        balance REAL NOT NULL DEFAULT 0
    );
    """
    transaction_table_query = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """
    try:
        conn.execute(user_table_query)
        conn.execute(transaction_table_query)
    except Error as e:
        print(f"Jadval yaratishda xatolik: {e}")

def add_user(conn, user):
    query = """INSERT INTO users(username, balance) VALUES (?, ?)"""
    conn.execute(query, user)
    conn.commit()

def update_balance(conn, user_id, amount, transaction_type):
    query = """SELECT balance FROM users WHERE id = ?"""
    current_balance = conn.execute(query, (user_id,)).fetchone()

    if not current_balance:
        print(f"Foydalanuvchi ID {user_id} topilmadi!")
        return

    current_balance = current_balance[0]

    if current_balance + amount < 0:
        print("Hisobingizda mablag' yetarli emas.")
        return

    update_query = """UPDATE users SET balance = balance + ? WHERE id = ?"""
    conn.execute(update_query, (amount, user_id))

    transaction_query = """INSERT INTO transactions(user_id, type, amount, timestamp)
                           VALUES (?, ?, ?, ?)"""
    conn.execute(transaction_query, (user_id, transaction_type, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()


def transfer(conn, sender_id, receiver_id, amount):
    if sender_id == receiver_id:
        print("O'zingizga pul o'tkazolmaysiz.")
        return

    query = """SELECT balance FROM users WHERE id = ?"""
    sender_balance = conn.execute(query, (sender_id,)).fetchone()

    if not sender_balance or sender_balance[0] < amount:
        print("Jo'natuvchining hisobida mablag' yetarli emas.")
        return

    update_balance(conn, sender_id, -amount, "Transfer Sent")
    update_balance(conn, receiver_id, amount, "Transfer Received")
    print("Tranzaksiya muvaffaqiyatli amalga oshirildi.")

def display_users(conn):
    query = """SELECT * FROM users"""
    users = conn.execute(query).fetchall()
    for user in users:
        print(user)
def display_transactions(conn):
    query = """SELECT * FROM transactions"""
    transactions = conn.execute(query).fetchall()
    for transaction in transactions:
        print(transaction)
def main():
    database = "payment_system.db"
    conn = create_connestion(database)
    create_tables(conn)

    while True:
        print("\nMini Payment System Menu")
        print("1. Foydalanuvchi qo'shish")
        print("2. Hisobga depozit qilish")
        print("3. Hisobdan mablag' yechish")
        print("4. Pul o'tkazish")
        print("5. Foydalanuvchilar ro'yxati")
        print("6. Tranzaksiyalar ro'yxati")
        print("7. Chiqish")
        choice = int(input("Tanlovingizni kiriting: "))
        if choice == 1:
            username = input("Foydalanuvchi ismini kiriting: ")
            balance = float(input("Boshlang'ich balansni kiriting: "))
            user = (username, balance)
            add_user(conn, user)
        elif choice == 2:
            user_id = int(input("Foydalanuvchi ID raqamini kiriting: "))
            amount = float(input("Depozit miqdorini kiriting: "))
            update_balance(conn, user_id, amount, "Deposit")
        elif choice == 3:
            user_id = int(input("Foydalanuvchi ID raqamini kiriting: "))
            amount = float(input("Yechib olish miqdorini kiriting: "))
            update_balance(conn, user_id, -amount, "Withdrawal")
        elif choice == 4:
            sender_id = int(input("Jo'natuvchi foydalanuvchi ID raqamini kiriting: "))
            receiver_id = int(input("Qabul qiluvchi foydalanuvchi ID raqamini kiriting: "))
            amount = float(input("O'tkazma miqdorini kiriting: "))
            transfer(conn, sender_id, receiver_id, amount)
        elif choice == 5:
            display_users(conn)
        elif choice == 6:
            display_transactions(conn)
        elif choice == 7:
            break
        else:
            print("Noto'g'ri tanlov. Qaytadan urinib ko'ring.")
    conn.close()
if __name__ == "__main__":
    main()

