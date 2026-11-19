# Python Lab Works

University lab assignments in Python: from language basics to Pygame games and PostgreSQL applications.

## Contents

| Folder | Topic |
|---|---|
| `lab1` | Syntax, variables, data types, strings |
| `lab2` | Booleans, `if / elif / else`, loops |
| `lab3` | Functions, lambdas, classes, inheritance |
| `lab4` | Dates, generators, JSON, math |
| `lab5` | Regular expressions, receipt parser |
| `lab6` | Built-in functions, file handling, directory management |
| `lab7` | PostgreSQL phonebook with `psycopg2` (CRUD) |
| `lab8` | PostgreSQL functions and stored procedures |
| `lab9` | Pygame: Mickey clock, moving ball, music player |
| `Lab10` | Pygame games: Snake, Racer, Paint |
| `lab11` | Improved versions of the games: food with weights and timers, coins, more tools |
| `TSIS/TSIS1` | Phonebook app: PostgreSQL schema, procedures, contact groups, CSV import |
| `TSIS/TSIS2` | Paint app with multiple drawing tools |
| `TSIS/TSIS3` | Racer game with UI and saved leaderboard |
| `TSIS/TSIS4` | Snake game with players and scores stored in PostgreSQL |

## Requirements

```bash
pip install pygame psycopg2-binary
```

## Database setup

Passwords are not stored in the repository.

- **lab7, lab8:** set the `PGPASSWORD` environment variable before running.
  ```powershell
  $env:PGPASSWORD = "your_password"
  ```
- **TSIS1, TSIS4:** copy `database.ini.example` to `database.ini` in the same folder and fill in your password. `database.ini` is listed in `.gitignore`.
