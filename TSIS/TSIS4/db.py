import psycopg2
from config import load_config

def get_connection():
    config = load_config()
    return psycopg2.connect(**config)

def init_db():
    commands = [
        """
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            score INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT NOW()
        )
        """
    ]
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                for cmd in commands:
                    cur.execute(cmd)
            conn.commit()
    except Exception as e:
        print(f"Database Init Error: {e}")

def save_score(username, score, level):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Находим или создаем игрока
                cur.execute("INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING RETURNING id", (username,))
                res = cur.fetchone()
                if res:
                    player_id = res[0]
                else:
                    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
                    player_id = cur.fetchone()[0]
                
                # Сохраняем сессию
                cur.execute("INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
                            (player_id, score, level))
            conn.commit()
    except Exception as e:
        print(f"Error saving score: {e}")

def get_top_10():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.username, s.score, s.level_reached, to_char(s.played_at, 'YYYY-MM-DD HH24:MI')
                    FROM game_sessions s
                    JOIN players p ON s.player_id = p.id
                    ORDER BY s.score DESC
                    LIMIT 10
                """)
                return cur.fetchall()
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        return []

def get_personal_best(username):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT MAX(s.score) FROM game_sessions s
                    JOIN players p ON s.player_id = p.id
                    WHERE p.username = %s
                """, (username,))
                res = cur.fetchone()
                return res[0] if res[0] is not None else 0
    except Exception as e:
        return 0