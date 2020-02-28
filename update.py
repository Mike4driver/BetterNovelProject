from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import writeAllToJson as nr
import time
import sqlite3
import datetime
import concurrent.futures

if __name__=="__main__":
    start_time = time.time()
    conn = sqlite3.connect("novels.db", check_same_thread=False)
    curs = conn.cursor()
    novelLinks = [row[0] for row in curs.execute("SELECT link from links")]

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executer:
        futureToNovel = {executer.submit( nr.getNovelOnDemand, novelLink, conn, curs):novelLink for novelLink in novelLinks}

    conn.commit()
    curs.close()    
    conn.close()

    print("--------%s seconds---------" % (time.time() -start_time))

    
