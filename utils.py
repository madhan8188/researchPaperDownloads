from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from glob import glob
import shutil


def ClickById(driver,id):
    WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.ID, id))).click()
    return driver


def ClickByclassName(driver):
    WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.CLASS_NAME, "ViewPDF"))).click()
    return driver

def ClickByxpath(driver):
    WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.XPATH, '''//*[@id="gs_res_ccl_mid"]/div/div[1]/div/div/a[1]'''))).click()
    return driver


def CheckFile(folder_path):
    files = os.listdir(folder_path)
    print(files)
    if len(files) == 1:
        shutil.move(os.path.join(folder_path,files[0]) ,os.path.join(folder_path.replace("/t",""),os.path.basename(files[0])))
        return True
    else:
        return False


def CreateDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    except Exception as e:return False
    
def pathJoin(dir1,dir2):
    return os.path.join(os.getcwd(),dir1,dir2)





def getSeleniumDriver(chromePath,defaultDownloadDirectory):
    try:
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless=new")
        options.add_experimental_option('prefs', {
            "download.default_directory": defaultDownloadDirectory,
            "download.prompt_for_download":False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True})
        try:
            service = Service(chromePath)
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
        driver.maximize_window()
        return driver
    except Exception as e:
        print(e)



def latest_download_file(downloadDir):
    try:
        list_of_files = glob(f'{downloadDir}/*.pdf') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
    except Exception as e:
        print(e)
        return None
    
def seleniumWayOfExtraction(driver,pdf_url):
    driver.get(pdf_url)
    # time.sleep(5)

def makeZipFolder(dirName):
    shutil.make_archive(dirName,"zip",dirName)
    return True