import os

DB_CONFIG = {
    "host": "localhost",
    "dbname": "phonebook",
    "user": "postgres",
    "password": os.environ.get("PGPASSWORD", ""),  # set PGPASSWORD before running
    "port": 5432,
}
