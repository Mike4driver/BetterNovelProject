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
    
    # novelLinks = [link.replace("\n", "") for link in novelLinks]
    # os.environ["LANG"] = "en_US.UTF-8"
    # chrome_options = Options()
    # chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript':2})
    # # chrome_options.add_extension("./Driver/uBlock.crx")
    # browser = webdriver.Chrome(executable_path=r'Driver\chromedriver.exe', chrome_options=chrome_options)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executer:
        futureToNovel = {executer.submit( nr.getNovelOnDemand, novelLink, conn, curs):novelLink for novelLink in novelLinks}

    # for link in novelLinks:
    #     nr.getNovelOnDemand(link, conn, curs)

        # curs.execute("UPDATE links SET lastUpdated=? WHERE link=?", [datetime.datetime.now(), link])
    conn.commit()
    curs.close()    
    conn.close()

    # browser.quit()
    print("--------%s seconds---------" % (time.time() -start_time))

    
