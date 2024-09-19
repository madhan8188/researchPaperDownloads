from googleScholarsModule.getLinks import *
from utils import *
from config import config
import time
from datetime import datetime
from random import randint
import json


def main(q):
    numberOfPages = "2"
    chromePath = config["chromeDriver"]
    defaultdownDir = config["downloadFolder"]
    apikey = config["API-KEY"]
    queryQ = '" AND "'.join(q.split(" "))
    queryQ = '"'+queryQ+'"'
    print(defaultdownDir)
    downloadDir = pathJoin(defaultdownDir,q.replace("/","").replace(" ","_")+"/t")
    CreateDirectory(downloadDir)
    print(downloadDir)
    print("download directory created successfully")
    results = []
    count = 1
    driver = getSeleniumDriver(chromePath=chromePath,defaultDownloadDirectory=downloadDir)
    lastFile = None
    nextUrl = None
    while count <= int(numberOfPages):
        print(f"Started processing page number , {count}")
        # responseFromScholar = requestGoogleScholar(q = q,start=len(results))
        # mainUrl = getRequestURL(q=q,start=(count-1)*10)
        driver.get("https://scholar.google.com/scholar")

        driver.find_element(By.XPATH,"""//*[@id="gs_hdr_tsi"]""").send_keys("polyphenol based color")

        time.sleep(10)

        driver.find_element(By.XPATH,"""//*[@id="gs_hdr_tsb"]/span""").click()
        # seleniumWayOfExtraction(driver=driver,pdf_url=mainUrl)
        soup = getSoupObject(driver.page_source)
        time.sleep(15)
        # # reqUrl = getRequestURL(q=q,start=len(results))
        # soup = getSoupObject(responseFromScholar)
        print(soup)
        resultFromEachPage = [forEachSoup(x) for x in soup.find("div",{"id":"gs_res_ccl_mid"}).find_all("div",{"class":"gs_r gs_or gs_scl"})]
        for result in resultFromEachPage:
            title = result["title"]
            crr = getTitleSuggestions(title=title)
            if crr.status_code == 200:
                papers = crr.json()['message']['items']
                for paper in papers:
                    print("Now processing",papers.index(paper))
                    links = paper.get("link",[]) or [{"URL":paper["resource"]["primary"]["URL"]}]
                    for url in links:
                        paperurl = url.get("URL","")
                        if ("api.elsevier.com" not in paperurl.lower()) and (".wiley.com" not in paperurl.lower()) and (paperurl != ""):
                            print(paperurl)
                            try:
                                paperResponse = requests.get(paperurl)
                                print(paperResponse)
                                time.sleep(15)
                                if paperResponse.status_code == 200 and "/pdf" in paperResponse.headers.get("Content-Type",""):
                                    fileName = pdfFileName(paperResponse.headers.get("content-disposition",""))
                                    if fileName:
                                        with open(pathJoin(downloadDir,fileName),"wb") as pdf:pdf.write(paperResponse.content)
                                        time.sleep(10)
                                if paperResponse.status_code != 200:
                                    seleniumWayOfExtraction(driver = driver, pdf_url=paperurl)
                                    time.sleep(15)
                            except requests.ConnectionError:
                                seleniumWayOfExtraction(driver = driver, pdf_url=paperurl)
                                time.sleep(30)  
                            if CheckFile(downloadDir):
                                break
                            else:
                                try:
                                    scholarResponse = requestGoogleScholar(q=paperurl,start=0)
                                    scholarSoup = getSoupObject(scholarResponse.content)
                                    downloadableLink = [forEachSoup(x) for x in scholarSoup.find("div",{"id":"gs_res_ccl_mid"}).find_all("div",{"class":"gs_r gs_or gs_scl"})][0]["downloadableLink"]
                                    if downloadableLink:
                                        paperResponse2 = requests.get(downloadableLink)
                                        if paperResponse2.status_code == 200 and "/pdf" in paperResponse2.headers.get("Content-Type",""):
                                            fileName = pdfFileName(paperResponse.headers.get("content-disposition",""))
                                            if fileName:
                                                with open(pathJoin(downloadDir,fileName),"wb") as pdf:pdf.write(paperResponse.content)
                                                time.sleep(10)
                                    time.sleep(60)

                                    if CheckFile(downloadDir):
                                        break
                                except Exception as e:
                                    print(e)
                        else:
                            print(url)
                            time.sleep(50)
        count +=1



main(q="polyphenol based color")