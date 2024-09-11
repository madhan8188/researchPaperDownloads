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
    downloadDir = pathJoin(defaultdownDir,q.replace("/","").replace(" ","_"))
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
        responseFromScholar = requestGoogleScholar(q = q,start=len(results))
        reqUrl = getRequestURL(q=q,start=len(results))
        soup = getSoupObject(responseFromScholar.content)
        resultFromEachPage = [forEachSoup(x) for x in soup.find("div",{"id":"gs_res_ccl_mid"}).find_all("div",{"class":"gs_r gs_or gs_scl"})]
        lastFile = None
        if not nextUrl and count%2 != 0:
            list_of_dois,nextUrl = get_list_of_dois(API_KEY=apikey,q=queryQ,nextUrl=nextUrl)

        for result in resultFromEachPage:
            index = resultFromEachPage.index(result)
            if index%2 == 1:
                try:
                    print("trying to load page based on scopus")
                    doi = list_of_dois[index]
                    print(doi)
                    doiUrl = getRequestURL(q=doi,start=0)
                    print(doiUrl)
                    seleniumWayOfExtraction(driver=driver,pdf_url=doiUrl)
                    print(1)
                    soup_doi = getSoupObject(driver.page_source)
                    print(2)
                    tag = [forEachSoup(x) for x in soup_doi.find("div",{"id":"gs_res_ccl_mid"}).find_all("div",{"class":"gs_r gs_or gs_scl"})][0].get("linkTag")
                    print(tag)
                    ClickById(driver=driver,id = tag)
                    ClickByclassName(driver=driver)
                except Exception as e:
                    print(e)

            try:
                seleniumWayOfExtraction(driver,result["downloadableLink"])
                time.sleep(5)
                recentfile = latest_download_file(downloadDir)
                if lastFile == recentfile:
                    driver.get(reqUrl)
                    ClickById(driver=driver,id = result["linkTag"]) 
                    time.sleep(5)
                    recentfile = latest_download_file(downloadDir)
                    if lastFile == recentfile:
                        schiHubLink = schiHub(result["downloadableLink"])
                        if not schiHubLink:
                            print("schiHubLink is not available, going for another approach")
                            schiHubLink = schiHub(result["title"])
                            print("schiLink=====>",schiHubLink)
                            if not schiHubLink:
                                doi = getdoi(result["title"])
                                if doi:
                                    schiHubLink1 = "https://sci-hub.se/"+doi
                                    schiHubLink = schiHub(link=schiHubLink1)
                        zeroCount = 0
                        while schiHubLink is not None and "zero.sci-hub" in schiHubLink.lower() and zeroCount<3:
                            time.sleep(randint(5,10))
                            schiHubLink = schiHub(result["downloadableLink"])
                            zeroCount +=1
                        if schiHubLink:
                            print("===================")
                            print(result["downloadableLink"])
                            print(schiHubLink)
                            print("====================")
                            seleniumWayOfExtraction(driver=driver,pdf_url=schiHubLink)
                            time.sleep(30)
                            recentfile = latest_download_file(downloadDir)
                            if recentfile:
                                if lastFile == recentfile:
                                    result["isDownloadable"] = False
                                    result["fileName"] = None
                                    result["link2"] = None
                                else:
                                    result["link2"] = driver.current_url
                                    result["isDownloadable"] = True
                                    result["fileName"] = recentfile
                                    lastFile = recentfile 
                    else:
                        result["link2"] = driver.current_url
                        result["isDownloadable"] = True
                        result["fileName"] = recentfile
                        lastFile = recentfile  
                else:
                    result["isDownloadable"] = True
                    result["fileName"] = recentfile
                    result["link2"] = driver.current_url
                    lastFile = recentfile 
                results.append(result)
                time.sleep(5)
            except Exception as e:
                print(e)
        count = count+1

        time.sleep(randint(5,10))
    driver.quit()
    with open(f"{q.replace('/','').replace(' ','_')}.json", "w") as fout:
        json.dump(results, fout, indent=4)
    return len(glob(defaultdownDir+"/*.pdf"))

        



if __name__ == "__main__":
    # mainList = [
    #     {
    #     "title":"Metal organic framework based color pdf",
    #     "timeTaken":1014,
    #     "numberOfFiles":33
    #     }
    # ]
    # # parser = argparse.ArgumentParser()
    # # parser.add_argument('-f', '--keyword')
    # # # parser.add_argument('-g', '--numberOfPDF')
    # # args = parser.parse_args()
    # # q= args.keyword
    # # # numberOfPdf = args.numberOfPDF
    # # print(q)
    # # print(numberOfPdf)
    keys = [
        "Metal organic framework based color",
        # "Structured surfactant systems pdf",
        # "Hydrocolloids and their properties in foods and dairy pdf",
        # "Dairy technology pdf",
        # "Dairy science pdf",
        # "Tensile strength of hair and fibers pdf",
        # "Cyclic voltammetry pdf",
        # "Mechanism of formation and recurrence of dandruff pdf",
        # "chemical properties of hair pdf",
        # "Mechanism of bleaching pdf"
        # "hair"
        ]
    # for q in keys:
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




