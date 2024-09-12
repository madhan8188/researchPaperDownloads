from googleScholarsModule.getLinks import *
from utils import *
from config import config
import time
from datetime import datetime
from random import randint
import json


def main(q):
    chromePath = config["chromeDriver"]
    defaultdownDir = config["downloadFolder"]
    print(defaultdownDir)
    downloadDir = pathJoin(defaultdownDir,q.replace("/","").replace(" ","_"))
    CreateDirectory(downloadDir)
    print(downloadDir)
    print("download directory created successfully")
    driver = getSeleniumDriver(chromePath=chromePath,defaultDownloadDirectory=downloadDir)
    pageNUmber = 1
    sr = sementic(query=q,pageNumber=pageNUmber)
    if sr.status_code == 200:
        totalPages = sr.json()["totalPages"]
        data = sr.json()
        time.sleep(randint(80,120))
        while (pageNUmber < totalPages) and (sr.status_code == 200):
            print(pageNUmber)
            urls = [
                        results.get("openAccessInfo", {})
                            .get("location", {})
                            .get("url") 
                        for results in data.get("results", []) 
                        if results.get("openAccessInfo") 
                        and results["openAccessInfo"].get("location") 
                        and results["openAccessInfo"]["location"].get("url")
                    ]
            for url in urls:
                seleniumWayOfExtraction(driver,url)
                time.sleep(randint(30,60))
            time.sleep(randint(80,120))
            sr = sementic(query=q,pageNumber=pageNUmber)
            data = sr.json()
            
            print("length of data",len(data))
            pageNUmber += 1
    driver.quit()

        



if __name__ == "__main__":
    keys = [
        "Metal organic framework based color",
        "Structured surfactant systems",
        "polyphenol based color"
        ]
    for q in keys:
        main(q)
    #     lenth = 0
    #     start_time = datetime.now() 
    #     lenth = main(q=q)
    #     end_time = datetime.now() 
    #     time_difference = (end_time - start_time).total_seconds()
    #     mainList.append(
    #         {
    #     "title":q,
    #     "timeTaken":time_difference,
    #     "numberOfFiles":lenth
    #         }
    #     ) 
    # with open("output_keyWords.json", "w") as fout:
    #     json.dump(mainList, fout, indent=4)




