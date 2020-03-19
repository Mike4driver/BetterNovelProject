import sqlite3
import time

if __name__ == "__main__":
    conn = sqlite3.connect("novels.db")

    # start_time = time.time()
    # textlist = (" " + row[0].strip() for row in conn.execute(f"SELECT [text] FROM chapters ORDER BY novelLink, chapterNumber"))
    text = []
    for row in conn.execute(f"SELECT [text] FROM chapters ORDER BY novelLink, chapterNumber"):
        text.append(row[0])
    
    index = 0
    for chapter in text:
        conn.execute("UPDATE chapters SET id=? WHERE [text] = ?", [index, chapter])
        index+=1
    # print("--------%s seconds---------" % (time.time() -start_time))

    conn.close()