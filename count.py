import sqlite3
import time

if __name__ == "__main__":
    conn = sqlite3.connect("novels.db")

    start_time = time.time()
    textlist = (" " + row[0].strip() for row in conn.execute(f"SELECT [text] FROM chapters WHERE novelLink LIKE '%against%'"))

    total = 1
    for text in textlist:
        for letter in text:
            if(letter == ' ' or letter == '\n' or letter == '\t'):
                total = total + 1

    print(total)
    print("--------%s seconds---------" % (time.time() -start_time))