import sqlite3

if __name__ == "__main__":
    conn = sqlite3.connect("novels.db")
    curs = conn.cursor()

    text = ''
    for row in conn.execute(f"SELECT [text] FROM chapters WHERE novelLink LIKE '%asura%' ORDER BY chapterNumber"):
        text += " " + row[0].strip()

    print(len(text.split(" ")))