from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from SapiHelper import Sapi
import os
import re
import sys
import time
import sqlite3
import datetime
from multiprocessing import Pool

def getAllChapterLinks(link, browser):
    """
    Returns Dictionary containing information about the novel, Including the number of chapters and the chapter links
    {Name, Link, Chapters [{chapterLink}]}
    """
    browser.get(link)
    try:
        chapterContainer = browser.find_element_by_id('accordion')
        
        chapterElems = (chapterElem for chapterElem in chapterContainer.find_elements_by_tag_name('a'))
        # for chapterElem in chapterContainer.find_elements_by_tag_name('a'):
        #     chapterElems.append(chapterElem)

        chapterLinks = (chapterElem.get_attribute("href") for chapterElem in chapterElems)
        novelInfo = {
            "Name": link.split("/")[-1],
            "Link": link,
            "Chapters":[]
        }
        novelInfo["Chapters"] = ({"chapterLink":chapterLink} for chapterLink in chapterLinks if "collapse" not in chapterLink)
        # for chapterLink in chapterLinks:
        #     novelInfo["Chapters"].append({
        #         "chapterLink": chapterLink,
        #     })
    except:
        novelInfo = {}


    return novelInfo


def getChapterTexts(link, browser):
    print(f"Getting {link}...")
    browser.get(link)
    try:
        chapterLinkNumber = link.split('/')[-1]
        chapterText = browser.find_element_by_id("chapter-content").text.replace("Previous Chapter", "")
        return [chapterLinkNumber, chapterText]
    except:
        return False

def stringIsNum(x):
    try:
        int(x)
        return True
    except ValueError:
        return False

def checkIfAudio(chapter, novel):
    newPath = r"Novels\{}".format(novel["Name"].replace("?", ''))
    chapterNumber = chapter["chapterNumber"]
    if os.path.isfile(newPath + f"\{str(chapterNumber).zfill(5)}.mp3"):
        return None
    return chapter
    
def chaptersToAudio(chapter, novel):
    os.environ["LANG"] = "en_US.UTF-8"

    conn = sqlite3.connect("novels.db")
    curs = conn.cursor()

    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript':2})
    speaker = Sapi()
    speaker.set_rate(4)
    voices = speaker.get_voices()
    speaker.set_voice(voices[1]) 
    '''
     this line selects a voice from the array of voices avaiable on your system. 
     This value can be toyed with if you want to use a different voice. 
     I plan on adding the option to change the voice to the command arguments
     '''
    newPath = r"Novels\{}".format(novel["Name"].replace("?", ''))
    chapterNumber = chapter["chapterNumber"]
    if not os.path.isfile(newPath + f"\{str(chapterNumber).zfill(5)}.mp3"):
        try:
            browser = webdriver.Chrome(executable_path=r'Driver\chromedriver.exe', chrome_options=chrome_options)
            chapterLinkNumber, chapterText = getChapterTexts(chapter['chapterLink'], browser)
            browser.quit()
            if chapterText:
                chapterText = re.sub("\[A-Za-z0-9]",'', chapterText)
                speaker.create_recording(newPath + f"\{str(chapterNumber).zfill(5)}.mp3", re.sub(r'Chapter \w+', r'', chapterText))
                curs.execute("INSERT INTO chapters VALUES (?,?,?)", [novel["Link"], str(chapterNumber).zfill(5), chapterText])
                conn.commit()
                print(f"Chapter {chapter['chapterNumber']}/{len(novel['Chapters'])} finished")

        except:
            try:
                browser.close()
            except:
                pass
    else:
        conn.close()
            

def getNovelOnDemand(novelLink, conn, curs):
    os.environ["LANG"] = "en_US.UTF-8"
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript':2})
    browser = webdriver.Chrome(executable_path=r'Driver\chromedriver.exe', chrome_options=chrome_options)
    novel = getAllChapterLinks(novelLink, browser)
    newPath = r"Novels\{}".format(novel["Name"].replace("?", ''))
    if not os.path.exists(newPath):
        os.makedirs(newPath)
    nonPresentChapters = []

    curs.execute("UPDATE links SET lastUpdated=?, totalChapters=?, novelName=? WHERE link=?", 
    [datetime.datetime.now(),len(list(novel["Chapters"])), novel["Name"], novelLink])

    conn.commit()
    chapterCount = 0

    print(f"Skipping present chapters for {novel['Name']}")
    for chapter in novel["Chapters"]:
        chapterCount+=1
        chapter["chapterNumber"] = chapterCount
        newChapter = checkIfAudio(chapter, novel)
        if newChapter:
            nonPresentChapters.append((newChapter))
    
    print(f"System has {os.cpu_count()} cores... creating {os.cpu_count()} processes") if len(nonPresentChapters) >= os.cpu_count() else print (f"Creating {len(nonPresentChapters)} processes") 
    # This will prevent the behavior we currently see where a the latest books in the update are all only being handled by the last process
    with Pool(processes=os.cpu_count()) as p:
        p.starmap(chaptersToAudio, [(chapter, novel) for chapter in nonPresentChapters])
        



if __name__ == '__main__':
    start_time = time.time()
    newNovelLinks = sys.argv[1:]
    conn = sqlite3.connect("novels.db")
    curs = conn.cursor()
    oldNovelLinks = (row[0] for row in curs.execute("SELECT link FROM links"))

    
    for link in newNovelLinks:
        if link not in oldNovelLinks:
            curs.execute("INSERT INTO links VALUES (?, ?, ?, ?)", [link, datetime.datetime.now(), None, None])
            conn.commit()

        getNovelOnDemand(link, conn, curs)

    conn.close()



    print("--------%s seconds---------" % (time.time() -start_time))