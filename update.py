from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import writeAllToJson as nr
import time
import sqlite3
import datetime

if __name__=="__main__":
    conn = sqlite3.connect("novels.db")
    curs = conn.cursor()
    novelLinks = [row[0] for row in curs.execute("SELECT link from links")]
    
    # novelLinks = [link.replace("\n", "") for link in novelLinks]
    os.environ["LANG"] = "en_US.UTF-8"
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript':2})
    # chrome_options.add_extension("./Driver/uBlock.crx")
    browser = webdriver.Chrome(executable_path=r'Driver\chromedriver.exe', chrome_options=chrome_options)

    for link in novelLinks:
        curs.execute("UPDATE links SET lastUpdated=? WHERE link=?", [datetime.datetime.now(), link])
        nr.getNovelOnDemand(link, browser, conn, curs)

    conn.commit()
    curs.close()    
    conn.close()

    browser.quit()


    
