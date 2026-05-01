import psycopg2

from connect import get_connection


def create_contacts_table():
    query = """
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        phone VARCHAR(50) NOT NULL
    )
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)


def load_sql_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def setup_database():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(load_sql_file("functions.sql"))
            cur.execute(load_sql_file("procedures.sql"))


def upsert_contact(first_name, last_name, phone):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CALL upsert_contact(%s, %s, %s)",
                (first_name, last_name, phone),
            )


def insert_many_contacts(first_names, last_names, phones):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CALL insert_many_contacts(%s, %s, %s, %s)",
                (first_names, last_names, phones, []),
            )


def search_contacts(pattern):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts_by_pattern(%s)", (pattern,))
            return cur.fetchall()


def get_paginated_contacts(limit, offset):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
            return cur.fetchall()


def delete_contact(value):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact(%s)", (value,))


def main():
    create_contacts_table()
    setup_database()

    upsert_contact("Ali", "Nurzhan", "+77011234567")
    upsert_contact("Aruzhan", "Saparova", "+77017654321")

    insert_many_contacts(
        ["Dias", "Malika", "Invalid"],
        ["Serik", "Aman", "User"],
        ["+77015550000", "87025550101", "bad-phone"],
    )

    print("Search results:")
    for row in search_contacts("Ali"):
        print(row)

    print("Paginated results:")
    for row in get_paginated_contacts(5, 0):
        print(row)

    delete_contact("Aruzhan Saparova")


if __name__ == "__main__":
    main()
