import sqlite3
import time

if __name__ == "__main__":
    conn = sqlite3.connect("novels.db")

    conn.close()