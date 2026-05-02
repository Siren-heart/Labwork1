import psycopg2
from config import load_config

def connect():
    try:
        # Читаем настройки
        config = load_config()
        print('Connecting to the PostgreSQL database...')
        
        # Подключаемся к серверу
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL database server!')
            
            # Проверяем версию, чтобы точно убедиться, что всё работает
            with conn.cursor() as cur:
                cur.execute('SELECT version()')
                db_version = cur.fetchone()
                print(f'PostgreSQL database version: {db_version[0]}')
                
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error: {error}")

if __name__ == '__main__':
    connect()