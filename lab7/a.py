import psycopg2

# --- НАСТРОЙКИ ---
DB_PARAMS = {
    "dbname": "lab_db",
    "user": "postgres",
    "password": "Kmb010206!", # ВПИШИ СВОЙ ПАРОЛЬ
    "host": "127.0.0.1",
    "port": "5432"
}

def get_connection():
    conn = psycopg2.connect(**DB_PARAMS)
    conn.set_client_encoding('UTF8')
    return conn

def create_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    phone VARCHAR(20) UNIQUE
                )
            """)
            conn.commit()

def add_contact(f_name, l_name, phone):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO phonebook (first_name, last_name, phone) VALUES (%s, %s, %s)", 
                            (f_name, l_name, phone))
                conn.commit()
                print("Успешно добавлено!")
    except Exception as e:
        print(f"Ошибка: {e}")

def update_phone(f_name, new_phone):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE phonebook SET phone = %s WHERE first_name = %s", (new_phone, f_name))
            conn.commit()
            print("Номер обновлен!")

def delete_contact(f_name):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM phonebook WHERE first_name = %s", (f_name,))
            conn.commit()
            print("Контакт удален!")

def query_contacts(pattern):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM phonebook WHERE first_name ILIKE %s OR last_name ILIKE %s", 
                        (f'%{pattern}%', f'%{pattern}%'))
            for row in cur.fetchall():
                print(row)

if __name__ == "__main__":
    create_table()
    print("\n--- PhoneBook CLI ---")
    print("1. Добавить контакт")
    print("2. Найти контакт")
    print("3. Обновить номер")
    print("4. Удалить контакт")
    
    choice = input("\nВыбери действие (1-4): ")
    
    if choice == '1':
        fn = input("Имя: ")
        ln = input("Фамилия: ")
        ph = input("Телефон: ")
        add_contact(fn, ln, ph)
    elif choice == '2':
        p = input("Введите имя или фамилию для поиска: ")
        query_contacts(p)
    elif choice == '3':
        fn = input("Имя контакта для смены номера: ")
        ph = input("Новый номер: ")
        update_phone(fn, ph)
    elif choice == '4':
        fn = input("Имя контакта для удаления: ")
        delete_contact(fn)